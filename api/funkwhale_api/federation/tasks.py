import datetime
import json
import logging
import os
from urllib.parse import urlparse

import requests
from celery import chain, group
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.db.models import F, Q
from django.db.models.deletion import Collector
from django.urls import reverse
from django.utils import timezone
from dynamic_preferences.registries import global_preferences_registry
from requests.exceptions import RequestException

from funkwhale_api.audio import models as audio_models
from funkwhale_api.common import models as common_models
from funkwhale_api.common import preferences, session
from funkwhale_api.common import utils as common_utils
from funkwhale_api.history import models as history_models
from funkwhale_api.history import tasks as history_tasks
from funkwhale_api.moderation import mrf
from funkwhale_api.music import models as music_models
from funkwhale_api.playlists import models as playlists_models
from funkwhale_api.taskapp import celery

from . import (
    activity,
    actors,
    exceptions,
    jsonld,
    keys,
    models,
    routes,
    serializers,
    signing,
    utils,
    webfinger,
)

logger = logging.getLogger(__name__)


@celery.app.task(name="federation.clean_music_cache")
def clean_music_cache():
    preferences = global_preferences_registry.manager()
    delay = preferences["federation__music_cache_duration"]
    if delay < 1:
        return  # cache clearing disabled
    limit = timezone.now() - datetime.timedelta(minutes=delay)

    candidates = (
        music_models.Upload.objects.filter(
            Q(audio_file__isnull=False)
            & (Q(accessed_date__lt=limit) | Q(accessed_date=None)),
            # library__actor__user=None,
        )
        .local(False)
        .exclude(audio_file="")
        .filter(Q(source__startswith="http://") | Q(source__startswith="https://"))
        .only("audio_file", "id")
        .order_by("id")
    )
    for upload in candidates:
        upload.audio_file.delete()

    # we also delete orphaned files, if any
    storage = models.LibraryTrack._meta.get_field("audio_file").storage
    files = get_files(storage, "federation_cache/tracks")
    existing = music_models.Upload.objects.filter(audio_file__in=files)
    missing = set(files) - set(existing.values_list("audio_file", flat=True))
    for m in missing:
        storage.delete(m)


def get_files(storage, *parts):
    """
    This is a recursive function that return all files available
    in a given directory using django's storage.
    """
    if not parts:
        raise ValueError("Missing path")
    try:
        dirs, files = storage.listdir(os.path.join(*parts))
    except FileNotFoundError:
        return []
    for dir in dirs:
        files += get_files(storage, *(list(parts) + [dir]))
    return [os.path.join(parts[-1], path) for path in files]


@celery.app.task(name="federation.dispatch_inbox")
@celery.require_instance(models.Activity.objects.select_related(), "activity")
def dispatch_inbox(activity, call_handlers=True):
    """
    Given an activity instance, triggers our internal delivery logic (follow
    creation, etc.)
    """

    routes.inbox.dispatch(
        activity.payload,
        context={
            "activity": activity,
            "actor": activity.actor,
            "inbox_items": activity.inbox_items.filter(is_read=False).order_by("id"),
        },
        call_handlers=call_handlers,
    )


@celery.app.task(name="federation.dispatch_outbox")
@celery.require_instance(models.Activity.objects.select_related(), "activity")
def dispatch_outbox(activity):
    """
    Deliver a local activity to its recipients, both locally and remotely
    """
    inbox_items = activity.inbox_items.filter(is_read=False).select_related()

    if inbox_items.exists():
        call_handlers = activity.type in ["Follow"]
        dispatch_inbox.delay(activity_id=activity.pk, call_handlers=call_handlers)

    if not preferences.get("federation__enabled"):
        # federation is disabled, we only deliver to local recipients
        return

    deliveries = activity.deliveries.filter(is_delivered=False)

    for id in deliveries.values_list("pk", flat=True):
        deliver_to_remote.delay(delivery_id=id)


@celery.app.task(
    name="federation.deliver_to_remote_inbox",
    autoretry_for=[RequestException],
    retry_backoff=30,
    max_retries=5,
)
@celery.require_instance(
    models.Delivery.objects.filter(is_delivered=False).select_related(
        "activity__actor"
    ),
    "delivery",
)
def deliver_to_remote(delivery):
    if not preferences.get("federation__enabled"):
        # federation is disabled, we only deliver to local recipients
        return

    # we check the domain is still reachable before attempting delivery
    if (
        models.Domain.objects.get(name=urlparse(delivery.inbox_url).netloc).reachable
        is False
    ):
        delivery.last_attempt_date = timezone.now()
        delivery.attempts = F("attempts") + 1
        delivery.save(update_fields=["last_attempt_date", "attempts"])
        logger.info(
            f"Skipping delivery to {delivery.inbox_url} as its domain is unreachable",
        )
        return

    actor = delivery.activity.actor
    logger.info("Preparing activity delivery to %s", delivery.inbox_url)
    auth = signing.get_auth(actor.private_key, actor.private_key_id)
    try:
        response = session.get_session().post(
            auth=auth,
            json=delivery.activity.payload,
            url=delivery.inbox_url,
            headers={"Content-Type": "application/activity+json"},
        )
        logger.debug("Remote answered with %s", response.status_code)
        response.raise_for_status()
    except Exception:
        delivery.last_attempt_date = timezone.now()
        delivery.attempts = F("attempts") + 1
        delivery.save(update_fields=["last_attempt_date", "attempts"])
        raise
    else:
        delivery.last_attempt_date = timezone.now()
        delivery.attempts = F("attempts") + 1
        delivery.is_delivered = True
        delivery.save(update_fields=["last_attempt_date", "attempts", "is_delivered"])


def fetch_nodeinfo(domain_name):
    s = session.get_session()
    wellknown_url = f"https://{domain_name}/.well-known/nodeinfo"
    response = s.get(url=wellknown_url)
    response.raise_for_status()
    serializer = serializers.NodeInfoSerializer(data=response.json())
    serializer.is_valid(raise_exception=True)
    nodeinfo_url = None
    for link in serializer.validated_data["links"]:
        if link["rel"] == "https://docs.funkwhale.audio/swagger/schema.yml":
            nodeinfo_url = link["href"]
            break
    if not nodeinfo_url:
        logger.info("Not supported nodeinfo schema")
    response = s.get(url=nodeinfo_url)
    response.raise_for_status()
    return response.json()


@celery.app.task(name="federation.update_domain_nodeinfo")
@celery.require_instance(
    models.Domain.objects.external(), "domain", id_kwarg_name="domain_name"
)
def update_domain_nodeinfo(domain):
    now = timezone.now()
    try:
        nodeinfo = {"status": "ok", "payload": fetch_nodeinfo(domain.name)}
    except (
        requests.RequestException,
        serializers.serializers.ValidationError,
        ValueError,
    ) as e:
        nodeinfo = {"status": "error", "error": str(e)}

    service_actor_id = common_utils.recursive_getattr(
        nodeinfo, "payload.metadata.actorId", permissive=True
    )
    try:
        domain.service_actor = (
            utils.retrieve_ap_object(
                service_actor_id,
                actor=None,
                queryset=models.Actor,
                serializer_class=serializers.ActorSerializer,
            )
            if service_actor_id
            else None
        )
    except (
        serializers.serializers.ValidationError,
        RequestException,
        exceptions.BlockedActorOrDomain,
    ) as e:
        logger.warning(
            "Cannot fetch system actor for domain %s: %s", domain.name, str(e)
        )
    domain.nodeinfo_fetch_date = now
    domain.nodeinfo = nodeinfo
    if nodeinfo.get("payload", {}).get("software", {}).get("name", "") == "funkwhale":
        domain.is_funkwhale_instance = True
    return domain.save(
        update_fields=[
            "nodeinfo",
            "nodeinfo_fetch_date",
            "service_actor",
            "is_funkwhale_instance",
        ]
    )


@celery.app.task(name="federation.refresh_nodeinfo_known_nodes")
def refresh_nodeinfo_known_nodes():
    """
    Trigger a node info refresh on all nodes that weren't refreshed since
    settings.NODEINFO_REFRESH_DELAY
    """
    limit = timezone.now() - datetime.timedelta(seconds=settings.NODEINFO_REFRESH_DELAY)
    candidates = (
        models.Domain.objects.external()
        .exclude(nodeinfo_fetch_date__gte=limit)
        .filter(nodeinfo__software__name="Funkwhale")
    )
    names = candidates.values_list("name", flat=True)
    logger.info("Launching periodic nodeinfo refresh on %s domains", len(names))
    for domain_name in names:
        update_domain_nodeinfo.delay(domain_name=domain_name)


def delete_qs(qs):
    label = qs.model._meta.label
    result = qs.delete()
    related = sum(result[1].values())

    logger.info(
        "Purged %s %s objects (and %s related entities)", result[0], label, related
    )


def handle_purge_actors(ids, only=[]):
    """
    Empty only means we purge everything
    Otherwise, we purge only the requested bits: media
    """
    # purge follows (received emitted)
    if not only:
        delete_qs(models.LibraryFollow.objects.filter(target__actor_id__in=ids))
        delete_qs(models.Follow.objects.filter(actor_id__in=ids))

    # purge audio content
    if not only or "media" in only:
        delete_qs(common_models.Attachment.objects.filter(actor__in=ids))
        delete_qs(models.LibraryFollow.objects.filter(actor_id__in=ids))
        delete_qs(models.Follow.objects.filter(target_id__in=ids))
        delete_qs(audio_models.Channel.objects.filter(attributed_to__in=ids))
        delete_qs(audio_models.Channel.objects.filter(actor__in=ids))
        delete_qs(music_models.Upload.objects.filter(library__actor_id__in=ids))
        delete_qs(music_models.Library.objects.filter(actor_id__in=ids))

    # purge remaining activities / deliveries
    if not only:
        delete_qs(models.InboxItem.objects.filter(actor_id__in=ids))
        delete_qs(models.Activity.objects.filter(actor_id__in=ids))


@celery.app.task(name="federation.purge_actors")
def purge_actors(ids=[], domains=[], only=[]):
    actors = models.Actor.objects.filter(
        Q(id__in=ids) | Q(domain_id__in=domains)
    ).order_by("id")
    found_ids = list(actors.values_list("id", flat=True))
    logger.info("Starting purging %s accounts", len(found_ids))
    handle_purge_actors(ids=found_ids, only=only)


@celery.app.task(name="federation.rotate_actor_key")
@celery.require_instance(models.Actor.objects.local(), "actor")
def rotate_actor_key(actor):
    pair = keys.get_key_pair()
    actor.private_key = pair[0].decode()
    actor.public_key = pair[1].decode()
    actor.save(update_fields=["private_key", "public_key"])


def iter_remote_pages(target, actor, object_type):
    if target == target.domain.service_actor:
        # we want to parse all the content
        params = {}
    else:
        params = {"scope": f"actor:{target.full_username}"}

    auth = signing.get_auth(actor.private_key, actor.private_key_id)
    url = (
        "https://"
        + target.domain.name
        + reverse(
            f"api:v2:{object_type}-list",
        )
    )

    page = 0
    while url:
        page += 1
        if page > settings.FEDERATION_COLLECTION_MAX_PAGES:
            break
        response = session.get_session().get(
            url=url,
            params=params,
            auth=auth,
            headers={"Accept": "application/json"},
        )
        data = response.json()
        logger.debug(f"Remote answered with {data}")
        yield from data["results"]
        url = data["next"]
        # params = None  # next already includes params


@celery.app.task(name="federation.parse_actor_collection")
@celery.require_instance(models.Actor.objects.local(include=False), "target")
@celery.require_instance(models.Actor.objects.local(), "actor")
def parse_remote_collections(target, actor, object_type):
    from . import api_serializers

    for obj in iter_remote_pages(target, actor, object_type):
        fid = obj["actor"]["fid"] if object_type == "channels" else obj["fid"]

        fetch_serializer = api_serializers.FetchSerializer(data={"object_uri": fid})
        fetch_serializer.is_valid(raise_exception=True)
        fetch_obj = fetch_serializer.save(actor=actor)

        if fetch_obj.status != "finished":
            # no duplicate was returned, we can fetch again
            fetch.delay(fetch_id=fetch_obj.pk)


@celery.app.task(name="federation.fetch_past_activities", bind=True)
@celery.require_instance(models.Actor.objects.local(include=False), "target")
@celery.require_instance(models.Actor.objects.local(), "actor")
def fetch_past_activities(self, target, actor):
    logger.info(
        "Heavy task, if you want to abort you need to kill all the children "
        f"tasks sharing this group_id :  {self.request.root_id}"
    )
    chain(
        parse_remote_collections.si(
            target_id=target.pk, actor_id=actor.pk, object_type="libraries"
        ),
        parse_remote_collections.si(
            target_id=target.pk, actor_id=actor.pk, object_type="playlists"
        ),
        parse_remote_collections.si(
            target_id=target.pk, actor_id=actor.pk, object_type="favorites:tracks"
        ),
    ).apply_async()

    if not target == target.domain.service_actor:
        listenings_scan = history_models.ListeningsScan.objects.create(
            actor=actor, target=target
        )
        # This is (way) more efficient than parse_actor_collection since it only use one query
        # per page (but it still need to fetch tracks on by one).
        # Could implement the same for TrackFavorites
        # (not needed for libraries and playlists since they are collections)
        history_tasks.start_listenings_scan.si(listenings_scan_id=listenings_scan.pk),


@celery.app.task(name="federation.bulk_fetch_past_activities", bind=True)
@celery.require_instance(models.Actor.objects.local(), "actor")
def bulk_fetch_past_activities(self, target_ids, actor):
    logger.info(
        "Heavy task, if you want to abort you need to kill all the children "
        f"tasks sharing this group_id :  {self.request.root_id}"
    )
    tasks = []

    for target_id in target_ids:
        task = fetch_past_activities.si(target_id=target_id, actor_id=actor.pk)
        tasks.append(task)

    job = group(tasks)
    job.apply_async()


@celery.app.task(name="federation.fetch")
@transaction.atomic
@celery.require_instance(
    models.Fetch.objects.filter(status="pending").select_related("actor"),
    "fetch_obj",
    "fetch_id",
)
def fetch(fetch_obj):
    def error(code, **kwargs):
        fetch_obj.status = "errored"
        fetch_obj.fetch_date = timezone.now()
        fetch_obj.detail = {"error_code": code}
        fetch_obj.detail.update(kwargs)
        fetch_obj.save(update_fields=["fetch_date", "status", "detail"])

    url = fetch_obj.url
    mrf_check_url = url
    if not mrf_check_url.startswith("webfinger://"):
        payload, updated = mrf.inbox.apply({"id": mrf_check_url})
        if not payload:
            return error("blocked", message="Blocked by MRF")

    actor = fetch_obj.actor
    if settings.FEDERATION_AUTHENTIFY_FETCHES:
        auth = signing.get_auth(actor.private_key, actor.private_key_id)
    else:
        auth = None
    try:
        if url.startswith("webfinger://"):
            # we first grab the corresponding webfinger representation
            # to get the ActivityPub actor ID
            webfinger_data = webfinger.get_resource(
                "acct:" + url.replace("webfinger://", "")
            )
            url = webfinger.get_ap_url(webfinger_data["links"])
            if not url:
                return error("webfinger", message="Invalid or missing webfinger data")
            payload, updated = mrf.inbox.apply({"id": url})
            if not payload:
                return error("blocked", message="Blocked by MRF")
        response = session.get_session().get(
            auth=auth,
            url=url,
            headers={"Accept": "application/activity+json"},
        )
        logger.debug("Remote answered with %s: %s", response.status_code, response.text)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return error(
            "http",
            status_code=e.response.status_code if e.response else None,
            message=e.response.text,
        )
    except requests.exceptions.Timeout:
        return error("timeout")
    except requests.exceptions.ConnectionError as e:
        return error("connection", message=str(e))
    except requests.RequestException as e:
        return error("request", message=str(e))
    except Exception as e:
        return error("unhandled", message=str(e))

    try:
        payload = response.json()
    except json.decoder.JSONDecodeError:
        # we attempt to extract a <link rel=alternate> that points
        # to an activity pub resource, if possible, and retry with this URL
        alternate_url = utils.find_alternate(response.text)
        if alternate_url:
            fetch_obj.url = alternate_url
            fetch_obj.save(update_fields=["url"])
            return fetch(fetch_id=fetch_obj.pk)
        return error("invalid_json")

    payload, updated = mrf.inbox.apply(payload)
    if not payload:
        return error("blocked", message="Blocked by MRF")

    try:
        doc = jsonld.expand(payload)
    except ValueError:
        return error("invalid_jsonld")

    try:
        type = doc.get("@type", [])[0]
    except IndexError:
        return error("missing_jsonld_type")
    try:
        serializer_classes = fetch_obj.serializers[type]
        model = serializer_classes[0].Meta.model
    except (KeyError, AttributeError):
        fetch_obj.status = "skipped"
        fetch_obj.fetch_date = timezone.now()
        fetch_obj.detail = {"reason": "unhandled_type", "type": type}
        return fetch_obj.save(update_fields=["fetch_date", "status", "detail"])
    try:
        id = doc.get("@id")
    except IndexError:
        existing = None
    else:
        existing = model.objects.filter(fid=id).first()

    serializer = None
    for serializer_class in serializer_classes:
        serializer = serializer_class(
            existing, data=payload, context={"fetch_actor": actor}
        )
        if not serializer.is_valid():
            continue
        else:
            break
    if serializer.errors:
        return error("validation", validation_errors=serializer.errors)
    try:
        obj = serializer.save()
    except Exception as e:
        error("save", message=str(e))
        raise

    # special case for channels
    # when obj is an actor, we check if the actor has a channel associated with it
    # if it is the case, we consider the fetch obj to be a channel instead
    # and also trigger a fetch on the channel outbox
    if isinstance(obj, models.Actor) and obj.get_channel():
        obj = obj.get_channel()
        if obj.actor.outbox_url:
            try:
                # first page fetch is synchronous, so that at least some data is available
                # in the UI after subscription
                result = fetch_collection(
                    obj.actor.outbox_url,
                    channel_id=obj.pk,
                    max_pages=1,
                )
            except Exception:
                logger.exception(
                    "Error while fetching actor outbox: %s", obj.actor.outbox_url
                )
            else:
                if result.get("next_page"):
                    # additional pages are fetched in the background
                    result = fetch_collection.delay(
                        result["next_page"],
                        channel_id=obj.pk,
                        max_pages=settings.FEDERATION_COLLECTION_MAX_PAGES - 1,
                        is_page=True,
                    )
    # if it's an actor user we trigger a fetch on its activities
    elif (
        isinstance(obj, models.Actor) and not obj.get_channel() and obj.type == "Person"
    ):
        common_utils.on_commit(
            fetch_past_activities.delay, target_id=obj.pk, actor_id=actor.pk
        )

    elif isinstance(obj, music_models.Library):
        logger.info("fetch library trigger library scan")
        obj.schedule_scan(actor)
    elif isinstance(obj, playlists_models.Playlist):
        logger.info("fetch playlist trigger playlist scan")
        obj.schedule_scan(actor)

    fetch_obj.object = obj
    fetch_obj.status = "finished"
    fetch_obj.fetch_date = timezone.now()
    return fetch_obj.save(
        update_fields=["fetch_date", "status", "object_id", "object_content_type"]
    )


class PreserveSomeDataCollector(Collector):
    """
    We need to delete everything related to an actor. Well… Almost everything.
    But definitely not the Delete Activity we send to announce the actor is deleted.
    """

    def __init__(self, *args, **kwargs):
        self.creation_date = timezone.now()
        super().__init__(*args, **kwargs)

    def related_objects(self, related, *args, **kwargs):
        qs = super().related_objects(related, *args, **kwargs)
        # We can only exclude the actions if these fields are available, most likely its a
        # model.Activity than
        if hasattr(related, "type") and hasattr(related, "creation_date"):
            # exclude the delete activity can be broadcasted properly
            qs = qs.exclude(type="Delete", creation_date__gte=self.creation_date)

        return qs


@celery.app.task(name="federation.remove_actor")
@transaction.atomic
@celery.require_instance(
    models.Actor.objects.all(),
    "actor",
)
def remove_actor(actor):
    # Then we broadcast the info over federation. We do this *before* deleting objects
    # associated with the actor, otherwise follows are removed and we don't know where
    # to broadcast
    logger.info("Broadcasting deletion to federation…")
    collector = PreserveSomeDataCollector(using="default")
    routes.outbox.dispatch(
        {"type": "Delete", "object": {"type": actor.type}}, context={"actor": actor}
    )

    # then we delete any object associated with the actor object, but *not* the actor
    # itself. We keep it for auditability and sending the Delete ActivityPub message
    logger.info(
        "Prepare deletion of objects associated with account %s…",
        actor.preferred_username,
    )
    collector.collect([actor])
    for model, instances in collector.data.items():
        if issubclass(model, actor.__class__):
            # we skip deletion of the actor itself
            continue

        to_delete = model.objects.filter(pk__in=[instance.pk for instance in instances])
        logger.info(
            "Deleting %s objects associated with account %s…",
            len(instances),
            actor.preferred_username,
        )
        to_delete.delete()

    # Finally, we update the actor itself and mark it as removed
    logger.info("Marking actor as Tombsone…")
    actor.type = "Tombstone"
    actor.name = None
    actor.summary = None
    actor.save(update_fields=["type", "name", "summary"])


COLLECTION_ACTIVITY_SERIALIZERS = [
    (
        {"type": "Create", "object.type": "Audio"},
        serializers.ChannelCreateUploadSerializer,
    )
]


def match_serializer(payload, conf):
    return [
        serializer_class
        for route, serializer_class in conf
        if activity.match_route(route, payload)
    ]


@celery.app.task(name="federation.fetch_collection")
@celery.require_instance(
    audio_models.Channel.objects.all(),
    "channel",
    allow_null=True,
)
def fetch_collection(url, max_pages, channel, is_page=False):
    actor = actors.get_service_actor()
    results = {
        "items": [],
        "skipped": 0,
        "errored": 0,
        "seen": 0,
        "total": 0,
    }
    if is_page:
        # starting immediately from a page, no need to fetch the wrapping collection
        logger.debug("Fetch collection page immediately at %s", url)
        results["next_page"] = url
    else:
        logger.debug("Fetching collection object at %s", url)
        collection = utils.retrieve_ap_object(
            url,
            actor=actor,
            serializer_class=serializers.PaginatedCollectionSerializer,
        )
        results["next_page"] = collection["first"]
        results["total"] = collection.get("totalItems")

    seen_pages = 0
    context = {}
    if channel:
        context["channel"] = channel

    for i in range(max_pages):
        page_url = results["next_page"]
        logger.debug("Handling page %s on max %s, at %s", i + 1, max_pages, page_url)
        page = utils.retrieve_ap_object(
            page_url,
            actor=actor,
            serializer_class=None,
        )
        try:
            items = page["orderedItems"]
        except KeyError:
            try:
                items = page["items"]
            except KeyError:
                logger.error("Invalid collection page at %s", page_url)
                break

        for item in items:
            results["seen"] += 1

            matching_serializer = match_serializer(
                item, COLLECTION_ACTIVITY_SERIALIZERS
            )
            if not matching_serializer:
                results["skipped"] += 1
                logger.debug("Skipping unhandled activity %s", item.get("type"))
                continue

            s = matching_serializer[0](data=item, context=context)
            if not s.is_valid():
                logger.warn("Skipping invalid activity: %s", s.errors)
                results["errored"] += 1
                continue

            results["items"].append(s.save())

        seen_pages += 1
        results["next_page"] = page.get("next", None) or None
        if not results["next_page"]:
            logger.debug("No more pages to fetch")
            break

    logger.info(
        "Finished fetch of collection pages at %s. Results:\n"
        "  Total in collection: %s\n"
        "  Seen: %s\n"
        "  Handled: %s\n"
        "  Skipped: %s\n"
        "  Errored: %s",
        url,
        results.get("total"),
        results["seen"],
        len(results["items"]),
        results["skipped"],
        results["errored"],
    )
    return results


@celery.app.task(name="federation.check_all_remote_instance_availability")
def check_all_remote_instance_availability():
    base_interval = 3600
    factor = 1.15

    for domain in models.Domain.objects.all():
        if domain.name == settings.FUNKWHALE_HOSTNAME:
            continue

        attempt = domain.reachable_retries or 0
        last_success = domain.last_successful_contact or domain.creation_date

        delay_seconds = base_interval * (factor**attempt)
        delay = datetime.timedelta(seconds=delay_seconds)

        next_check_due = last_success + delay
        now = timezone.now()

        if domain.reachable is False and now < next_check_due:
            logger.info(
                f"[{domain.name}] Skipping check. Last successful: {last_success}, "
                f"attempt #{attempt}, next check due in {delay} at {next_check_due}"
            )
            continue

        check_single_remote_instance_availability(domain)


@celery.app.task(name="federation.check_single_remote_instance_availability")
def check_single_remote_instance_availability(domain):
    try:
        nodeinfo = fetch_nodeinfo(domain.name)
    except Exception as e:
        logger.info(
            f"Domain {domain.name} could not be reached because of the following error : {e}. \
            Setting domain as unreachable."
        )
        domain.reachable = False
        domain.reachable_retries += 1
        domain.save()
        return domain.reachable

    if "version" in nodeinfo.keys():
        domain.reachable = True
        domain.last_successful_contact = timezone.now()
        domain.reachable_retries = 0
        domain.save()
        return domain.reachable
    else:
        logger.info(
            f"Domain {domain.name} is not reachable at the moment. Setting domain as unreachable."
        )
        domain.reachable = False
        domain.reachable_retries += 1
        domain.save()
        return domain.reachable


@celery.app.task(name="federation.trigger_playlist_ap_update")
def trigger_playlist_ap_update(playlist):
    for playlist_uuid in cache.get("playlists_for_ap_update"):
        routes.outbox.dispatch(
            {"type": "Update", "object": {"type": "Playlist"}},
            context={
                "playlist": playlists_models.Playlist.objects.get(uuid=playlist_uuid)
            },
        )


def create_domains(data, local_domains):
    from . import api_serializers

    for remote_domain in data["results"]:
        if remote_domain["name"] in local_domains:
            logger.info("Domain already in db. Skipping")
            continue

        else:
            logger.info(f"Adding discovered domain {remote_domain} to db")
            data = {"name": remote_domain["name"], "creation_date": timezone.now}
            serializer = api_serializers.DomainSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            domain = serializer.save()
            update_domain_nodeinfo(domain_name=domain.name)


@celery.app.task(name="federation.discover_domains")
def discover_domains_from_known_ones():
    if preferences.get("federation__auto_federation") is False:
        logger.info("Automatic federation is disabled. Skipping task.")
        return

    local_fw_domains = (
        models.Domain.objects.all()
        .exclude(is_funkwhale_instance=False)
        .exclude(name=settings.FEDERATION_HOSTNAME)
        .exclude(reachable=False)
    )

    # loaded into memory to avoid networks requests by checking if we already know them.
    local_domains = (
        models.Domain.objects.all()
        .exclude(name=settings.FEDERATION_HOSTNAME)
        .values_list("name", flat=True)
    )

    for local_fw_domain in local_fw_domains:
        url = utils.get_remote_url(
            local_fw_domain,
            reverse("api:v2:federation:domains-list"),
            {"is_funkwhale_instance": True},
        )

        try:
            response = session.get_session().get(url)
        except Exception as e:
            local_fw_domain.reachable = False
            local_fw_domain.reachable_retries += 1
            local_fw_domain.save()
            logger.info(
                f"Domain {local_fw_domain.name} is not reachable at the moment. Setting domain as unreachable. "
                f"Exception was {e}"
            )
            return

        if response.status_code != 200:
            logger.info(
                f"No domain found from {url}, status code: {response.status_code}"
            )
            return

        create_domains(response.json(), local_domains)


@celery.app.task(name="federation.discover_domains_from_funkwhale_audio")
def discover_domains_from_funkwhale_audio():
    if preferences.get("federation__auto_federation") is False:
        logger.info("Automatic federation is disabled. Skipping task.")
        return
    url = "https://network.funkwhale.audio/api/domains"
    local_domains = (
        models.Domain.objects.all()
        .exclude(name=settings.FEDERATION_HOSTNAME)
        .values_list("name", flat=True)
    )
    try:
        response = session.get_session().get(url)
    except Exception as e:
        logger.info("Network.funkwhale.audio is not reachable at the moment.")
        raise e

    if response.status_code != 200:
        logger.info(f"No domains found, status code: {response.status_code}")
        return

    create_domains(response.json(), local_domains)


@celery.app.task(name="federation.follow_all_domains")
def follow_all_domains():
    from . import api_serializers

    if preferences.get("federation__auto_federation") is False:
        logger.info("Automatic federation is disabled. Skipping task.")
        return

    actor = actors.get_service_actor()
    domains = (
        models.Domain.objects.all()
        .exclude(name=settings.FEDERATION_HOSTNAME)
        .exclude(is_funkwhale_instance=False)
        .exclude(reachable=False)
        .exclude(service_actor__following=actor)
    )
    target_ids = []
    for domain in domains:
        try:
            data = {"target": domain.name}
            serializer = api_serializers.DomainFollowSerializer(
                data=data, context={"actor": actor}
            )
            if serializer.is_valid():
                follow_serializer = api_serializers.FollowSerializer(
                    data=serializer.validated_data, context={"actor": actor}
                )
                if follow_serializer.is_valid():
                    follow = follow_serializer.save(actor=actors.get_service_actor())
                    routes.outbox.dispatch(
                        {"type": "Follow"}, context={"follow": follow}
                    )
                target_ids.append(follow.target.pk)
        except Exception as e:
            logger.error(f"Unhandled error while creating domain follow : {e} ")
    bulk_fetch_past_activities.delay(
        target_ids=target_ids,
        actor_id=actors.get_service_actor().pk,
    )
