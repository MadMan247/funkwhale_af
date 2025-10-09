import django.db.models.deletion
from django.db import migrations, models, transaction
from funkwhale_api.federation import utils as federation_utils
from django.urls import reverse
import uuid
from django.conf import settings


def add_uploads_to_pl_library(playlist, library):
    for plt in playlist.playlist_tracks.all():
        for upload in plt.track.uploads.filter(library__actor=playlist.actor):
            library.uploads.add(upload)


@transaction.atomic
def create_playlist_libraries(apps, schema_editor):
    Playlist = apps.get_model("playlists", "Playlist")
    Library = apps.get_model("music", "Library")
    Actor = apps.get_model("federation", "Actor")
    playlist_with_lib_count = 0
    playlists = []
    for playlist in Playlist.objects.all():
        if not federation_utils.is_local(playlist.actor.fid):
            continue
        library = playlist.library
        if not library:
            try:
                # we don't want to get_or_create in case it's a channel lib
                library = Library.objects.create(
                    name="playlist_" + playlist.name,
                    privacy_level="me",
                    actor=playlist.actor,
                    uuid=(new_uuid := uuid.uuid4()),
                    fid=federation_utils.full_url(
                        reverse(
                            "federation:music:libraries-detail",
                            kwargs={"uuid": new_uuid},
                        )
                    ),
                )
                library.save()
                playlist.library = library
                playlists.append(playlist)
                with transaction.atomic():
                    add_uploads_to_pl_library(playlist, library)
            except Exception as e:
                print(
                    f"An error occurred during playlist.library creation, raising since we want\
                      to enforce one lib per playlist"
                )
                raise e
        Playlist.objects.bulk_update(playlists, fields=["library"], batch_size=5000)
        playlist_with_lib_count = playlist_with_lib_count + 1
        local_actors = Actor.objects.filter(domain_id=settings.FEDERATION_HOSTNAME)

        if (
            Library.objects.filter(
                playlist__isnull=False, actor__in=local_actors
            ).count()
            != playlist_with_lib_count
        ):
            raise Exception(
                "Should have the same amount of local playlist and libraries with playlist"
            )


class Migration(migrations.Migration):
    dependencies = [
        ("playlists", "0008_playlist_library_drop"),
    ]

    operations = [
        migrations.AddField(
            model_name="playlist",
            name="library",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="playlist",
                to="music.library",
            ),
        ),
        migrations.RunPython(
            create_playlist_libraries, reverse_code=migrations.RunPython.noop
        ),
    ]
