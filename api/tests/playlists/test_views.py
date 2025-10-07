import pytest
from django.urls import reverse

from funkwhale_api.playlists import models


def test_can_create_playlist_via_api(logged_in_api_client):
    actor = logged_in_api_client.user.create_actor()
    url = reverse("api:v1:playlists-list")
    data = {"name": "test", "privacy_level": "everyone"}

    logged_in_api_client.post(url, data)

    playlist = models.Playlist.objects.latest("id")
    assert playlist.name == "test"
    assert playlist.actor == actor
    assert playlist.privacy_level == "everyone"


def test_serializer_includes_tracks_count(factories, logged_in_api_client):
    actor = logged_in_api_client.user.create_actor()
    playlist = factories["playlists.Playlist"](actor=actor)
    factories["playlists.PlaylistTrack"](playlist=playlist)
    url = reverse("api:v1:playlists-detail", kwargs={"uuid": playlist.uuid})
    response = logged_in_api_client.get(url, content_type="application/json")

    assert response.data["tracks_count"] == 1


def test_serializer_includes_tracks_count_986(factories, logged_in_api_client):
    logged_in_api_client.user.create_actor()
    playlist = factories["playlists.Playlist"](privacy_level="everyone")
    plt = factories["playlists.PlaylistTrack"](playlist=playlist)
    factories["music.Upload"].create_batch(
        3, track=plt.track, library__privacy_level="everyone", import_status="finished"
    )
    url = reverse("api:v1:playlists-detail", kwargs={"uuid": playlist.uuid})
    response = logged_in_api_client.get(url, content_type="application/json")

    assert response.data["tracks_count"] == 1


def test_serializer_includes_is_playable(factories, logged_in_api_client):
    logged_in_api_client.user.create_actor()
    playlist = factories["playlists.Playlist"](privacy_level="everyone")
    factories["playlists.PlaylistTrack"](playlist=playlist)

    url = reverse("api:v1:playlists-detail", kwargs={"uuid": playlist.uuid})
    response = logged_in_api_client.get(url, content_type="application/json")

    assert response.data["is_playable"] is False


def test_serializer_includes_followers_lib(factories, logged_in_api_client):
    actor = logged_in_api_client.user.create_actor()
    playlist = factories["playlists.Playlist"](privacy_level="followers", actor=actor)

    url = reverse("api:v1:playlists-detail", kwargs={"uuid": playlist.uuid})
    response = logged_in_api_client.get(url, content_type="application/json")

    assert response.data["is_playable"] is False


def test_playlist_inherits_user_privacy(logged_in_api_client):
    url = reverse("api:v1:playlists-list")
    user = logged_in_api_client.user
    user.create_actor()
    user.privacy_level = "me"
    user.save()

    data = {"name": "test"}

    logged_in_api_client.post(url, data)
    playlist = models.Playlist.objects.filter(actor=user.actor).latest("id")
    assert playlist.privacy_level == user.privacy_level


@pytest.mark.parametrize(
    "name,method",
    [("api:v1:playlists-list", "post")],
)
def test_url_requires_login(name, method, factories, api_client):
    url = reverse(name)

    response = getattr(api_client, method.lower())(url, {})

    assert response.status_code == 401


def test_only_can_add_track_on_own_playlist_via_api(factories, logged_in_api_client):
    logged_in_api_client.user.create_actor()
    track = factories["music.Track"]()
    playlist = factories["playlists.Playlist"]()
    url = reverse("api:v1:playlists-add", kwargs={"uuid": playlist.uuid})
    data = {"tracks": [track.pk]}

    response = logged_in_api_client.post(url, data, content_type="application/json")
    assert response.status_code == 404
    assert playlist.playlist_tracks.count() == 0


def test_deleting_plt_updates_indexes(mocker, factories, logged_in_api_client):
    actor = logged_in_api_client.user.create_actor()
    remove = mocker.spy(models.Playlist, "remove")
    factories["music.Track"]()
    playlist = factories["playlists.Playlist"](actor=actor)
    plt0 = factories["playlists.PlaylistTrack"](index=0, playlist=playlist)
    plt1 = factories["playlists.PlaylistTrack"](index=1, playlist=playlist)
    url = reverse("api:v1:playlists-remove", kwargs={"uuid": playlist.uuid})

    response = logged_in_api_client.delete(url, {"index": 0})

    assert response.status_code == 204
    remove.assert_called_once_with(plt0.playlist, 0)
    with pytest.raises(plt0.DoesNotExist):
        plt0.refresh_from_db()
    plt1.refresh_from_db()
    assert plt1.index == 0


def test_deleting_plt_updates_pl_lib(mocker, factories, logged_in_api_client):
    actor = logged_in_api_client.user.create_actor()
    factories["music.Track"]()
    playlist = factories["playlists.Playlist"](actor=actor)
    # playlist.library.uploads.add(plt0.track.uploads.all()[0])
    # playlist.library.uploads.add(plt1.track.uploads.all()[0])

    tracks = factories["music.Track"].create_batch(size=5)
    for track in tracks:
        factories["music.Upload"](track=track, library__actor=actor)

    not_user_actor = factories["federation.Actor"]()
    not_user_upload = factories["music.Upload"](
        track=tracks[0], library__actor=not_user_actor
    )

    track_ids = [t.id for t in tracks]
    url = reverse("api:v1:playlists-add", kwargs={"uuid": playlist.uuid})
    logged_in_api_client.post(url, {"tracks": track_ids})

    assert not_user_upload not in playlist.library.uploads.all()
    for plt in playlist.playlist_tracks.all():
        for upload in playlist.library.uploads.all():
            assert upload.tracks.filter(id=plt.track.id).exists()

    url = reverse("api:v1:playlists-remove", kwargs={"uuid": playlist.uuid})
    logged_in_api_client.delete(url, {"index": 0})
    playlist.library.refresh_from_db()

    for plt in playlist.playlist_tracks.all():
        for upload in playlist.library.uploads.all():
            assert not upload.tracks.filter(id=plt.track.id).exists()


@pytest.mark.parametrize("level", ["instance", "me", "followers"])
def test_playlist_privacy_respected_in_list_anon(
    preferences, level, factories, api_client
):
    preferences["common__api_authentication_required"] = False
    factories["playlists.Playlist"](privacy_level=level)
    url = reverse("api:v1:playlists-list")
    response = api_client.get(url)

    assert response.data["count"] == 0


@pytest.mark.parametrize("method", ["PUT", "PATCH", "DELETE"])
def test_only_owner_can_edit_playlist(method, factories, logged_in_api_client):
    logged_in_api_client.user.create_actor()
    playlist = factories["playlists.Playlist"]()
    url = reverse("api:v1:playlists-detail", kwargs={"uuid": playlist.uuid})
    response = getattr(logged_in_api_client, method.lower())(url)

    assert response.status_code == 404


def test_can_add_multiple_tracks_at_once_via_api(
    factories, mocker, logged_in_api_client
):
    actor = logged_in_api_client.user.create_actor()
    playlist = factories["playlists.Playlist"](actor=actor)
    tracks = factories["music.Track"].create_batch(size=5)
    track_ids = [t.id for t in tracks]
    mocker.spy(playlist, "insert_many")
    url = reverse("api:v1:playlists-add", kwargs={"uuid": playlist.uuid})
    response = logged_in_api_client.post(url, {"tracks": track_ids})

    assert response.status_code == 201
    assert playlist.playlist_tracks.count() == len(track_ids)

    for plt in playlist.playlist_tracks.order_by("index"):
        assert response.data["results"][plt.index]["index"] == plt.index
        assert plt.track == tracks[plt.index]


def test_add_multiple_tracks_at_once_update_pl_library(
    factories, mocker, logged_in_api_client
):
    actor = logged_in_api_client.user.create_actor()
    playlist = factories["playlists.Playlist"](actor=actor)
    tracks = factories["music.Track"].create_batch(size=5)
    not_user_actor = factories["federation.Actor"]()
    not_user_track = factories["music.Track"]()
    not_user_upload = factories["music.Upload"](
        size=5, track=not_user_track, library__actor=not_user_actor
    )
    for track in tracks:
        factories["music.Upload"](track=track, library__actor=actor)

    track_already_in_playlist = factories["music.Track"]()
    upload_already_in_playlist = factories["music.Upload"](
        track=track_already_in_playlist, library__actor=actor
    )
    upload_already_in_playlist.playlist_libraries.add(playlist.library)

    track_ids = [t.id for t in tracks]
    track_ids.append(not_user_track.id)
    track_ids.append(track_already_in_playlist.id)
    mocker.spy(playlist, "insert_many")
    url = reverse("api:v1:playlists-add", kwargs={"uuid": playlist.uuid})
    response = logged_in_api_client.post(url, {"tracks": track_ids})

    assert response.status_code == 201
    assert playlist.playlist_tracks.count() == len(track_ids)
    assert playlist.playlist_tracks.filter(track=not_user_track).exists()
    assert not_user_upload not in playlist.library.uploads.all()
    for plt in playlist.playlist_tracks.all():
        for upload in playlist.library.uploads.all():
            assert upload.tracks.filter(id=plt.track.id).exists()
            assert len(upload.playlist_libraries.all()) == 1


def test_honor_max_playlist_size(factories, mocker, logged_in_api_client, preferences):
    actor = logged_in_api_client.user.create_actor()
    preferences["playlists__max_tracks"] = 3
    playlist = factories["playlists.Playlist"](actor=actor)
    tracks = factories["music.Track"].create_batch(
        size=preferences["playlists__max_tracks"] + 1
    )
    track_ids = [t.id for t in tracks]
    mocker.spy(playlist, "insert_many")
    url = reverse("api:v1:playlists-add", kwargs={"uuid": playlist.uuid})
    response = logged_in_api_client.post(url, {"tracks": track_ids})

    assert response.status_code == 400


def test_can_clear_playlist_from_api(factories, mocker, logged_in_api_client):
    actor = logged_in_api_client.user.create_actor()
    playlist = factories["playlists.Playlist"](actor=actor)
    factories["playlists.PlaylistTrack"].create_batch(size=5, playlist=playlist)
    url = reverse("api:v1:playlists-clear", kwargs={"uuid": playlist.uuid})
    response = logged_in_api_client.delete(url)

    assert response.status_code == 204
    assert playlist.playlist_tracks.count() == 0


def test_clear_playlist_from_api_remove_pl_lib_uploads(
    factories, mocker, logged_in_api_client
):
    actor = logged_in_api_client.user.create_actor()
    playlist = factories["playlists.Playlist"](actor=actor)
    factories["playlists.PlaylistTrack"].create_batch(size=5, playlist=playlist)
    for upload in playlist.library.uploads.all():
        assert upload.playlist_libraries.filter(playlist=playlist).exists()
        assert upload.playlist_libraries.get(playlist=playlist).actor == actor
    url = reverse("api:v1:playlists-clear", kwargs={"uuid": playlist.uuid})
    response = logged_in_api_client.delete(url)

    assert response.status_code == 204
    assert not playlist.library.uploads.all()


def test_update_playlist_from_api(factories, mocker, logged_in_api_client):
    actor = logged_in_api_client.user.create_actor()
    playlist = factories["playlists.Playlist"](actor=actor)
    factories["playlists.PlaylistTrack"].create_batch(size=5, playlist=playlist)
    url = reverse("api:v1:playlists-detail", kwargs={"uuid": playlist.uuid})
    response = logged_in_api_client.patch(url, {"name": "test"})
    playlist.refresh_from_db()

    assert response.status_code == 200
    assert response.data["actor"]["full_username"] == playlist.actor.full_username


def test_move_plt_updates_indexes(mocker, factories, logged_in_api_client):
    actor = logged_in_api_client.user.create_actor()
    playlist = factories["playlists.Playlist"](actor=actor)
    plt0 = factories["playlists.PlaylistTrack"](index=0, playlist=playlist)
    plt1 = factories["playlists.PlaylistTrack"](index=1, playlist=playlist)
    url = reverse("api:v1:playlists-move", kwargs={"uuid": playlist.uuid})

    response = logged_in_api_client.post(url, {"from": 1, "to": 0})

    assert response.status_code == 204

    plt0.refresh_from_db()
    plt1.refresh_from_db()
    assert plt0.index == 1
    assert plt1.index == 0
