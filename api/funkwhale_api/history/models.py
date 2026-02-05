import uuid

from django.db import models
from django.urls import reverse
from django.utils import timezone

from funkwhale_api.common import fields
from funkwhale_api.common import models as common_models
from funkwhale_api.federation import models as federation_models
from funkwhale_api.federation import utils as federation_utils
from funkwhale_api.music.models import Track


class ListeningQuerySet(models.QuerySet, common_models.LocalFromFidQuerySet):
    pass


class Listening(federation_models.FederationMixin):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    creation_date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    track = models.ForeignKey(
        Track, related_name="listenings", on_delete=models.CASCADE
    )
    actor = models.ForeignKey(
        "federation.Actor",
        related_name="listenings",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    privacy_level = fields.get_privacy_field()
    session_key = models.CharField(max_length=100, null=True, blank=True)
    source = models.CharField(max_length=100, null=True, blank=True)
    federation_namespace = "listenings"
    objects = ListeningQuerySet.as_manager()

    class Meta:
        ordering = ("-creation_date",)

    def get_activity_url(self):
        return f"{self.actor.get_absolute_url()}/listenings/tracks/{self.pk}"

    def get_absolute_url(self):
        return f"/library/tracks/{self.track.pk}"

    def get_federation_id(self):
        if self.fid:
            return self.fid

        return federation_utils.full_url(
            reverse(
                f"federation:music:{self.federation_namespace}-detail",
                kwargs={"uuid": self.uuid},
            )
        )

    def save(self, **kwargs):
        if not self.pk and not self.fid:
            self.fid = self.get_federation_id()
        if hasattr(self.actor, "user"):
            self.privacy_level = self.actor.user.privacy_level
        return super().save(**kwargs)


class ListeningsScan(models.Model):
    actor = models.ForeignKey(
        "federation.Actor", null=True, blank=True, on_delete=models.CASCADE
    )
    target = models.ForeignKey(
        federation_models.Actor,
        related_name="listening_scans",
        on_delete=models.CASCADE,
    )
    total_files = models.PositiveIntegerField(default=0)
    processed_files = models.PositiveIntegerField(default=0)
    errored_files = models.PositiveIntegerField(default=0)
    status = models.CharField(default="pending", max_length=25)
    creation_date = models.DateTimeField(default=timezone.now)
    modification_date = models.DateTimeField(null=True, blank=True)
