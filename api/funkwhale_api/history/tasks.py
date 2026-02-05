import logging

from requests.exceptions import RequestException

from funkwhale_api.common import session
from funkwhale_api.federation import models as federation_models
from funkwhale_api.federation import serializers, signing
from funkwhale_api.taskapp import celery

from . import models

logger = logging.getLogger("plugins")


def get_listenings_collection(collection_url, request_actor):
    auth = signing.get_auth(request_actor.private_key, request_actor.private_key_id)

    response = session.get_session().get(
        collection_url,
        auth=auth,
        headers={"Accept": "application/activity+json"},
    )

    if response.status_code >= 400:
        return {"errors": [f"HTTP {response.status_code}"]}

    serializer = serializers.IndexSerializer(data=response.json())
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


def get_listenings_page(actor, page_url):
    auth = signing.get_auth(actor.private_key, actor.private_key_id)

    response = session.get_session().get(
        page_url,
        auth=auth,
        headers={"Accept": "application/activity+json"},
    )
    logger.debug(f"listening page response {response.json()}")
    serializer = serializers.CollectionPageSerializer(
        data=response.json(),
        context={
            "item_serializer": serializers.ListeningSerializer,
        },
    )
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


@celery.app.task(
    name="music.scan_listenings_page",
    retry_backoff=60,
    max_retries=5,
    autoretry_for=[RequestException],
)
@celery.require_instance(federation_models.Actor.objects.all(), "actor")
def scan_listenings_page(actor, page_url):
    data = get_listenings_page(actor, page_url)
    created = 0

    for listening_serializer in data["items"]:
        listening_serializer.save()
        created += 1

    next_page = data.get("next")
    if next_page and next_page != page_url:
        scan_listenings_page.delay(actor_id=actor.pk, page_url=next_page)


@celery.app.task(name="music.start_listenings_scan")
@celery.require_instance(models.ListeningsScan.objects.all(), "listenings_scan")
def start_listenings_scan(listenings_scan):
    lst_actor = listenings_scan.target
    # to do : pass listens and favorites endpoints to actor object through federation.
    collection_url = lst_actor.fid + "/listens"
    data = get_listenings_collection(collection_url, listenings_scan.actor)

    if "errors" in data:
        raise Exception(data["errors"])

    first_page = data.get("first")
    if not data.get("totalItems") > 0:
        return

    scan_listenings_page.delay(
        actor_id=listenings_scan.actor.pk,
        page_url=first_page,
    )
