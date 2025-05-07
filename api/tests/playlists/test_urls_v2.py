import json

from defusedxml import ElementTree as etree
from django.shortcuts import resolve_url
from django.urls import reverse


def test_can_get_playlist_list(factories, logged_in_api_client):
    logged_in_api_client.user.create_actor()
    factories["playlists.Playlist"].create_batch(5)
    url = reverse("api:v2:playlists-list")
    headers = {"Content-Type": "application/json"}
    response = logged_in_api_client.get(url, headers=headers)
    data = json.loads(response.content)

    assert response.status_code == 200
    assert data["count"] == 5


def test_can_get_playlists_octet_stream(factories, logged_in_api_client):
    logged_in_api_client.user.create_actor()
    pl = factories["playlists.Playlist"]()
    factories["playlists.PlaylistTrack"](playlist=pl)
    factories["playlists.PlaylistTrack"](playlist=pl)
    factories["playlists.PlaylistTrack"](playlist=pl)

    url = reverse("api:v2:playlists-detail", kwargs={"uuid": pl.uuid})
    headers = {"Accept": "application/octet-stream"}
    response = logged_in_api_client.get(url, headers=headers)
    el = etree.fromstring(response.content)
    ns = {"xspf": "http://xspf.org/ns/0/"}
    assert response.status_code == 200
    assert el.findtext("./xspf:title", namespaces=ns) == pl.name


def test_can_get_playlists_json(factories, logged_in_api_client):
    logged_in_api_client.user.create_actor()
    pl = factories["playlists.Playlist"]()
    url = reverse("api:v2:playlists-detail", kwargs={"uuid": pl.uuid})
    response = logged_in_api_client.get(url, format="json")
    assert response.status_code == 200
    assert response.data["name"] == pl.name


def test_can_get_user_playlists_list(factories, logged_in_api_client):
    logged_in_api_client.user.create_actor()
    user = factories["users.User"](with_actor=True)
    factories["playlists.Playlist"](actor=user.actor)

    url = reverse("api:v2:playlists-list")
    url = resolve_url(url) + "?user=me"
    response = logged_in_api_client.get(url)
    data = json.loads(response.content.decode("utf-8"))

    assert response.status_code == 200
    assert data["count"] == 1


def test_can_post_user_playlists(logged_in_api_client):
    logged_in_api_client.user.create_actor()
    playlist = {"name": "Les chiennes de l'hexagone", "privacy_level": "me"}
    url = reverse("api:v2:playlists-list")

    response = logged_in_api_client.post(url, playlist, format="json")
    data = json.loads(response.content.decode("utf-8"))
    assert response.status_code == 201
    assert data["name"] == "Les chiennes de l'hexagone"
    assert data["privacy_level"] == "me"


def test_can_post_playlists_octet_stream(factories, logged_in_api_client):
    logged_in_api_client.user.create_actor()
    artist = factories["music.Artist"](name="Davinhor")
    album = factories["music.Album"](
        title="Racisme en pls", artist_credit__artist=artist
    )
    factories["music.Track"](
        title="Opinel 12", artist_credit__artist=artist, album=album
    )
    url = reverse("api:v2:playlists-list")
    data = open("./tests/playlists/test.xspf", "rb").read()
    response = logged_in_api_client.post(url, data=data, format="xspf")
    data = json.loads(response.content)
    assert response.status_code == 201
    assert data["name"] == "Test"


def test_can_post_playlists_octet_stream_invalid_track(factories, logged_in_api_client):
    logged_in_api_client.user.create_actor()
    url = reverse("api:v2:playlists-list")
    data = open("./tests/playlists/test.xspf", "rb").read()
    response = logged_in_api_client.post(url, data=data, format="xspf")
    data = json.loads(response.content)
    assert response.status_code == 201
    assert data["name"] == "Test"


def test_can_patch_playlists_octet_stream(factories, logged_in_api_client):
    logged_in_api_client.user.create_actor()
    pl = factories["playlists.Playlist"](actor=logged_in_api_client.user.actor)
    artist = factories["music.Artist"](name="Davinhor")
    album = factories["music.Album"](
        title="Racisme en pls", artist_credit__artist=artist
    )
    track = factories["music.Track"](
        title="Opinel 12", artist_credit__artist=artist, album=album
    )
    url = reverse("api:v2:playlists-detail", kwargs={"uuid": pl.uuid})
    data = open("./tests/playlists/test.xspf", "rb").read()
    response = logged_in_api_client.patch(url, data=data, format="xspf")
    pl.refresh_from_db()
    assert response.status_code == 201
    assert pl.name == "Test"
    assert pl.playlist_tracks.all()[0].track.title == track.title


def test_can_get_playlists_track(factories, logged_in_api_client):
    logged_in_api_client.user.create_actor()
    pl = factories["playlists.Playlist"]()
    plt = factories["playlists.PlaylistTrack"](playlist=pl)
    url = reverse("api:v2:playlists-tracks", kwargs={"uuid": pl.uuid})
    response = logged_in_api_client.get(url)
    data = json.loads(response.content.decode("utf-8"))
    assert response.status_code == 200
    assert data["count"] == 1
    assert data["results"][0]["track"]["title"] == plt.track.title


def test_can_get_playlists_releases(factories, logged_in_api_client):
    logged_in_api_client.user.create_actor()
    playlist = factories["playlists.Playlist"]()
    plt = factories["playlists.PlaylistTrack"](playlist=playlist)
    url = reverse("api:v2:playlists-albums", kwargs={"uuid": playlist.uuid})
    response = logged_in_api_client.get(url)
    data = json.loads(response.content)
    assert response.status_code == 200
    assert data[0]["title"] == plt.track.album.title


def test_can_get_playlists_artists(factories, logged_in_api_client):
    logged_in_api_client.user.create_actor()
    playlist = factories["playlists.Playlist"]()
    plt = factories["playlists.PlaylistTrack"](playlist=playlist)
    url = reverse("api:v2:playlists-artists", kwargs={"uuid": playlist.uuid})
    response = logged_in_api_client.get(url)
    data = json.loads(response.content)
    assert response.status_code == 200
    assert data[0]["name"] == plt.track.get_artist_credit_string
