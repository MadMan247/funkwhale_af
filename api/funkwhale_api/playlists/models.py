import datetime
import uuid

from django.db import models, transaction
from django.db.models import Q
from django.db.models.expressions import OuterRef, Subquery
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from rest_framework import exceptions

from funkwhale_api.common import fields
from funkwhale_api.common import models as common_models
from funkwhale_api.common import preferences
from funkwhale_api.common import utils as common_utils
from funkwhale_api.federation import models as federation_models
from funkwhale_api.federation import utils as federation_utils
from funkwhale_api.music import models as music_models


class PlaylistQuerySet(models.QuerySet, common_models.LocalFromFidQuerySet):
    def with_tracks_count(self):
        return self.annotate(_tracks_count=models.Count("playlist_tracks"))

    def with_duration(self):
        subquery = Subquery(
            music_models.Upload.objects.filter(
                track_id=OuterRef("playlist_tracks__track__id")
            )
            .order_by("id")
            .values("id")[:1]
        )
        return self.annotate(
            duration=models.Sum(
                "playlist_tracks__track__uploads__duration",
                filter=Q(playlist_tracks__track__uploads=subquery),
            )
        )

    def with_covers(self):
        album_prefetch = models.Prefetch(
            "album",
            queryset=music_models.Album.objects.select_related("attachment_cover"),
        )
        track_prefetch = models.Prefetch(
            "track",
            queryset=music_models.Track.objects.prefetch_related(album_prefetch).only(
                "id", "album_id"
            ),
        )

        plt_prefetch = models.Prefetch(
            "playlist_tracks",
            queryset=PlaylistTrack.objects.all()
            .exclude(track__album__attachment_cover=None)
            .order_by("index")
            .only("id", "playlist_id", "track_id")
            .prefetch_related(track_prefetch),
            to_attr="plts_for_cover",
        )
        return self.prefetch_related(plt_prefetch)

    def with_playable_plts(self, actor):
        return self.prefetch_related(
            models.Prefetch(
                "playlist_tracks",
                queryset=PlaylistTrack.objects.playable_by(actor),
                to_attr="playable_plts",
            )
        )

    def playable_by(self, actor, include=True):
        plts = PlaylistTrack.objects.playable_by(actor, include)
        if include:
            return self.filter(playlist_tracks__in=plts).distinct()
        else:
            return self.exclude(playlist_tracks__in=plts).distinct()


class Playlist(federation_models.FederationMixin):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=100)
    actor = models.ForeignKey(
        "federation.Actor", related_name="playlists", on_delete=models.CASCADE
    )
    creation_date = models.DateTimeField(default=timezone.now)
    modification_date = models.DateTimeField(auto_now=True)
    privacy_level = fields.get_privacy_field()
    description = models.TextField(max_length=5000, null=True, blank=True)
    objects = PlaylistQuerySet.as_manager()
    federation_namespace = "playlists"
    library = models.OneToOneField(
        "music.Library",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="playlist",
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/library/playlists/{self.uuid}"

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

        if not self.pk and not self.library_id:
            self.library = music_models.Library.objects.create(
                actor=self.actor,
                name="playlist_" + self.name,
                privacy_level="me",
                uuid=(new_uuid := uuid.uuid4()),
                fid=federation_utils.full_url(
                    reverse(
                        "federation:music:libraries-detail", kwargs={"uuid": new_uuid}
                    ),
                ),
            )

        return super().save(**kwargs)

    @transaction.atomic
    def insert(self, plt, index=None, allow_duplicates=True):
        """
        Given a PlaylistTrack, insert it at the correct index in the playlist,
        and update other tracks index if necessary.
        """
        old_index = plt.index
        move = old_index is not None
        if index is not None and index == old_index:
            # moving at same position, just skip
            return index

        existing = self.playlist_tracks.select_for_update()
        if move:
            existing = existing.exclude(pk=plt.pk)
        total = existing.filter(index__isnull=False).count()

        if index is None:
            # we simply increment the last track index by 1
            index = total

        if index > total:
            raise exceptions.ValidationError("Index is not continuous")

        if index < 0:
            raise exceptions.ValidationError("Index must be zero or positive")

        if not allow_duplicates:
            existing_without_current_plt = existing.exclude(pk=plt.pk)
            self._check_duplicate_add(existing_without_current_plt, [plt.track])

        if move:
            # we remove the index temporarily, to avoid integrity errors
            plt.index = None
            plt.save(update_fields=["index"])
            if index > old_index:
                # new index is higher than current, we decrement previous tracks
                to_update = existing.filter(index__gt=old_index, index__lte=index)
                to_update.update(index=models.F("index") - 1)
            if index < old_index:
                # new index is lower than current, we increment next tracks
                to_update = existing.filter(index__lt=old_index, index__gte=index)
                to_update.update(index=models.F("index") + 1)
        else:
            to_update = existing.filter(index__gte=index)
            to_update.update(index=models.F("index") + 1)

        plt.index = index
        plt.save(update_fields=["index"])
        self.save(update_fields=["modification_date"])
        return index

    @transaction.atomic
    def remove(self, index):
        existing = self.playlist_tracks.select_for_update()
        self.save(update_fields=["modification_date"])
        to_update = existing.filter(index__gt=index)
        return to_update.update(index=models.F("index") - 1)

    @transaction.atomic
    def insert_many(self, tracks, allow_duplicates=True):
        existing = self.playlist_tracks.select_for_update()
        now = timezone.now()
        total = existing.filter(index__isnull=False).count()
        max_tracks = preferences.get("playlists__max_tracks")
        if existing.count() + len(tracks) > max_tracks:
            raise exceptions.ValidationError(
                f"Playlist would reach the maximum of {max_tracks} tracks"
            )

        if not allow_duplicates:
            self._check_duplicate_add(existing, tracks)

        self.save(update_fields=["modification_date"])
        start = total

        plts = [
            PlaylistTrack(
                creation_date=now,
                playlist=self,
                track=track,
                index=start + i,
                uuid=(new_uuid := uuid.uuid4()),
                fid=federation_utils.full_url(
                    reverse(
                        f"federation:music:{self.federation_namespace}-detail",
                        kwargs={"uuid": new_uuid},  # Use the newly generated UUID
                    )
                ),
            )
            for i, track in enumerate(tracks)
        ]
        return PlaylistTrack.objects.bulk_create(plts)

    def _check_duplicate_add(self, existing_playlist_tracks, tracks_to_add):
        track_ids = [t.pk for t in tracks_to_add]

        duplicates = existing_playlist_tracks.filter(
            track__pk__in=track_ids
        ).values_list("track__pk", flat=True)
        if duplicates:
            duplicate_tracks = [t for t in tracks_to_add if t.pk in duplicates]
            raise exceptions.ValidationError(
                {
                    "non_field_errors": [
                        {
                            "tracks": duplicate_tracks,
                            "playlist_name": self.name,
                            "code": "tracks_already_exist_in_playlist",
                        }
                    ]
                }
            )

    def schedule_scan(self, actor, force=False):
        """Update playlist tracks if playlist is a remote one. If it's a local playlist it send an update activity
        on the remote server which will trigger a scan"""

        latest_scan = (
            self.scans.exclude(status="errored").order_by("-creation_date").first()
        )
        delay_between_scans = datetime.timedelta(seconds=1)
        now = timezone.now()
        if (
            not force
            and latest_scan
            and latest_scan.creation_date + delay_between_scans > now
        ):
            return

        from . import tasks

        scan = self.scans.create(
            total_files=len(self.playlist_tracks.all()), actor=actor
        )

        if self.actor.is_local:
            from funkwhale_api.federation import routes

            routes.outbox.dispatch(
                {"type": "Update", "object": {"type": "Playlist"}},
                context={"playlist": self, "actor": self.actor},
            )
            scan.status = "finished"
            return scan
        else:
            common_utils.on_commit(
                tasks.start_playlist_scan.delay, playlist_scan_id=scan.pk
            )
            return scan


@receiver(post_delete, sender=Playlist)
def delete_playlist_library(sender, instance, **kwargs):
    if instance.library:
        instance.library.delete()


class PlaylistTrackQuerySet(models.QuerySet, common_models.LocalFromFidQuerySet):
    def for_nested_serialization(self, actor=None):
        tracks = music_models.Track.objects.with_playable_uploads(actor)
        tracks = tracks.prefetch_related(
            "artist_credit__artist",
            "album__artist_credit__artist",
            "album__attachment_cover",
            "attributed_to",
        )
        return self.prefetch_related(
            models.Prefetch("track", queryset=tracks, to_attr="_prefetched_track")
        )

    def annotate_playable_by_actor(self, actor):
        tracks = (
            music_models.Upload.objects.playable_by(actor)
            .filter(track__pk=models.OuterRef("track"))
            .order_by("id")
            .values("id")[:1]
        )
        subquery = models.Subquery(tracks)
        return self.annotate(is_playable_by_actor=subquery)

    def playable_by(self, actor, include=True):
        tracks = music_models.Track.objects.playable_by(actor)
        if include:
            return self.filter(track__pk__in=tracks).distinct()
        else:
            return self.exclude(track__pk__in=tracks).distinct()

    def by_index(self, index):
        plts = self.order_by("index").values_list("id", flat=True)
        try:
            plt_id = plts[index]
        except IndexError:
            raise PlaylistTrack.DoesNotExist

        return PlaylistTrack.objects.get(pk=plt_id)


class PlaylistTrack(federation_models.FederationMixin):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    track = models.ForeignKey(
        "music.Track", related_name="playlist_tracks", on_delete=models.CASCADE
    )
    index = models.PositiveIntegerField(null=True, blank=True)
    playlist = models.ForeignKey(
        Playlist, related_name="playlist_tracks", on_delete=models.CASCADE
    )
    creation_date = models.DateTimeField(default=timezone.now)

    objects = PlaylistTrackQuerySet.as_manager()
    federation_namespace = "playlist-tracks"

    class Meta:
        ordering = ("-playlist", "index")

    def delete(self, *args, **kwargs):
        playlist = self.playlist
        index = self.index
        update_indexes = kwargs.pop("update_indexes", False)
        r = super().delete(*args, **kwargs)
        if index is not None and update_indexes:
            playlist.remove(index)
        return r

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

        return super().save(**kwargs)

    def get_absolute_url(self):
        return f"/library/tracks/{self.track.pk}"


class PlaylistScan(models.Model):
    actor = models.ForeignKey(
        "federation.Actor", null=True, blank=True, on_delete=models.CASCADE
    )
    playlist = models.ForeignKey(
        Playlist, related_name="scans", on_delete=models.CASCADE
    )
    total_files = models.PositiveIntegerField(default=0)
    processed_files = models.PositiveIntegerField(default=0)
    errored_files = models.PositiveIntegerField(default=0)
    status = models.CharField(default="pending", max_length=25)
    creation_date = models.DateTimeField(default=timezone.now)
    modification_date = models.DateTimeField(null=True, blank=True)
