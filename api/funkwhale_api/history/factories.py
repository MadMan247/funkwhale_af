import factory
from django.conf import settings

from funkwhale_api.factories import NoUpdateOnCreate, registry
from funkwhale_api.federation import models
from funkwhale_api.federation.factories import ActorFactory
from funkwhale_api.music import factories


@registry.register
class ListeningFactory(NoUpdateOnCreate, factory.django.DjangoModelFactory):
    actor = factory.SubFactory(ActorFactory)
    track = factory.SubFactory(factories.TrackFactory)
    fid = factory.Faker("federation_url")
    uuid = factory.Faker("uuid4")
    privacy_level = "everyone"

    class Meta:
        model = "history.Listening"

    @factory.post_generation
    def local(self, create, extracted, **kwargs):
        if not extracted and not kwargs:
            return
        domain = models.Domain.objects.get_or_create(name=settings.FEDERATION_HOSTNAME)[
            0
        ]
        self.fid = f"https://{domain}/federation/music/favorite/{self.uuid}"
        self.save(update_fields=["fid"])


@registry.register
class ListeningsScanFactory(NoUpdateOnCreate, factory.django.DjangoModelFactory):
    actor = factory.SubFactory(ActorFactory)
    target = factory.SubFactory(ActorFactory)

    class Meta:
        model = "history.ListeningsScan"
