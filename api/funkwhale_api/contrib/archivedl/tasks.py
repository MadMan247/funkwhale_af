import asyncio
import hashlib
import logging
import os
import tempfile
import urllib.parse

import requests
from django.core.files import File
from django.utils import timezone

from funkwhale_api.federation import actors
from funkwhale_api.music import models, utils
from funkwhale_api.taskapp import celery

logger = logging.getLogger(__name__)


def create_upload(url, track, files_data):
    mimetype = f"audio/{files_data.get('format', 'unknown')}"
    duration = files_data.get("mtime", 0)
    filesize = files_data.get("size", 0)
    bitrate = files_data.get("bitrate", 0)

    service_library = models.Library.objects.create(
        privacy_level="everyone",
        actor=actors.get_service_actor(),
    )

    return models.Upload.objects.create(
        mimetype=mimetype,
        source=url,
        third_party_provider="archive-dl",
        creation_date=timezone.now(),
        track=track,
        duration=duration,
        size=filesize,
        bitrate=bitrate,
        library=service_library,
        from_activity=None,
        import_status="finished",
    )


@celery.app.task(name="archivedl.archive_download")
@celery.require_instance(models.Track.objects.select_related(), "track")
def archive_download(track, conf):
    artist_name = utils.get_artist_credit_string(track)
    query = f"mediatype:audio AND title:{track.title} AND creator:{artist_name}"
    with requests.Session() as session:
        url = get_search_url(query, page_size=1, page=1)
        page_data = fetch_json(url, session)
        for obj in page_data["response"]["docs"]:
            logger.info(f"launching download item for {str(obj)}")
            download_item(
                item_data=obj,
                session=session,
                allowed_extensions=utils.SUPPORTED_EXTENSIONS,
                track=track,
            )


def fetch_json(url, session):
    logger.info(f"Fetching {url}...")
    with session.get(url) as response:
        return response.json()


def download_item(
    item_data,
    session,
    allowed_extensions,
    track,
):
    files_data = get_files_data(item_data["identifier"], session)
    to_download = list(
        filter_files(
            files_data["result"],
            allowed_extensions=allowed_extensions,
        )
    )
    url = f"https://archive.org/download/{item_data['identifier']}/{to_download[0]['name']}"
    upload = create_upload(url, track, to_download[0])
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, to_download[0]["name"])
            download_file(
                path,
                url=url,
                session=session,
                checksum=to_download[0]["sha1"],
                upload=upload,
                to_download=to_download,
            )

            logger.info(f"Finished to download item {item_data['identifier']}...")
    except Exception as e:
        upload.delete()
        raise e


def check_integrity(path, expected_checksum):
    with open(path, mode="rb") as f:
        hash = hashlib.sha1()
        hash.update(f.read())

        return expected_checksum == hash.hexdigest()


def get_files_data(identifier, session):
    url = f"https://archive.org/metadata/{identifier}/files"
    logger.info(f"Fetching files data at {url}...")
    with session.get(url) as response:
        return response.json()


def download_file(path, url, session, checksum, upload, to_download):
    if os.path.exists(path) and check_integrity(path, checksum):
        logger.info(f"Skipping already downloaded file at {path}")
        return
    logger.info(f"Downloading file {url}...")
    with open(path, mode="wb") as f:
        try:
            with session.get(url) as response:
                f.write(response.content)
        except asyncio.TimeoutError as e:
            logger.error(f"Timeout error while downloading {url}: {e}")

    with open(path, "rb") as f:
        upload.audio_file.save(f"{to_download['name']}", File(f))
        upload.import_status = "finished"
        upload.url = url
        upload.save()
        return upload


def filter_files(files, allowed_extensions):
    for f in files:
        if allowed_extensions:
            extension = os.path.splitext(f["name"])[-1][1:]
            if extension not in allowed_extensions:
                continue
        yield f


def get_search_url(query, page_size, page):
    q = urllib.parse.urlencode({"q": query})
    return f"https://archive.org/advancedsearch.php?{q}&sort[]=addeddate+desc&rows={page_size}&page={page}&output=json"
