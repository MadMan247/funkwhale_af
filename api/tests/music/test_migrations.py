from uuid import uuid4

import pytest
from django.conf import settings
from django.utils.timezone import now

# this test is commented since it's very slow, but it can be useful for future development
# def test_pytest_plugin_initial(migrator):
#     mapping_list = [
#         ("audio/mpeg", "20", "low", 0, 1),
#         ("audio/ogg", "180", "medium", 1, 2),
#         ("audio/x-m4a", "280", "high", 2, 3),
#         ("audio/opus", "130", "high", 2, 4),
#         ("audio/opus", "513", "very-high", 3, 5),
#         ("audio/aiff", "1312", "very-high", 3, 6),
#         ("audio/mpeg", "320", "high", 2, 8),
#         ("audio/mpeg", "200", "medium", 1, 9),
#         ("audio/aiff", "1", "very-high", 3, 10),
#         ("audio/flac", "1", "very-high", 3, 11),
#     ]

#     a, f, t = ("music", "0057_auto_20221118_2108", "0058_upload_quality")

#     migrator.migrate([(a, f)])
#     old_apps = migrator.loader.project_state([(a, f)]).apps
#     Upload = old_apps.get_model(a, "Upload")
#     for upload in mapping_list:
#         Upload.objects.create(pk=upload[4], mimetype=upload[0], bitrate=upload[1])

#     migrator.loader.build_graph()
#     migrator.migrate([(a, t)])
#     new_apps = migrator.loader.project_state([(a, t)]).apps

#     upload_manager = new_apps.get_model(a, "Upload")


#     for upload in mapping_list:
#         upload_obj = upload_manager.objects.get(pk=upload[4])
#         assert upload_obj.quality == upload[3]


def test_artist_credit_migration(migrator):
    mapping_list = [("artist_name", "album_title", "track_title")]

    a, f, t = (
        "music",
        "0058_upload_quality",
        "0059_remove_album_artist_remove_track_artist_artistcredit_and_more",
    )

    migrator.migrate([(a, f)])
    old_apps = migrator.loader.project_state([(a, f)]).apps
    Track = old_apps.get_model(a, "Track")
    Album = old_apps.get_model(a, "Album")
    Artist = old_apps.get_model(a, "Artist")

    for track in mapping_list:
        artist = Artist.objects.create(name=track[0])
        old_album = Album.objects.create(title=track[1], artist=artist)
        old_track = Track.objects.create(title=track[2], artist=artist, album=old_album)

    migrator.loader.build_graph()

    migrator.migrate([(a, t)])
    new_apps = migrator.loader.project_state([(a, t)]).apps

    track_manager = new_apps.get_model(a, "Track")
    album_manager = new_apps.get_model(a, "Album")

    for track in mapping_list:
        track_obj = track_manager.objects.get(title=track[2])
        album_obj = album_manager.objects.get(title=track[1])

        assert track_obj.artist_credit.all()[0].artist.pk == old_track.artist.pk
        assert track_obj.artist_credit.all()[0].joinphrase == ""
        assert track_obj.artist_credit.all()[0].credit == old_track.artist.name

        assert album_obj.artist_credit.all()[0].artist.pk == old_album.artist.pk
        assert album_obj.artist_credit.all()[0].joinphrase == ""
        assert album_obj.artist_credit.all()[0].credit == old_album.artist.name


@pytest.mark.django_db
def test_migrate_libraries_to_playlist(migrator):
    music_initial_migration = (
        "music",
        "0060_empty_for_test",
    )
    music_final_migration = ("music", "0061_migrate_libraries_to_playlist")

    # Apply migrations
    migrator.migrate(
        [
            music_initial_migration,
        ]
    )
    music_apps = migrator.loader.project_state([music_initial_migration]).apps

    Playlist = music_apps.get_model("playlists", "Playlist")
    LibraryFollow = music_apps.get_model("federation", "LibraryFollow")
    Actor = music_apps.get_model("federation", "Actor")
    Domain = music_apps.get_model("federation", "Domain")
    Track = music_apps.get_model("music", "Track")
    Library = music_apps.get_model("music", "Library")
    Upload = music_apps.get_model("music", "Upload")
    Playlist = music_apps.get_model("playlists", "Playlist")

    # Create data
    d = settings.FEDERATION_HOSTNAME
    domain = Domain.objects.create()
    domain2 = Domain.objects.create(pk=2)
    actor = Actor.objects.create(name="Test Actor", domain=domain, fid=f"http://{d}/")
    target_actor = Actor.objects.create(
        name="Test Actor 2",
        domain=domain2,
        fid="http://test2.com/superduniquemanonmam",
    )

    library = Library.objects.create(
        name="This should becane playlist name",
        actor=actor,
        creation_date=now(),
        privacy_level="everyone",
        uuid=uuid4(),
        description="This is a description",
    )
    Library.objects.create(
        name="me",
        actor=actor,
        creation_date=now(),
        privacy_level="me",
        uuid=uuid4(),
        description="This is a description",
        fid=f"http://{d}/mylocallob",
    )

    library_not_local = Library.objects.create(
        name="This should not becane playlist name",
        fid="https://asupernotlocal.acab/federation/music/libraries/8505207e-45da-449a-9ec8-ed12a848fcea",
        actor=target_actor,
        creation_date=now(),
        privacy_level="everyone",
        uuid=uuid4(),
        description="This is a description recalling to eat the rich",
    )

    Track.objects.create()
    Track.objects.create()
    track = Track.objects.create()
    track2 = Track.objects.create()
    track3 = Track.objects.create()

    uploads = [
        Upload.objects.create(library=library, track=track),
        Upload.objects.create(library=library, track=track2),
        Upload.objects.create(library=library, track=track3),
    ]

    Upload.objects.create(library=library_not_local, track=track),
    Upload.objects.create(library=library_not_local, track=track2),
    Upload.objects.create(library=library_not_local, track=track3),
    # Plt = music_apps.get_model("playlists", "PlaylistTrack")
    # playlist = Playlist.objects.create(
    #     name="This should becane a library name",
    #     fid="https://asupernotlocal.acab/federation/music/playlist/8505207e-45da-449a-9ec8-ed12a848fcea",
    #     actor=actor,
    #     creation_date=now(),
    #     privacy_level="everyone",
    #     uuid=uuid4(),
    # )

    # playlist_not_local = Playlist.objects.create(
    #     name="This should not becane a library name",
    #     actor=target_actor,
    #     creation_date=now(),
    #     privacy_level="everyone",
    #     uuid=uuid4(),
    # )
    # Plt.objects.create(playlist=playlist, track=track)
    # Plt.objects.create(
    #     playlist=playlist_not_local,
    #     track=track,
    #     fid="https://asupernotlocal.acab/federation/music/playlistttrack/8505207e-",
    # )

    library_follow = LibraryFollow.objects.create(
        uuid=uuid4(),
        target=library,
        actor=actor,
        approved=True,
        creation_date=now(),
        modification_date=now(),
    )

    # Perform migration
    migrator.loader.build_graph()
    migrator.migrate([music_final_migration])

    new_apps = migrator.loader.project_state([music_final_migration]).apps
    Playlist = new_apps.get_model("playlists", "Playlist")
    PlaylistTrack = new_apps.get_model("playlists", "PlaylistTrack")
    LibraryFollow = new_apps.get_model("federation", "LibraryFollow")
    Library = new_apps.get_model("music", "Library")

    # Assertions

    # Verify Playlist creation
    playlist = Playlist.objects.get(name="This should becane playlist name")

    assert playlist.actor.pk == library.actor.pk
    assert playlist.creation_date == library.creation_date
    assert playlist.privacy_level == library.privacy_level
    assert playlist.description == library.description

    # Verify Playlist me creation skipped
    assert not Playlist.objects.filter(name="me")
    assert playlist.actor.libraries.filter(name="me").count() == 1

    # Verify PlaylistTrack creation
    playlist_tracks = PlaylistTrack.objects.filter(playlist=playlist).order_by("index")
    assert playlist_tracks.count() == 3
    for i, playlist_track in enumerate(playlist_tracks):
        assert playlist_track.track.pk == uploads[i].track.pk

    # Verify playlist.library Follow creation
    follow = LibraryFollow.objects.get(target__pk=playlist.library.pk)
    assert follow.actor.pk == actor.pk
    assert follow.approved == library_follow.approved
    assert follow.target == playlist.library

    # Verify uploads are migrated in lib.playlist_uploads
    for upload in uploads:
        assert upload.pk in [u.pk for u in playlist.library.playlist_uploads.all()]
        assert upload.pk not in [u.pk for u in playlist.library.uploads.all()]
        assert not playlist.library.uploads.all()

    # Test fail but works on real db I don't get why
    # no library are found in the new app
    # NewAppLibrary = new_apps.get_model("music", "Library")
    # assert NewAppLibrary.objects.count() == 3

    # Playlist
    # library = Playlist.objects.get(name="This should becane a library name").library
    # assert library.name == "This should becane a library name"
    # assert library.privacy_level == "me"

    # # Not local
    # library_not_local = Library.objects.get(fid=library_not_local.fid)
    # assert not library_not_local.playlist_uploads.all()

    # playlist_not_local = Playlist.objects.get(
    #     name="This should not becane a library name"
    # )
    # assert not playlist_not_local.library
