import logging

import requests
from django.db.models import F
from django.utils import timezone
from requests.exceptions import RequestException

from funkwhale_api.common import session
from funkwhale_api.federation import serializers, signing
from funkwhale_api.taskapp import celery

from . import models

logger = logging.getLogger(__name__)


def get_playlist_data(playlist_url, actor):
    auth = signing.get_auth(actor.private_key, actor.private_key_id)
    try:
        response = session.get_session().get(
            playlist_url,
            auth=auth,
            headers={"Accept": "application/activity+json"},
        )
    except requests.ConnectionError:
        return {"errors": ["This playlist is not reachable"]}
    scode = response.status_code
    if scode == 401:
        return {"errors": ["This playlist requires authentication"]}
    elif scode == 403:
        return {
            "errors": [
                f"Permission denied while scanning playlist. Error : {scode}. PLaylist url = {playlist_url}"
            ]
        }
    elif scode >= 400:
        return {"errors": [f"Error {scode} while fetching the playlist"]}
    serializer = serializers.PlaylistCollectionSerializer(data=response.json())

    if not serializer.is_valid():
        return {"errors": ["Invalid ActivityPub response from remote playlist"]}

    return serializer.validated_data


def get_playlist_page(playlist, page_url, actor):
    auth = signing.get_auth(actor.private_key, actor.private_key_id)
    response = session.get_session().get(
        page_url,
        auth=auth,
        headers={"Accept": "application/activity+json"},
    )
    serializer = serializers.CollectionPageSerializer(
        data=response.json(),
        context={
            "playlist": playlist,
            "item_serializer": serializers.PlaylistTrackSerializer,
            "conf": {"library": playlist.library},
        },
    )
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


@celery.app.task(name="playlist.start_playlist_scan")
@celery.require_instance(
    models.PlaylistScan.objects.select_related().filter(status="pending"),
    "playlist_scan",
)
def start_playlist_scan(playlist_scan):
    playlist_scan.playlist.playlist_tracks.all().delete()

    try:
        data = get_playlist_data(playlist_scan.playlist.fid, actor=playlist_scan.actor)
    except Exception:
        playlist_scan.status = "errored"
        playlist_scan.save(update_fields=["status", "modification_date"])
        raise
    if "errors" in data.keys():
        playlist_scan.status = "errored"
        playlist_scan.save(update_fields=["status", "modification_date"])
        raise Exception("Error from remote server : " + str(data))
    playlist_scan.modification_date = timezone.now()
    playlist_scan.status = "scanning"
    playlist_scan.total_files = data["totalItems"]

    playlist_scan.save(update_fields=["status", "modification_date", "total_files"])
    scan_playlist_page.delay(playlist_scan_id=playlist_scan.pk, page_url=data["first"])


@celery.app.task(
    name="playlist.scan_playlist_page",
    retry_backoff=60,
    max_retries=5,
    autoretry_for=[RequestException],
)
@celery.require_instance(
    models.PlaylistScan.objects.select_related().filter(status="scanning"),
    "playlist_scan",
)
def scan_playlist_page(playlist_scan, page_url):
    data = get_playlist_page(playlist_scan.playlist, page_url, playlist_scan.actor)
    plts = []
    for item_serializer in data["items"]:
        try:
            plt = item_serializer.save(playlist=playlist_scan.playlist.fid)
            # we get any upload owned by the playlist.actor and add a m2m with playlist_libraries
            upload_qs = plt.track.uploads.filter(
                library__actor=playlist_scan.playlist.actor
            )
            if not upload_qs:
                logger.debug(
                    f"Could not find a upload for the playlist track {plt.track.title}. Probably the \
                    playlist.library library_scan failed or was not launched by inbox_update_playlist ?"
                )
            else:
                upload_qs[0].playlist_libraries.add(playlist_scan.playlist.library)
                logger.debug(f"Added {plt.track.title} to playlist library")
            plts.append(plt)
        except Exception as e:
            logger.info(
                f"Error while saving track to playlist {playlist_scan.playlist}: {e}"
            )
            continue

    playlist_scan.processed_files = F("processed_files") + len(plts)
    playlist_scan.modification_date = timezone.now()
    update_fields = ["modification_date", "processed_files"]

    next_page = data.get("next")
    fetch_next = next_page and next_page != page_url

    if not fetch_next:
        update_fields.append("status")
        playlist_scan.status = "finished"
    playlist_scan.save(update_fields=update_fields)

    if fetch_next:
        scan_playlist_page.delay(playlist_scan_id=playlist_scan.pk, page_url=next_page)
