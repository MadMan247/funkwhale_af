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
