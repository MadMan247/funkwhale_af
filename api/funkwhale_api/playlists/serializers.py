import logging

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from funkwhale_api.federation.serializers import APIActorSerializer
from funkwhale_api.music import tasks
from funkwhale_api.music.models import Album, Artist, Track
from funkwhale_api.music.serializers import TrackSerializer

from . import models

logger = logging.getLogger(__name__)


class PlaylistTrackSerializer(serializers.ModelSerializer):
    # track = TrackSerializer()
    track = serializers.SerializerMethodField()

    class Meta:
        model = models.PlaylistTrack
        fields = ("track", "index", "creation_date")

    def get_track(self, o):
        track = o._prefetched_track if hasattr(o, "_prefetched_track") else o.track
        return TrackSerializer(track).data


class PlaylistSerializer(serializers.ModelSerializer):
    tracks_count = serializers.SerializerMethodField(read_only=True)
    duration = serializers.SerializerMethodField(read_only=True)
    album_covers = serializers.SerializerMethodField(read_only=True)
    is_playable = serializers.SerializerMethodField()
    actor = APIActorSerializer(read_only=True)

    class Meta:
        model = models.Playlist
        fields = (
            "id",
            "name",
            "actor",
            "modification_date",
            "creation_date",
            "privacy_level",
            "tracks_count",
            "album_covers",
            "duration",
            "is_playable",
            "actor",
        )
        read_only_fields = ["id", "modification_date", "creation_date"]

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_playable(self, obj):
        return getattr(obj, "is_playable_by_actor", False)

    def get_tracks_count(self, obj) -> int:
        return getattr(obj, "tracks_count", obj.playlist_tracks.count())

    def get_duration(self, obj) -> int:
        try:
            return obj.duration
        except AttributeError:
            # no annotation?
            return 0

    @extend_schema_field({"type": "array", "items": {"type": "string"}})
    def get_album_covers(self, obj):
        try:
            plts = obj.plts_for_cover
        except AttributeError:
            return []

        excluded_artists = []
        try:
            user = self.context["request"].user
        except (KeyError, AttributeError):
            user = None
        if user and user.is_authenticated:
            excluded_artists = list(
                user.content_filters.values_list("target_artist", flat=True)
            )

        covers = []
        max_covers = 5
        for plt in plts:
            if [
                ac.artist.pk for ac in plt.track.album.artist_credit.all()
            ] in excluded_artists:
                continue
            url = plt.track.album.attachment_cover.download_url_medium_square_crop
            if url in covers:
                continue
            covers.append(url)
            if len(covers) >= max_covers:
                break

        full_urls = []
        for url in covers:
            if "request" in self.context:
                url = self.context["request"].build_absolute_uri(url)
            full_urls.append(url)
        return full_urls


class PlaylistAddManySerializer(serializers.Serializer):
    tracks = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Track.objects.for_nested_serialization()
    )
    allow_duplicates = serializers.BooleanField(required=False)

    class Meta:
        fields = "allow_duplicates"


class XspfTrackSerializer(serializers.Serializer):
    location = serializers.CharField(allow_blank=True, required=False)
    title = serializers.CharField()
    creator = serializers.CharField()
    album = serializers.CharField(allow_blank=True, required=False)
    duration = serializers.CharField(allow_blank=True, required=False)

    def validate(self, data):
        title = data["title"]
        album = data.get("album", None)
        acs_tuples = tasks.parse_credits(data["creator"], "", 0)
        try:
            artist_id = Artist.objects.get(name=acs_tuples[0][0])
        except ObjectDoesNotExist:
            raise ValidationError("Couldn't find artist in the database")
        if album:
            try:
                album_id = Album.objects.get(title=album)
                fw_track = Track.objects.get(
                    title=title, artist_credit__artist=artist_id, album=album_id
                )
            except ObjectDoesNotExist:
                pass
        try:
            fw_track = Track.objects.get(title=title, artist_credit__artist=artist_id)
        except ObjectDoesNotExist as e:
            raise ValidationError(f"Couldn't find track in the database : {e!r}")

        super().validate(data)
        return fw_track


class XspfSerializer(serializers.Serializer):
    title = serializers.CharField()
    creator = serializers.CharField(allow_blank=True, required=False)
    creation_date = serializers.DateTimeField(required=False)
    version = serializers.IntegerField(required=False)
    tracks = XspfTrackSerializer(many=True, required=False)

    def create(self, validated_data):
        pl = models.Playlist.objects.create(
            name=validated_data["title"],
            privacy_level="private",
            actor=validated_data["request"].user.actor,
        )
        pl.insert_many(validated_data["tracks"])

        return pl

    def update(self, instance, validated_data):
        instance.name = validated_data["title"]
        instance.playlist_tracks.all().delete()
        instance.insert_many(validated_data["tracks"])
        instance.save()
        return instance
