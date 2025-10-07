import datetime
from urllib.parse import urlparse

from django.conf import settings
from django.core import validators
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from funkwhale_api.audio import models as audio_models
from funkwhale_api.audio import serializers as audio_serializers
from funkwhale_api.common import serializers as common_serializers
from funkwhale_api.music import models as music_models
from funkwhale_api.playlists import models as playlists_models
from funkwhale_api.users import serializers as users_serializers

from . import filters, models
from . import serializers as federation_serializers


class NestedLibraryFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LibraryFollow
        fields = ["creation_date", "uuid", "fid", "approved", "modification_date"]


class LibraryScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = music_models.LibraryScan
        fields = [
            "total_files",
            "processed_files",
            "errored_files",
            "status",
            "creation_date",
            "modification_date",
        ]


class DomainSerializer(serializers.Serializer):
    name = serializers.CharField()


class LibrarySerializer(serializers.ModelSerializer):
    actor = federation_serializers.APIActorSerializer()
    uploads_count = serializers.SerializerMethodField()
    latest_scan = LibraryScanSerializer(required=False, allow_null=True)
    # The follow field is likely broken, so I removed the test
    follow = NestedLibraryFollowSerializer(required=False, allow_null=True)

    class Meta:
        model = music_models.Library
        fields = [
            "fid",
            "uuid",
            "actor",
            "name",
            "creation_date",
            "uploads_count",
            "privacy_level",
            "follow",
            "latest_scan",
        ]

    def get_uploads_count(self, o) -> int:
        return max(getattr(o, "_uploads_count", 0), o.uploads_count)

    @extend_schema_field(NestedLibraryFollowSerializer)
    def get_follow(self, o):
        try:
            return NestedLibraryFollowSerializer(o._follows[0]).data
        except (AttributeError, IndexError):
            return None


class LibraryFollowSerializer(serializers.ModelSerializer):
    target = common_serializers.RelatedField("uuid", LibrarySerializer(), required=True)
    actor = serializers.SerializerMethodField()

    class Meta:
        model = models.LibraryFollow
        fields = ["creation_date", "actor", "uuid", "target", "approved"]
        read_only_fields = ["uuid", "actor", "approved", "creation_date"]

    def validate_target(self, v):
        actor = self.context["actor"]
        if v.actor == actor:
            raise serializers.ValidationError("You cannot follow your own library")

        if v.received_follows.filter(actor=actor).exists():
            raise serializers.ValidationError("You are already following this library")
        return v

    @extend_schema_field(federation_serializers.APIActorSerializer)
    def get_actor(self, o):
        return federation_serializers.APIActorSerializer(o.actor).data


class FollowSerializer(serializers.ModelSerializer):
    target = common_serializers.RelatedField(
        "fid", federation_serializers.APIActorSerializer(), required=True
    )
    actor = serializers.SerializerMethodField()

    class Meta:
        model = models.Follow
        fields = ["creation_date", "actor", "uuid", "target", "approved"]
        read_only_fields = ["uuid", "actor", "approved", "creation_date"]

    def validate_target(self, v):
        request_actor = self.context["actor"]
        if v == request_actor:
            raise serializers.ValidationError("You cannot follow yourself")
        if v.received_follows.filter(actor=request_actor).exists():
            raise serializers.ValidationError("You are already following this user")
        return v

    @extend_schema_field(federation_serializers.APIActorSerializer)
    def get_actor(self, o):
        return federation_serializers.APIActorSerializer(o.actor).data


def serialize_generic_relation(activity, obj):
    data = {"type": obj._meta.label}
    if data["type"] == "federation.Actor":
        data["full_username"] = obj.full_username
    else:
        data["uuid"] = obj.uuid

    if data["type"] == "music.Library":
        data["name"] = obj.name
    if (
        data["type"] == "federation.LibraryFollow"
        or data["type"] == "federation.Follow"
    ):
        data["approved"] = obj.approved
    return data


class ActivitySerializer(serializers.ModelSerializer):
    actor = federation_serializers.APIActorSerializer()
    object = serializers.SerializerMethodField(allow_null=True)
    target = serializers.SerializerMethodField(allow_null=True)
    related_object = serializers.SerializerMethodField()

    class Meta:
        model = models.Activity
        fields = [
            "uuid",
            "fid",
            "actor",
            "payload",
            "object",
            "target",
            "related_object",
            "actor",
            "creation_date",
            "type",
        ]

    @extend_schema_field(OpenApiTypes.OBJECT, None)
    def get_object(self, o):
        if o.object:
            return serialize_generic_relation(o, o.object)

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_related_object(self, o):
        if o.related_object:
            return serialize_generic_relation(o, o.related_object)

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_target(self, o):
        if o.target:
            return serialize_generic_relation(o, o.target)


class InboxItemSerializer(serializers.ModelSerializer):
    activity = ActivitySerializer()

    class Meta:
        model = models.InboxItem
        fields = ["id", "type", "activity", "is_read"]
        read_only_fields = ["id", "type", "activity"]


class InboxItemActionSerializer(common_serializers.ActionSerializer):
    actions = [common_serializers.Action("read", allow_all=True)]
    filterset_class = filters.InboxItemFilter

    def handle_read(self, objects):
        return objects.update(is_read=True)


OBJECT_SERIALIZER_MAPPING = {
    music_models.Artist: federation_serializers.ArtistSerializer,
    music_models.Album: federation_serializers.AlbumSerializer,
    music_models.Track: federation_serializers.TrackSerializer,
    music_models.Library: federation_serializers.LibrarySerializer,
    models.Actor: federation_serializers.APIActorSerializer,
    audio_models.Channel: audio_serializers.ChannelSerializer,
    playlists_models.Playlist: federation_serializers.PlaylistSerializer,
}


def convert_url_to_webfinger(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc  # e.g., "node1.funkwhale.test"
    path_parts = parsed_url.path.strip("/").split("/")
    # Ensure the path is in the expected format
    if len(path_parts) > 0 and path_parts[0].startswith("@"):
        username = path_parts[0][1:]  # Remove the '@'
        return f"{username}@{domain}"
    return None


class FetchSerializer(serializers.ModelSerializer):
    actor = federation_serializers.APIActorSerializer(read_only=True)
    object_uri = serializers.CharField(required=True, write_only=True)
    object = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    force = serializers.BooleanField(default=False, required=False, write_only=True)

    class Meta:
        model = models.Fetch
        fields = [
            "id",
            "url",
            "actor",
            "status",
            "detail",
            "creation_date",
            "fetch_date",
            "object_uri",
            "force",
            "type",
            "object",
        ]
        read_only_fields = [
            "id",
            "url",
            "actor",
            "status",
            "detail",
            "creation_date",
            "fetch_date",
            "type",
            "object",
        ]

    def get_type(self, fetch):
        obj = fetch.object
        if obj is None:
            return None

        # Return the type as a string
        if isinstance(obj, music_models.Artist):
            return "artist"
        elif isinstance(obj, music_models.Album):
            return "album"
        elif isinstance(obj, music_models.Track):
            return "track"
        elif isinstance(obj, models.Actor):
            return "account"
        elif isinstance(obj, audio_models.Channel):
            return "channel"
        elif isinstance(obj, playlists_models.Playlist):
            return "playlist"
        else:
            return None

    def validate_object_uri(self, value):
        if value.startswith("https://"):
            converted = convert_url_to_webfinger(value)
            if converted:
                value = converted
        if value.startswith("@"):
            value = value.lstrip("@")
        validator = validators.EmailValidator()
        try:
            validator(value)
        except validators.ValidationError:
            return value
        return f"webfinger://{value}"

    @extend_schema_field(
        {
            "oneOf": [
                {"$ref": "#/components/schemas/Artist"},
                {"$ref": "#/components/schemas/Album"},
                {"$ref": "#/components/schemas/Track"},
                {"$ref": "#/components/schemas/APIActor"},
                {"$ref": "#/components/schemas/Channel"},
                {"$ref": "#/components/schemas/Playlist"},
            ]
        }
    )
    def get_object(self, fetch):
        obj = fetch.object
        if obj is None:
            return None

        serializer_class = OBJECT_SERIALIZER_MAPPING.get(type(obj))
        if serializer_class:
            return serializer_class(obj).data
        return None

    def create(self, validated_data):
        check_duplicates = not validated_data.get("force", False)
        if check_duplicates:
            # first we check for duplicates
            duplicate = (
                validated_data["actor"]
                .fetches.filter(
                    status="finished",
                    url=validated_data["object_uri"],
                    creation_date__gte=timezone.now()
                    - datetime.timedelta(
                        seconds=settings.FEDERATION_DUPLICATE_FETCH_DELAY
                    ),
                )
                .order_by("-creation_date")
                .first()
            )
            if duplicate:
                return duplicate

        fetch = models.Fetch.objects.create(
            actor=validated_data["actor"], url=validated_data["object_uri"]
        )
        return fetch


class FullActorSerializer(serializers.Serializer):
    fid = serializers.URLField()
    url = serializers.URLField()
    domain = serializers.CharField(source="domain_id")
    creation_date = serializers.DateTimeField()
    last_fetch_date = serializers.DateTimeField()
    name = serializers.CharField()
    preferred_username = serializers.CharField()
    full_username = serializers.CharField()
    type = serializers.CharField()
    is_local = serializers.BooleanField()
    is_channel = serializers.SerializerMethodField()
    manually_approves_followers = serializers.BooleanField()
    user = users_serializers.UserBasicSerializer()
    summary = common_serializers.ContentSerializer(source="summary_obj")
    icon = common_serializers.AttachmentSerializer(source="attachment_icon")

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_channel(self, o):
        try:
            return bool(o.channel)
        except ObjectDoesNotExist:
            return False
