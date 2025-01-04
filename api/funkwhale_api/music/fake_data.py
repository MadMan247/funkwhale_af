"""
Populates the database with fake data
"""

import logging
import random

from funkwhale_api.cli import users
from funkwhale_api.federation import factories as federation_factories
from funkwhale_api.history import factories as history_factories
from funkwhale_api.music import factories as music_factories
from funkwhale_api.playlists import factories as playlist_factories
from funkwhale_api.users import models, serializers

logger = logging.getLogger(__name__)


def create_data(count=2, super_user_name=None):
    super_user = None
    if super_user_name:
        try:
            super_user = users.handler_create_user(
                username=str(super_user_name),
                password="funkwhale",
                email=f"{super_user_name}eat@the.rich",
                is_superuser=True,
                is_staff=True,
                upload_quota=None,
            )
        except serializers.ValidationError as e:
            for field, errors in e.detail.items():
                if (
                    "A user with that username already exists"
                    or "A user is already registered with this e-mail address"
                    in errors[0]
                ):
                    print(
                        f"Superuser {super_user_name} already in db. Skipping fake-data creation"
                    )
                    super_user = models.User.objects.get(username=super_user_name)
                    continue
                else:
                    raise e
        print(f"Superuser with username {super_user_name} and password `funkwhale`")

        library = federation_factories.MusicLibraryFactory(
            actor=(
                super_user.actor if super_user else federation_factories.ActorFactory()
            ),
            local=True,
        )
        uploads = music_factories.UploadFactory.create_batch(
            size=random.randint(3, 18),
            playable=True,
            library=library,
            local=True,
        )
        for upload in uploads:
            history_factories.ListeningFactory(
                track=upload.track, actor=upload.library.actor
            )
        print("Created fid", upload.track.fid)

        playlist = playlist_factories.PlaylistFactory(
            name="playlist test public",
            privacy_level="everyone",
            actor=(
                super_user.actor if super_user else federation_factories.ActorFactory()
            ),
        )
        playlist_factories.PlaylistTrackFactory(playlist=playlist, track=upload.track)
        federation_factories.LibraryFollowFactory.create_batch(
            size=random.randint(3, 18), actor=super_user.actor
        )


if __name__ == "__main__":
    create_data()
