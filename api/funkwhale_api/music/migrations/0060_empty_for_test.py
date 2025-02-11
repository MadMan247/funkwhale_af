from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("music", "0059_remove_album_artist_remove_track_artist_artistcredit_and_more"),
        ("playlists", "0007_alter_playlist_actor_alter_playlisttrack_uuid_and_more"),
    ]

    operations = []
