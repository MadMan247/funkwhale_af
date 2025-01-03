from django.core.paginator import Paginator

from funkwhale_api.federation import serializers as federation_serializers
from funkwhale_api.playlists import tasks


def test_scan_playlist_page_fetches_page_and_creates_tracks(
    now, mocker, factories, r_mock
):
    scan_page = mocker.patch("funkwhale_api.playlists.tasks.scan_playlist_page.delay")
    scan = factories["playlists.PlaylistScan"](status="scanning", total_files=5)
    tracks = [
        factories["playlists.PlaylistTrack"](
            playlist=scan.playlist,
            index=i,
        )
        for i in range(5)
    ]

    page_conf = {
        "actor": scan.playlist.actor,
        "id": scan.playlist.fid,
        "page": Paginator(tracks, 3).page(1),
        "item_serializer": federation_serializers.PlaylistTrackSerializer,
    }
    tracks[0].__class__.objects.filter(pk__in=[u.pk for u in tracks]).delete()
    page = federation_serializers.CollectionPageSerializer(page_conf)

    r_mock.get(page.data["id"], json=page.data)

    tasks.scan_playlist_page(playlist_scan_id=scan.pk, page_url=page.data["id"])

    scan.refresh_from_db()
    plts = list(scan.playlist.playlist_tracks.all().order_by("-creation_date"))

    assert len(plts) == 3
    for track in tracks[:3]:
        scan.playlist.playlist_tracks.get(fid=track.fid)

    assert scan.status == "scanning"
    assert scan.processed_files == 3
    assert scan.modification_date == now

    scan_page.assert_called_once_with(
        playlist_scan_id=scan.pk, page_url=page.data["next"]
    )


def test_scan_playlist_fetches_page_and_calls_scan_page(now, mocker, factories, r_mock):
    scan = factories["playlists.PlaylistScan"]()
    factories["playlists.PlaylistTrack"].create_batch(size=10, playlist=scan.playlist)
    collection_conf = {
        "actor": scan.playlist.actor,
        "id": scan.playlist.fid,
        "page_size": 10,
        "items": range(10),
        "type": "Playlist",
        "name": "hello",
    }
    collection = federation_serializers.PlaylistCollectionSerializer(scan.playlist)
    data = collection.data
    data["followers"] = "https://followers.domain"
    scan_page = mocker.patch("funkwhale_api.playlists.tasks.scan_playlist_page.delay")
    r_mock.get(collection_conf["id"], json=data)
    tasks.start_playlist_scan(playlist_scan_id=scan.pk)

    scan_page.assert_called_once_with(playlist_scan_id=scan.pk, page_url=data["first"])
    scan.refresh_from_db()

    assert scan.status == "scanning"
    assert scan.total_files == len(collection_conf["items"])
    assert scan.modification_date == now


def test_scan_page_fetches_page_and_creates_tracks(now, mocker, factories, r_mock):
    scan_page = mocker.patch("funkwhale_api.playlists.tasks.scan_playlist_page.delay")
    scan = factories["playlists.PlaylistScan"](status="scanning", total_files=5)
    tracks = [
        factories["playlists.PlaylistTrack"](
            playlist=scan.playlist,
            index=i,
        )
        for i in range(5)
    ]

    page_conf = {
        "actor": scan.playlist.actor,
        "id": scan.playlist.fid,
        "page": Paginator(tracks, 3).page(1),
        "item_serializer": federation_serializers.PlaylistTrackSerializer,
    }
    tracks[0].__class__.objects.filter(pk__in=[u.pk for u in tracks]).delete()
    page = federation_serializers.CollectionPageSerializer(page_conf)

    r_mock.get(page.data["id"], json=page.data)

    tasks.scan_playlist_page(playlist_scan_id=scan.pk, page_url=page.data["id"])

    scan.refresh_from_db()
    lts = list(scan.playlist.playlist_tracks.all().order_by("-creation_date"))

    assert len(lts) == 3
    for track in tracks[:3]:
        scan.playlist.playlist_tracks.get(fid=track.fid)

    assert scan.status == "scanning"
    assert scan.processed_files == 3
    assert scan.modification_date == now

    scan_page.assert_called_once_with(
        playlist_scan_id=scan.pk, page_url=page.data["next"]
    )


def test_scan_page_trigger_next_page_scan_skip_if_same(mocker, factories, r_mock):
    patched_scan = mocker.patch(
        "funkwhale_api.playlists.tasks.scan_playlist_page.delay"
    )
    scan = factories["playlists.PlaylistScan"](status="scanning", total_files=5)
    uploads = factories["playlists.PlaylistTrack"].build_batch(
        size=5, playlist=scan.playlist
    )
    page_conf = {
        "actor": scan.playlist.actor,
        "id": scan.playlist.fid,
        "page": Paginator(uploads, 3).page(1),
        "item_serializer": federation_serializers.PlaylistTrackSerializer,
    }
    page = federation_serializers.CollectionPageSerializer(page_conf)
    data = page.data
    data["next"] = data["id"]
    r_mock.get(page.data["id"], json=data)

    tasks.scan_playlist_page(playlist_scan_id=scan.pk, page_url=data["id"])
    patched_scan.assert_not_called()
    scan.refresh_from_db()

    assert scan.status == "finished"
