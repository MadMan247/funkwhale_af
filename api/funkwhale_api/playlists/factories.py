import factory
from django.conf import settings

from funkwhale_api.factories import NoUpdateOnCreate, registry
from funkwhale_api.federation import models
from funkwhale_api.federation.factories import ActorFactory, MusicLibraryFactory
from funkwhale_api.music.factories import TrackFactory


@registry.register
class PlaylistFactory(NoUpdateOnCreate, factory.django.DjangoModelFactory):
    name = factory.Faker("name")
    actor = factory.SubFactory(ActorFactory)
    fid = factory.Faker("federation_url")
    uuid = factory.Faker("uuid4")
    library = factory.SubFactory(MusicLibraryFactory)

    class Meta:
        model = "playlists.Playlist"

    @factory.post_generation
    def local(self, create, extracted, **kwargs):
        if not extracted and not kwargs:
            return
        domain = models.Domain.objects.get_or_create(name=settings.FEDERATION_HOSTNAME)[
            0
        ]
        self.fid = f"https://{domain}/federation/music/playlists/{self.uuid}"
        self.save(update_fields=["fid"])


@registry.register
class PlaylistTrackFactory(NoUpdateOnCreate, factory.django.DjangoModelFactory):
    playlist = factory.SubFactory(PlaylistFactory)
    track = factory.SubFactory(TrackFactory)
    fid = factory.Faker("federation_url")
    uuid = factory.Faker("uuid4")

    class Meta:
        model = "playlists.PlaylistTrack"

    @factory.post_generation
    def local(self, create, extracted, **kwargs):
        if not extracted and not kwargs:
            return
        domain = models.Domain.objects.get_or_create(name=settings.FEDERATION_HOSTNAME)[
            0
        ]
        self.fid = f"https://{domain}/federation/music/playlists-tracks/{self.uuid}"
        self.save(update_fields=["fid"])


@registry.register
class PlaylistScanFactory(NoUpdateOnCreate, factory.django.DjangoModelFactory):
    playlist = factory.SubFactory(PlaylistFactory)
    actor = factory.SubFactory(ActorFactory)

    class Meta:
        model = "playlists.PlaylistScan"
