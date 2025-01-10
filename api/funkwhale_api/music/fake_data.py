"""
Populates the database with fake data
"""

import logging
import random

from funkwhale_api.audio import factories as audio_factories
from funkwhale_api.cli import users
from funkwhale_api.favorites import factories as favorites_factories
from funkwhale_api.federation import factories as federation_factories
from funkwhale_api.history import factories as history_factories
from funkwhale_api.music import factories as music_factories
from funkwhale_api.playlists import factories as playlist_factories
from funkwhale_api.users import models, serializers

logger = logging.getLogger(__name__)


def create_data(super_user_name=None):
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
                        f"Superuser {super_user_name} already in db. Skipping superuser creation"
                    )
                    super_user = models.User.objects.get(username=super_user_name)
                    continue
                else:
                    raise e
        print(f"Superuser with username {super_user_name} and password `funkwhale`")

    library = federation_factories.MusicLibraryFactory(
        actor=(super_user.actor if super_user else federation_factories.ActorFactory()),
        local=True,
    )
    uploads = music_factories.UploadFactory.create_batch(
        size=random.randint(3, 18),
        playable=True,
        library=library,
        local=True,
    )
    for upload in uploads[:2]:
        history_factories.ListeningFactory(
            track=upload.track, actor=upload.library.actor
        )
        favorites_factories.TrackFavorite(
            track=upload.track, actor=upload.library.actor
        )

    print("Created fid", upload.track.fid)

    playlist = playlist_factories.PlaylistFactory(
        name="playlist test public",
        privacy_level="everyone",
        actor=(super_user.actor if super_user else federation_factories.ActorFactory()),
    )
    playlist_factories.PlaylistTrackFactory(playlist=playlist, track=upload.track)
    federation_factories.LibraryFollowFactory.create_batch(
        size=random.randint(3, 18), actor=super_user.actor
    )

    # my podcast
    my_podcast_library = federation_factories.MusicLibraryFactory(
        actor=(super_user.actor if super_user else federation_factories.ActorFactory()),
        local=True,
    )
    my_podcast_channel = audio_factories.ChannelFactory(
        library=my_podcast_library,
        attributed_to=super_user.actor,
        artist__content_category="podcast",
    )
    my_podcast_channel_serie = music_factories.AlbumFactory(
        artist_credit__artist=my_podcast_channel.artist
    )
    music_factories.TrackFactory.create_batch(
        size=random.randint(3, 6),
        artist_credit__artist=my_podcast_channel.artist,
        album=my_podcast_channel_serie,
    )

    # podcast
    podcast_channel = audio_factories.ChannelFactory(artist__content_category="podcast")
    podcast_channel_serie = music_factories.AlbumFactory(
        artist_credit__artist=podcast_channel.artist
    )
    music_factories.TrackFactory.create_batch(
        size=random.randint(3, 6),
        artist_credit__artist=podcast_channel.artist,
        album=podcast_channel_serie,
    )

    audio_factories.SubscriptionFactory(
        approved=True, target=podcast_channel.actor, actor=super_user.actor
    )

    # my artist channel
    my_artist_library = federation_factories.MusicLibraryFactory(
        actor=(super_user.actor if super_user else federation_factories.ActorFactory()),
        local=True,
    )
    my_artist_channel = audio_factories.ChannelFactory(
        library=my_artist_library,
        attributed_to=super_user.actor,
        artist__content_category="music",
    )
    my_artist_channel_serie = music_factories.AlbumFactory(
        artist_credit__artist=my_artist_channel.artist
    )
    music_factories.TrackFactory.create_batch(
        size=random.randint(3, 6),
        artist_credit__artist=my_artist_channel.artist,
        album=my_artist_channel_serie,
    )

    # artist channel
    artist_channel = audio_factories.ChannelFactory(artist__content_category="artist")
    artist_channel_serie = music_factories.AlbumFactory(
        artist_credit__artist=artist_channel.artist
    )
    music_factories.TrackFactory.create_batch(
        size=random.randint(3, 6),
        artist_credit__artist=artist_channel.artist,
        album=artist_channel_serie,
    )

    audio_factories.SubscriptionFactory(
        approved=True, target=artist_channel.actor, actor=super_user.actor
    )


if __name__ == "__main__":
    create_data()
