from rest_framework import serializers

from funkwhale_api.activity import serializers as activity_serializers
from funkwhale_api.federation import serializers as federation_serializers
from funkwhale_api.music.serializers import TrackActivitySerializer, TrackSerializer

from . import models


class TrackFavoriteActivitySerializer(activity_serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    object = TrackActivitySerializer(source="track")
    actor = federation_serializers.APIActorSerializer(read_only=True)
    published = serializers.DateTimeField(source="creation_date")

    class Meta:
        model = models.TrackFavorite
        fields = ["id", "local_id", "object", "type", "actor", "published"]

    def get_type(self, obj):
        return "Like"


class UserTrackFavoriteSerializer(serializers.ModelSerializer):
    track = TrackSerializer(read_only=True)
    actor = federation_serializers.APIActorSerializer(read_only=True)

    class Meta:
        model = models.TrackFavorite
        fields = ("id", "actor", "track", "creation_date", "actor")


class UserTrackFavoriteWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TrackFavorite
        fields = ("id", "track", "creation_date")


class SimpleFavoriteSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    track = serializers.IntegerField()


class AllFavoriteSerializer(serializers.Serializer):
    results = SimpleFavoriteSerializer(many=True, source="*")
    count = serializers.SerializerMethodField()

    def get_count(self, o) -> int:
        return len(o)
