import logging
import uuid

from django.db.models import Q

from funkwhale_api.favorites import models as favorites_models
from funkwhale_api.history import models as history_models
from funkwhale_api.music import models as music_models
from funkwhale_api.playlists import models as playlist_models

from . import activity, actors, models, serializers

logger = logging.getLogger(__name__)
inbox = activity.InboxRouter()
outbox = activity.OutboxRouter()


def with_recipients(payload, to=[], cc=[]):
    if to:
        payload["to"] = to
    if cc:
        payload["cc"] = cc
    return payload


@inbox.register({"type": "Follow"})
def inbox_follow(payload, context):
    context["recipient"] = [
        ii.actor for ii in context["inbox_items"] if ii.type == "to"
    ][0]
    serializer = serializers.FollowSerializer(data=payload, context=context)
    if not serializer.is_valid(raise_exception=context.get("raise_exception", False)):
        logger.debug(
            "Discarding invalid follow from {}: %s",
            context["actor"].fid,
            serializer.errors,
        )
        return

    autoapprove = serializer.validated_data["object"].should_autoapprove_follow(
        context["actor"]
    )
    follow = serializer.save(approved=True if autoapprove else None)
    if follow.approved:
        outbox.dispatch({"type": "Accept"}, context={"follow": follow})
    return {"object": follow.target, "related_object": follow}


@inbox.register({"type": "Accept"})
def inbox_accept(payload, context):
    context["recipient"] = [
        ii.actor for ii in context["inbox_items"] if ii.type == "to"
    ][0]
    serializer = serializers.AcceptFollowSerializer(data=payload, context=context)
    if not serializer.is_valid(raise_exception=context.get("raise_exception", False)):
        logger.debug(
            "Discarding invalid accept from {}: %s",
            context["actor"].fid,
            serializer.errors,
        )
        return

    serializer.save()
    obj = serializer.validated_data["follow"]
    return {"object": obj, "related_object": obj.target}


@outbox.register({"type": "Accept"})
def outbox_accept(context):
    follow = context["follow"]
    if follow._meta.label == "federation.LibraryFollow":
        actor = follow.target.actor
    else:
        actor = follow.target
    payload = serializers.AcceptFollowSerializer(follow, context={"actor": actor}).data
    yield {
        "actor": actor,
        "type": "Accept",
        "payload": with_recipients(payload, to=[follow.actor]),
        "object": follow,
        "related_object": follow.target,
    }


@outbox.register({"type": "Reject"})
def outbox_reject_follow(context):
    follow = context["follow"]
    if follow._meta.label == "federation.LibraryFollow":
        actor = follow.target.actor
    else:
        actor = follow.target
    payload = serializers.RejectFollowSerializer(follow, context={"actor": actor}).data
    yield {
        "actor": actor,
        "type": "Reject",
        "payload": with_recipients(payload, to=[follow.actor]),
        "object": follow,
        "related_object": follow.target,
    }


@inbox.register({"type": "Reject"})
def inbox_reject_follow(payload, context):
    serializer = serializers.RejectFollowSerializer(data=payload, context=context)
    if not serializer.is_valid(raise_exception=context.get("raise_exception", False)):
        logger.debug(
            "Discarding invalid follow reject from %s: %s",
            context["actor"].fid,
            serializer.errors,
        )
        return

    serializer.save()


@inbox.register({"type": "Undo", "object.type": "Follow"})
def inbox_undo_follow(payload, context):
    serializer = serializers.UndoFollowSerializer(data=payload, context=context)
    if not serializer.is_valid(raise_exception=context.get("raise_exception", False)):
        logger.debug(
            "Discarding invalid follow undo from %s: %s",
            context["actor"].fid,
            serializer.errors,
        )
        return

    serializer.save()


@outbox.register({"type": "Undo", "object.type": "Follow"})
def outbox_undo_follow(context):
    follow = context["follow"]
    actor = follow.actor
    if follow._meta.label == "federation.LibraryFollow":
        recipient = follow.target.actor
    else:
        recipient = follow.target
    payload = serializers.UndoFollowSerializer(follow, context={"actor": actor}).data
    yield {
        "actor": actor,
        "type": "Undo",
        "payload": with_recipients(payload, to=[recipient]),
        "object": follow,
        "related_object": follow.target,
    }


@outbox.register({"type": "Follow"})
def outbox_follow(context):
    follow = context["follow"]
    if follow._meta.label == "federation.LibraryFollow":
        target = follow.target.actor
    else:
        target = follow.target
    payload = serializers.FollowSerializer(follow, context={"actor": follow.actor}).data
    yield {
        "type": "Follow",
        "actor": follow.actor,
        "payload": with_recipients(payload, to=[target]),
        "object": follow.target,
        "related_object": follow,
    }


@outbox.register({"type": "Create", "object.type": "Audio"})
def outbox_create_audio(context):
    upload = context["upload"]
    channel = upload.library.get_channel()
    followers_target = channel.actor if channel else upload.library.actor
    actor = channel.actor if channel else upload.library.actor
    if channel:
        serializer = serializers.ChannelCreateUploadSerializer(upload)
    else:
        upload_serializer = serializers.UploadSerializer
        serializer = serializers.ActivitySerializer(
            {
                "type": "Create",
                "actor": actor.fid,
                "object": upload_serializer(upload).data,
            }
        )
    yield {
        "type": "Create",
        "actor": actor,
        "payload": with_recipients(
            serializer.data, to=[{"type": "followers", "target": followers_target}]
        ),
        "object": upload,
        "target": None if channel else upload.library,
    }


@inbox.register({"type": "Create", "object.type": "Audio"})
def inbox_create_audio(payload, context):
    is_channel = "library" not in payload["object"]
    if is_channel:
        channel = context["actor"].get_channel()
        serializer = serializers.ChannelCreateUploadSerializer(
            data=payload,
            context={"channel": channel},
        )
    else:
        serializer = serializers.UploadSerializer(
            data=payload["object"],
            context={"activity": context.get("activity"), "actor": context["actor"]},
        )
    if not serializer.is_valid(raise_exception=context.get("raise_exception", False)):
        logger.warn("Discarding invalid audio create: %s", serializer.errors)
        return

    upload = serializer.save()
    if is_channel:
        return {"object": upload, "target": channel}
    else:
        return {"object": upload, "target": upload.library}


@inbox.register({"type": "Delete", "object.type": "Library"})
def inbox_delete_library(payload, context):
    actor = context["actor"]
    library_id = payload["object"].get("id")
    if not library_id:
        logger.debug("Discarding deletion of empty library")
        return

    try:
        library = actor.libraries.get(fid=library_id)
    except music_models.Library.DoesNotExist:
        logger.debug("Discarding deletion of unkwnown library %s", library_id)
        return

    library.delete()


@outbox.register({"type": "Delete", "object.type": "Library"})
def outbox_delete_library(context):
    library = context["library"]
    serializer = serializers.ActivitySerializer(
        {"type": "Delete", "object": {"type": "Library", "id": library.fid}}
    )
    yield {
        "type": "Delete",
        "actor": library.actor,
        "payload": with_recipients(
            serializer.data, to=[{"type": "followers", "target": library}]
        ),
    }


@outbox.register({"type": "Update", "object.type": "Library"})
def outbox_update_library(context):
    library = context["library"]
    serializer = serializers.ActivitySerializer(
        {"type": "Update", "object": serializers.LibrarySerializer(library).data}
    )

    yield {
        "type": "Update",
        "actor": library.actor,
        "payload": with_recipients(
            serializer.data, to=[{"type": "followers", "target": library}]
        ),
    }


@inbox.register({"type": "Update", "object.type": "Library"})
def inbox_update_library(payload, context):
    actor = context["actor"]
    library_id = payload["object"].get("id")
    if not library_id:
        logger.debug("Discarding deletion of empty library")
        return

    if not actor.libraries.filter(fid=library_id).exists():
        logger.debug("Discarding deletion of unkwnown library %s", library_id)
        return

    serializer = serializers.LibrarySerializer(data=payload["object"])
    if serializer.is_valid():
        serializer.save()
    else:
        logger.debug(
            "Discarding update of library %s because of payload errors: %s",
            library_id,
            serializer.errors,
        )


@inbox.register({"type": "Delete", "object.type": "Audio"})
def inbox_delete_audio(payload, context):
    actor = context["actor"]
    try:
        upload_fids = [i for i in payload["object"]["id"]]
    except TypeError:
        # we did not receive a list of Ids, so we can probably use the value directly
        upload_fids = [payload["object"]["id"]]

    query = Q(fid__in=upload_fids) & (
        Q(library__actor=actor) | Q(track__artist_credit__artist__channel__actor=actor)
    )
    candidates = music_models.Upload.objects.filter(query)

    total = candidates.count()
    logger.info("Deleting %s uploads with ids %s", total, upload_fids)
    candidates.delete()


@outbox.register({"type": "Delete", "object.type": "Audio"})
def outbox_delete_audio(context):
    uploads = context["uploads"]
    library = uploads[0].library
    channel = library.get_channel()
    actor = channel.actor if channel else library.actor
    followers_target = channel.actor if channel else actor
    serializer = serializers.ActivitySerializer(
        {
            "type": "Delete",
            "object": {"type": "Audio", "id": [u.get_federation_id() for u in uploads]},
        }
    )
    yield {
        "type": "Delete",
        "actor": actor,
        "payload": with_recipients(
            serializer.data, to=[{"type": "followers", "target": followers_target}]
        ),
    }


def handle_library_entry_update(payload, context, queryset, serializer_class):
    actor = context["actor"]
    obj_id = payload["object"].get("id")
    if not obj_id:
        logger.debug("Discarding update of empty obj")
        return

    try:
        obj = queryset.select_related("attributed_to").get(fid=obj_id)
    except queryset.model.DoesNotExist:
        logger.debug("Discarding update of unkwnown obj %s", obj_id)
        return
    if not actor.can_manage(obj):
        logger.debug(
            "Discarding unauthorize update of obj %s from %s", obj_id, actor.fid
        )
        return

    serializer = serializer_class(obj, data=payload["object"])
    if serializer.is_valid():
        serializer.save()
    else:
        logger.debug(
            "Discarding update of obj %s because of payload errors: %s",
            obj_id,
            serializer.errors,
        )


@inbox.register({"type": "Update", "object.type": "Track"})
def inbox_update_track(payload, context):
    return handle_library_entry_update(
        payload,
        context,
        queryset=music_models.Track.objects.all(),
        serializer_class=serializers.TrackSerializer,
    )


@inbox.register({"type": "Update", "object.type": "Audio"})
def inbox_update_audio(payload, context):
    serializer = serializers.ChannelCreateUploadSerializer(
        data=payload, context=context
    )

    if not serializer.is_valid(raise_exception=context.get("raise_exception", False)):
        logger.info("Skipped update, invalid payload")
        return
    serializer.save()


@outbox.register({"type": "Update", "object.type": "Audio"})
def outbox_update_audio(context):
    upload = context["upload"]
    channel = upload.library.get_channel()
    actor = channel.actor
    serializer = serializers.ChannelCreateUploadSerializer(
        upload, context={"type": "Update", "activity_id_suffix": str(uuid.uuid4())[:8]}
    )

    yield {
        "type": "Update",
        "actor": actor,
        "payload": with_recipients(
            serializer.data,
            to=[activity.PUBLIC_ADDRESS, {"type": "instances_with_followers"}],
        ),
    }


@inbox.register({"type": "Update", "object.type": "Artist"})
def inbox_update_artist(payload, context):
    return handle_library_entry_update(
        payload,
        context,
        queryset=music_models.Artist.objects.all(),
        serializer_class=serializers.ArtistSerializer,
    )


@inbox.register({"type": "Update", "object.type": "Album"})
def inbox_update_album(payload, context):
    return handle_library_entry_update(
        payload,
        context,
        queryset=music_models.Album.objects.all(),
        serializer_class=serializers.AlbumSerializer,
    )


@outbox.register({"type": "Update", "object.type": "Track"})
def outbox_update_track(context):
    track = context["track"]
    serializer = serializers.ActivitySerializer(
        {"type": "Update", "object": serializers.TrackSerializer(track).data}
    )

    yield {
        "type": "Update",
        "actor": actors.get_service_actor(),
        "payload": with_recipients(
            serializer.data,
            to=[activity.PUBLIC_ADDRESS, {"type": "instances_with_followers"}],
        ),
    }


@outbox.register({"type": "Update", "object.type": "Album"})
def outbox_update_album(context):
    album = context["album"]
    serializer = serializers.ActivitySerializer(
        {"type": "Update", "object": serializers.AlbumSerializer(album).data}
    )

    yield {
        "type": "Update",
        "actor": actors.get_service_actor(),
        "payload": with_recipients(
            serializer.data,
            to=[activity.PUBLIC_ADDRESS, {"type": "instances_with_followers"}],
        ),
    }


@outbox.register({"type": "Update", "object.type": "Artist"})
def outbox_update_artist(context):
    artist = context["artist"]
    serializer = serializers.ActivitySerializer(
        {"type": "Update", "object": serializers.ArtistSerializer(artist).data}
    )

    yield {
        "type": "Update",
        "actor": actors.get_service_actor(),
        "payload": with_recipients(
            serializer.data,
            to=[activity.PUBLIC_ADDRESS, {"type": "instances_with_followers"}],
        ),
    }


@outbox.register(
    {
        "type": "Delete",
        "object.type": [
            "Tombstone",
            "Actor",
            "Person",
            "Application",
            "Organization",
            "Service",
            "Group",
        ],
    }
)
def outbox_delete_actor(context):
    actor = context["actor"]
    serializer = serializers.ActivitySerializer(
        {"type": "Delete", "object": {"type": actor.type, "id": actor.fid}}
    )
    yield {
        "type": "Delete",
        "actor": actor,
        "payload": with_recipients(
            serializer.data,
            to=[activity.PUBLIC_ADDRESS, {"type": "instances_with_followers"}],
        ),
    }


@inbox.register(
    {
        "type": "Delete",
        "object.type": [
            "Actor",
            "Person",
            "Application",
            "Organization",
            "Service",
            "Group",
        ],
    }
)
def inbox_delete_actor(payload, context):
    actor = context["actor"]
    serializer = serializers.ActorDeleteSerializer(data=payload)
    if not serializer.is_valid():
        logger.info("Skipped actor %s deletion, invalid payload", actor.fid)
        return

    deleted_fid = serializer.validated_data["fid"]
    try:
        # ensure the actor only can delete itself, and is a remote one
        actor = models.Actor.objects.local(False).get(fid=deleted_fid, pk=actor.pk)
    except models.Actor.DoesNotExist:
        logger.warn("Cannot delete actor %s, no matching object found", actor.fid)
        return
    actor.delete()


@inbox.register({"type": "Delete", "object.type": "Tombstone"})
def inbox_delete(payload, context):
    serializer = serializers.DeleteSerializer(data=payload, context=context)
    if not serializer.is_valid(raise_exception=context.get("raise_exception", False)):
        logger.info("Skipped deletion, invalid payload")
        return

    to_delete = serializer.validated_data["object"]
    to_delete.delete()


@inbox.register({"type": "Flag"})
def inbox_flag(payload, context):
    serializer = serializers.FlagSerializer(data=payload, context=context)
    if not serializer.is_valid(raise_exception=context.get("raise_exception", False)):
        logger.debug(
            "Discarding invalid report from {}: %s",
            context["actor"].fid,
            serializer.errors,
        )
        return

    report = serializer.save()
    return {"object": report.target, "related_object": report}


@outbox.register({"type": "Flag"})
def outbox_flag(context):
    report = context["report"]
    if not report.target or not report.target.fid:
        return
    actor = actors.get_service_actor()
    serializer = serializers.FlagSerializer(report)
    yield {
        "type": "Flag",
        "actor": actor,
        "payload": with_recipients(
            serializer.data,
            # Mastodon requires the report to be sent to the reported actor inbox
            # (and not the shared inbox)
            to=[{"type": "actor_inbox", "actor": report.target_owner}],
        ),
    }


@inbox.register({"type": "Delete", "object.type": "Album"})
def inbox_delete_album(payload, context):
    actor = context["actor"]
    album_id = payload["object"].get("id")
    if not album_id:
        logger.debug("Discarding deletion of empty library")
        return

    query = Q(fid=album_id) & (
        Q(attributed_to=actor) | Q(artist_credit__artist__channel__actor=actor)
    )
    try:
        album = music_models.Album.objects.get(query)
    except music_models.Album.DoesNotExist:
        logger.debug("Discarding deletion of unkwnown album %s", album_id)
        return

    album.delete()


@outbox.register({"type": "Delete", "object.type": "Album"})
def outbox_delete_album(context):
    album = context["album"]
    album_artist = album.artist_credit.all()[0].artist
    actor = (
        album_artist.channel.actor
        if album_artist.get_channel()
        else album.attributed_to
    )
    actor = actor or actors.get_service_actor()
    serializer = serializers.ActivitySerializer(
        {"type": "Delete", "object": {"type": "Album", "id": album.fid}}
    )

    yield {
        "type": "Delete",
        "actor": actor,
        "payload": with_recipients(
            serializer.data,
            to=[activity.PUBLIC_ADDRESS, {"type": "instances_with_followers"}],
        ),
    }


@outbox.register({"type": "Like", "object.type": "Track"})
def outbox_create_track_favorite(context):
    track = context["track"]
    actor = context["actor"]

    serializer = serializers.ActivitySerializer(
        {
            "type": "Like",
            "id": context["id"],
            "object": {"type": "Track", "id": track.fid},
            "audience": actor.user.privacy_level,
        }
    )
    yield {
        "type": "Like",
        "actor": actor,
        "payload": with_recipients(
            serializer.data,
            to=[{"type": "followers", "target": actor}],
        ),
    }


@outbox.register({"type": "Dislike", "object.type": "Track"})
def outbox_delete_favorite(context):
    favorite = context["favorite"]
    actor = favorite.actor
    serializer = serializers.ActivitySerializer(
        {"type": "Dislike", "object": {"type": "Track", "id": favorite.track.fid}}
    )
    yield {
        "type": "Dislike",
        "actor": actor,
        "payload": with_recipients(
            serializer.data,
            to=[{"type": "followers", "target": actor}],
        ),
    }


@inbox.register({"type": "Like", "object.type": "Track"})
def inbox_create_favorite(payload, context):
    serializer = serializers.TrackFavoriteSerializer(data=payload)
    serializer.is_valid(raise_exception=True)
    instance = serializer.save()
    return {"object": instance}


@inbox.register({"type": "Dislike", "object.type": "Track"})
def inbox_delete_favorite(payload, context):
    actor = context["actor"]
    track_id = payload["object"].get("id")

    query = Q(track__fid=track_id) & Q(actor=actor)
    try:
        favorite = favorites_models.TrackFavorite.objects.get(query)
    except favorites_models.TrackFavorite.DoesNotExist:
        logger.debug(
            "Discarding deletion of unkwnown favorite with track : %s", track_id
        )
        return
    favorite.delete()


@outbox.register({"type": "Listen", "object.type": "Track"})
def outbox_create_listening(context):
    track = context["track"]
    actor = context["actor"]

    serializer = serializers.ActivitySerializer(
        {
            "type": "Listen",
            "id": context["id"],
            "object": {"type": "Track", "id": track.fid},
            "audience": actor.user.privacy_level,
        }
    )
    yield {
        "type": "Listen",
        "actor": actor,
        "payload": with_recipients(
            serializer.data,
            to=[{"type": "followers", "target": actor}],
        ),
    }


@outbox.register({"type": "Delete", "object.type": "Listen"})
def outbox_delete_listening(context):
    listening = context["listening"]
    actor = listening.actor
    serializer = serializers.ActivitySerializer(
        {"type": "Delete", "object": {"type": "Listen", "id": listening.fid}}
    )
    yield {
        "type": "Delete",
        "actor": actor,
        "payload": with_recipients(
            serializer.data,
            to=[{"type": "followers", "target": actor}],
        ),
    }


@inbox.register({"type": "Listen", "object.type": "Track"})
def inbox_create_listening(payload, context):
    serializer = serializers.ListeningSerializer(data=payload)
    serializer.is_valid(raise_exception=True)
    instance = serializer.save()
    return {"object": instance}


@inbox.register({"type": "Delete", "object.type": "Listen"})
def inbox_delete_listening(payload, context):
    actor = context["actor"]
    listening_id = payload["object"].get("id")

    query = Q(fid=listening_id) & Q(actor=actor)
    try:
        favorite = history_models.Listening.objects.get(query)
    except history_models.Listening.DoesNotExist:
        logger.debug("Discarding deletion of unkwnown listening %s", listening_id)
        return
    favorite.delete()


@outbox.register({"type": "Create", "object.type": "Playlist"})
def outbox_create_playlist(context):
    playlist = context["playlist"]

    serializer = serializers.ActivitySerializer(
        {
            "type": "Create",
            "actor": playlist.actor,
            "id": playlist.fid,
            "object": serializers.PlaylistSerializer(playlist).data,
        }
    )
    yield {
        "type": "Create",
        "actor": playlist.actor,
        "payload": with_recipients(
            serializer.data,
            to=[{"type": "followers", "target": playlist.actor}],
        ),
    }


@outbox.register({"type": "Delete", "object.type": "Playlist"})
def outbox_delete_playlist(context):
    playlist = context["playlist"]
    actor = playlist.actor
    serializer = serializers.ActivitySerializer(
        {"type": "Delete", "object": {"type": "Playlist", "id": playlist.fid}}
    )
    yield {
        "type": "Delete",
        "actor": actor,
        "payload": with_recipients(
            serializer.data,
            to=[activity.PUBLIC_ADDRESS, {"type": "instances_with_followers"}],
        ),
    }


@inbox.register({"type": "Create", "object.type": "Playlist"})
def inbox_create_playlist(payload, context):
    serializer = serializers.PlaylistSerializer(data=payload["object"])
    serializer.is_valid(raise_exception=True)
    instance = serializer.save()
    return {"object": instance}


@inbox.register({"type": "Delete", "object.type": "Playlist"})
def inbox_delete_playlist(payload, context):
    actor = context["actor"]
    playlist_id = payload["object"].get("id")

    query = Q(fid=playlist_id) & Q(actor=actor)
    try:
        playlist = playlist_models.Playlist.objects.get(query)
    except playlist_models.Playlist.DoesNotExist:
        logger.debug("Discarding deletion of unkwnown listening %s", playlist_id)
        return
    playlist.playlist_tracks.all().delete()
    playlist.delete()


@inbox.register({"type": "Update", "object.type": "Playlist"})
def inbox_update_playlist(payload, context):
    """If we receive an update on an unkwnown playlist, we create the playlist"""

    playlist_id = payload["object"].get("id")

    serializer = serializers.PlaylistSerializer(data=payload["object"])
    if serializer.is_valid(raise_exception=True):
        playlist = serializer.save()
        # we update the playlist.library to get the plt.track.uploads locally
        if follows := playlist.library.received_follows.filter(approved=True):
            playlist.library.schedule_scan(follows[0].actor, force=True)
        # we trigger a scan since we use this activity to avoid sending many PlaylistTracks activities
        playlist.schedule_scan(actors.get_service_actor(), force=True)

        return
    else:
        logger.debug(
            "Discarding update of playlist_id %s because of payload errors: %s",
            playlist_id,
            serializer.errors,
        )


@outbox.register({"type": "Update", "object.type": "Playlist"})
def outbox_update_playlist(context):
    playlist = context["playlist"]
    serializer = serializers.ActivitySerializer(
        {"type": "Update", "object": serializers.PlaylistSerializer(playlist).data}
    )
    yield {
        "type": "Update",
        "actor": playlist.actor,
        "payload": with_recipients(
            serializer.data,
            to=[{"type": "followers", "target": playlist.actor}],
        ),
    }


@inbox.register({"type": "Update", "object.type": "AudioCollection"})
def inbox_update_audiocollection(payload, context):
    serializer = serializers.AudioCollectionSerializer(
        data=payload["object"], context=context
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()


@outbox.register({"type": "Update", "object.type": "AudioCollection"})
def outbox_update_audiocollection(context):
    audios = context["audios"]
    serializer = serializers.ActivitySerializer(
        {"type": "Update", "object": serializers.AudioCollectionSerializer(audios).data}
    )
    yield {
        "type": "Update",
        "actor": audios[0].library.actor,
        "payload": with_recipients(
            serializer.data,
            to=[activity.PUBLIC_ADDRESS, {"type": "instances_with_followers"}],
        ),
    }


@inbox.register({"type": "Delete", "object.type": "AudioCollection"})
def inbox_delete_audiocollection(payload, context):
    serializer = serializers.AudioCollectionSerializer(
        data=payload["object"], context=context
    )
    serializer.is_valid(raise_exception=True)

    for upload in serializer.validated_data["items"]:
        music_models.Upload.objects.filter(fid=upload["id"]).delete()


@outbox.register({"type": "Delete", "object.type": "AudioCollection"})
def outbox_delete_audiocollection(context):
    audios = context["audios"]
    serializer = serializers.ActivitySerializer(
        {"type": "Delete", "object": serializers.AudioCollectionSerializer(audios).data}
    )
    yield {
        "type": "Delete",
        "actor": audios[0].library.actor,
        "payload": with_recipients(
            serializer.data,
            to=[activity.PUBLIC_ADDRESS, {"type": "instances_with_followers"}],
        ),
    }
