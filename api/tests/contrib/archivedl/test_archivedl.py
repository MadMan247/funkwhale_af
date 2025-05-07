import logging

import pytest

from funkwhale_api.contrib.archivedl import tasks


def test_check_existing_download_task(factories, caplog, mocker):
    logger = logging.getLogger("funkwhale_api.contrib.archivedl")
    caplog.set_level(logging.INFO)
    logger.addHandler(caplog.handler)
    upload = factories["music.Upload"](
        third_party_provider="archive-dl", import_status="pending"
    )
    mocker.patch("funkwhale_api.contrib.archivedl.tasks.fetch_json", return_value={})
    tasks.archive_download(track_id=upload.track.id, conf={})
    assert (
        "Upload for this track already exist or is pending. Stopping task"
        in caplog.text
    )


def test_check_last_third_party_queries(factories, caplog, mocker):
    logger = logging.getLogger("funkwhale_api.contrib.archivedl")
    caplog.set_level(logging.INFO)
    logger.addHandler(caplog.handler)
    factories["music.Upload"].create_batch(
        size=10, third_party_provider="archive-dl", import_status="pending"
    )
    track = factories["music.Track"]()
    mocker.patch("funkwhale_api.contrib.archivedl.tasks.fetch_json", return_value={})

    with pytest.raises(KeyError):
        tasks.archive_download(track_id=track.id, conf={})
    assert (
        "Last archive.org query was too recent. Trying to wait 2 seconds..."
        in caplog.text
    )
