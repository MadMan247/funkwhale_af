import datetime
from unittest.mock import Mock

import pytest
from django.db.models import signals
from django.urls import reverse

from funkwhale_api.federation import (
    actors,
    api_serializers,
    models,
    serializers,
    tasks,
    views,
)


def test_user_can_list_their_library_follows(factories, logged_in_api_client):
    # followed by someont else
    factories["federation.LibraryFollow"]()
    follow = factories["federation.LibraryFollow"](
        actor__user=logged_in_api_client.user
    )
    url = reverse("api:v2:federation:library-follows-list")
    response = logged_in_api_client.get(url)

    assert response.data["count"] == 1
    assert response.data["results"][0]["uuid"] == str(follow.uuid)


def test_user_can_fetch_library_using_url(mocker, factories, logged_in_api_client):
    library = factories["music.Library"]()
    mocked_retrieve = mocker.patch(
        "funkwhale_api.federation.utils.retrieve_ap_object", return_value=library
    )
    url = reverse("api:v2:federation:libraries-fetch")
    response = logged_in_api_client.post(url, {"fid": library.fid})
    assert mocked_retrieve.call_count == 1
    args = mocked_retrieve.call_args
    assert args[0] == (library.fid,)
    assert args[1]["queryset"].model == views.MusicLibraryViewSet.queryset.model
    assert args[1]["serializer_class"] == serializers.LibrarySerializer
    assert response.status_code == 200
    assert response.data["results"] == [api_serializers.LibrarySerializer(library).data]


def test_user_can_fetch_playlist_library_using_url(
    mocker, factories, logged_in_api_client
):
    pl_library = factories["music.Library"]()
    upload = factories["music.Upload"]()
    upload.playlist_libraries.add(pl_library)

    mocked_retrieve = mocker.patch(
        "funkwhale_api.federation.utils.retrieve_ap_object", return_value=pl_library
    )
    url = reverse("api:v2:federation:libraries-fetch")
    response = logged_in_api_client.post(url, {"fid": pl_library.fid})
    assert mocked_retrieve.call_count == 1
    args = mocked_retrieve.call_args
    assert args[0] == (pl_library.fid,)
    assert args[1]["queryset"].model == views.MusicLibraryViewSet.queryset.model
    assert args[1]["serializer_class"] == serializers.LibrarySerializer
    assert response.status_code == 200
    assert response.data["results"] == [
        api_serializers.LibrarySerializer(pl_library).data
    ]


def test_user_can_schedule_library_scan(mocker, factories, logged_in_api_client):
    actor = logged_in_api_client.user.actor
    library = factories["music.Library"](privacy_level="everyone")
    library.actor.user.delete()  # make sure library is not local

    schedule_scan = mocker.patch(
        "funkwhale_api.music.models.Library.schedule_scan", return_value=True
    )
    url = reverse("api:v2:federation:libraries-scan", kwargs={"uuid": library.uuid})

    response = logged_in_api_client.post(url)

    assert response.status_code == 200

    schedule_scan.assert_called_once_with(actor=actor)


def test_can_follow_library(factories, logged_in_api_client, mocker):
    dispatch = mocker.patch("funkwhale_api.federation.routes.outbox.dispatch")
    actor = logged_in_api_client.user.create_actor()
    library = factories["music.Library"]()
    url = reverse("api:v2:federation:library-follows-list")
    response = logged_in_api_client.post(url, {"target": library.uuid})

    assert response.status_code == 201

    follow = library.received_follows.latest("id")

    assert follow.approved is None
    assert follow.actor == actor

    dispatch.assert_called_once_with({"type": "Follow"}, context={"follow": follow})


def test_can_undo_library_follow(factories, logged_in_api_client, mocker):
    dispatch = mocker.patch("funkwhale_api.federation.routes.outbox.dispatch")
    actor = logged_in_api_client.user.create_actor()
    follow = factories["federation.LibraryFollow"](actor=actor)
    delete = mocker.patch.object(follow.__class__, "delete")
    url = reverse(
        "api:v2:federation:library-follows-detail", kwargs={"uuid": follow.uuid}
    )
    response = logged_in_api_client.delete(url)

    assert response.status_code == 204

    delete.assert_called_once_with()
    dispatch.assert_called_once_with(
        {"type": "Undo", "object": {"type": "Follow"}}, context={"follow": follow}
    )


@pytest.mark.parametrize("action", ["accept", "reject"])
def test_user_cannot_edit_someone_else_library_follow(
    factories, logged_in_api_client, action
):
    logged_in_api_client.user.create_actor()
    follow = factories["federation.LibraryFollow"]()
    url = reverse(
        f"api:v2:federation:library-follows-{action}",
        kwargs={"uuid": follow.uuid},
    )
    response = logged_in_api_client.post(url)

    assert response.status_code == 404


@pytest.mark.parametrize("action,expected", [("accept", True), ("reject", False)])
def test_user_can_accept_or_reject_own_follows(
    factories, logged_in_api_client, action, expected, mocker
):
    mocked_dispatch = mocker.patch(
        "funkwhale_api.federation.activity.OutboxRouter.dispatch"
    )
    actor = logged_in_api_client.user.create_actor()
    follow = factories["federation.LibraryFollow"](target__actor=actor)
    url = reverse(
        f"api:v2:federation:library-follows-{action}",
        kwargs={"uuid": follow.uuid},
    )
    response = logged_in_api_client.post(url)

    assert response.status_code == 204

    follow.refresh_from_db()

    assert follow.approved is expected

    mocked_dispatch.assert_called_once_with(
        {"type": action.title()}, context={"follow": follow}
    )


def test_user_can_list_inbox_items(factories, logged_in_api_client):
    actor = logged_in_api_client.user.create_actor()
    ii = factories["federation.InboxItem"](
        activity__type="Follow", actor=actor, type="to"
    )

    factories["federation.InboxItem"](activity__type="Follow", actor=actor, type="cc")
    factories["federation.InboxItem"](activity__type="Follow", type="to")

    url = reverse("api:v2:federation:inbox-list")

    response = logged_in_api_client.get(url)

    assert response.status_code == 200
    assert response.data == {
        "count": 1,
        "results": [api_serializers.InboxItemSerializer(ii).data],
        "next": None,
        "previous": None,
    }


def test_user_can_update_read_status_of_inbox_item(factories, logged_in_api_client):
    actor = logged_in_api_client.user.create_actor()
    ii = factories["federation.InboxItem"](
        activity__type="Follow", actor=actor, type="to"
    )

    url = reverse("api:v2:federation:inbox-detail", kwargs={"pk": ii.pk})

    response = logged_in_api_client.patch(url, {"is_read": True})
    assert response.status_code == 200

    ii.refresh_from_db()

    assert ii.is_read is True


def test_can_detail_fetch(logged_in_api_client, factories):
    actor = logged_in_api_client.user.create_actor()
    fetch = factories["federation.Fetch"](url="http://test.object", actor=actor)
    url = reverse("api:v2:federation:fetches-detail", kwargs={"pk": fetch.pk})

    response = logged_in_api_client.get(url)

    expected = api_serializers.FetchSerializer(fetch).data

    assert response.status_code == 200
    assert response.data == expected


def test_user_can_list_domains(factories, api_client, preferences):
    preferences["common__api_authentication_required"] = False
    allowed = factories["federation.Domain"]()
    factories["moderation.InstancePolicy"](
        actor=None, for_domain=True, block_all=True
    ).target_domain
    url = reverse("api:v2:federation:domains-list")
    response = api_client.get(url)

    expected = {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [api_serializers.DomainSerializer(allowed).data],
    }
    assert response.data == expected


def test_can_retrieve_actor(factories, api_client, preferences):
    preferences["common__api_authentication_required"] = False
    actor = factories["federation.Actor"]()
    url = reverse(
        "api:v2:federation:actors-detail", kwargs={"full_username": actor.full_username}
    )
    response = api_client.get(url)

    expected = api_serializers.FullActorSerializer(actor).data
    assert response.data == expected


def test_can_retrieve_local_actor_with_allow_list_enabled(
    factories, api_client, preferences
):
    preferences["common__api_authentication_required"] = False
    preferences["moderation__allow_list_enabled"] = True
    actor = factories["federation.Actor"](local=True)
    url = reverse(
        "api:v2:federation:actors-detail", kwargs={"full_username": actor.full_username}
    )
    response = api_client.get(url)

    expected = api_serializers.FullActorSerializer(actor).data
    assert response.data == expected


@pytest.mark.parametrize(
    "object_id, expected_url",
    [
        ("https://fetch.url", "https://fetch.url"),
        ("name@domain.tld", "webfinger://name@domain.tld"),
        ("@name@domain.tld", "webfinger://name@domain.tld"),
    ],
)
def test_can_fetch_using_url_synchronous(
    object_id, expected_url, factories, logged_in_api_client, mocker, settings
):
    settings.FEDERATION_SYNCHRONOUS_FETCH = True
    actor = logged_in_api_client.user.create_actor()

    def fake_task(fetch_id):
        actor.fetches.filter(id=fetch_id).update(status="finished")

    fetch_task = mocker.patch.object(tasks, "fetch", side_effect=fake_task)

    url = reverse("api:v2:federation:fetches-list")
    data = {"object_uri": object_id}
    response = logged_in_api_client.post(url, data)
    assert response.status_code == 201

    fetch = actor.fetches.latest("id")

    assert fetch.status == "finished"
    assert fetch.url == expected_url
    assert response.data == api_serializers.FetchSerializer(fetch).data
    fetch_task.assert_called_once_with(fetch_id=fetch.pk)


def test_fetch_duplicate(factories, logged_in_api_client, settings, now):
    object_id = "http://example.test"
    settings.FEDERATION_DUPLICATE_FETCH_DELAY = 60
    actor = logged_in_api_client.user.create_actor()
    duplicate = factories["federation.Fetch"](
        actor=actor,
        status="finished",
        url=object_id,
        creation_date=now - datetime.timedelta(seconds=59),
    )
    url = reverse("api:v2:federation:fetches-list")
    data = {"object_uri": object_id}
    response = logged_in_api_client.post(url, data)
    assert response.status_code == 201
    assert response.data == api_serializers.FetchSerializer(duplicate).data


def test_fetch_duplicate_bypass_with_force(
    factories, logged_in_api_client, mocker, settings, now
):
    fetch_task = mocker.patch.object(tasks, "fetch")
    object_id = "http://example.test"
    settings.FEDERATION_DUPLICATE_FETCH_DELAY = 60
    actor = logged_in_api_client.user.create_actor()
    duplicate = factories["federation.Fetch"](
        actor=actor,
        status="finished",
        url=object_id,
        creation_date=now - datetime.timedelta(seconds=59),
    )
    url = reverse("api:v2:federation:fetches-list")
    data = {"object_uri": object_id, "force": True}
    response = logged_in_api_client.post(url, data)

    fetch = actor.fetches.latest("id")
    assert fetch != duplicate
    assert response.status_code == 201
    assert response.data == api_serializers.FetchSerializer(fetch).data
    fetch_task.assert_called_once_with(fetch_id=fetch.pk)


def test_library_follow_get_all(factories, logged_in_api_client):
    actor = logged_in_api_client.user.create_actor()
    library = factories["music.Library"]()
    follow = factories["federation.LibraryFollow"](target=library, actor=actor)
    factories["federation.LibraryFollow"]()
    factories["music.Library"]()
    url = reverse("api:v2:federation:library-follows-all")
    response = logged_in_api_client.get(url)

    assert response.status_code == 200
    assert response.data == {
        "results": [
            {
                "uuid": str(follow.uuid),
                "library": str(library.uuid),
                "approved": follow.approved,
            }
        ],
        "count": 1,
    }


def test_user_follow_get_all(factories, logged_in_api_client):
    actor = logged_in_api_client.user.create_actor()
    target_actor = factories["federation.Actor"]()
    follow = factories["federation.Follow"](target=target_actor, actor=actor)
    factories["federation.Follow"]()
    url = reverse("api:v2:federation:user-follows-all")
    response = logged_in_api_client.get(url)

    assert response.status_code == 200
    assert response.data == {
        "results": [
            {
                "uuid": str(follow.uuid),
                "actor": str(target_actor.fid),
                "approved": follow.approved,
            }
        ],
        "count": 1,
    }


def test_user_follow_retrieve(factories, logged_in_api_client):
    actor = logged_in_api_client.user.create_actor()
    target_actor = factories["federation.Actor"]()
    follow = factories["federation.Follow"](target=target_actor, actor=actor)
    factories["federation.Follow"]()
    url = reverse("api:v2:federation:user-follows-detail", kwargs={"uuid": follow.uuid})
    response = logged_in_api_client.get(url)

    assert response.status_code == 200


def test_user_can_list_their_received_follows(factories, logged_in_api_client):
    # followed by someont else
    factories["federation.Follow"]()
    follow = factories["federation.Follow"](actor__user=logged_in_api_client.user)
    url = reverse("api:v2:federation:user-follows-list")
    response = logged_in_api_client.get(url)

    assert response.data["count"] == 1
    assert response.data["results"][0]["uuid"] == str(follow.uuid)


def test_can_follow_user_actor(factories, logged_in_api_client, mocker):
    lib = factories["music.Library"]()
    lib2 = factories["music.Library"]()

    dispatch = mocker.patch("funkwhale_api.federation.routes.outbox.dispatch")
    mock_session = Mock()
    mock_response = Mock()
    # one response for the everyone lib and another one for followers lib
    mock_response.json.side_effect = [
        {"results": [serializers.LibrarySerializer(lib).data]},
        {"results": [serializers.LibrarySerializer(lib2).data]},
    ]
    mock_session.get.return_value = mock_response
    mocker.patch(
        "funkwhale_api.federation.utils.session.get_session",
        return_value=mock_session,
    )
    actor = logged_in_api_client.user.create_actor()
    target_actor = factories["federation.Actor"]()
    url = reverse("api:v2:federation:user-follows-list")
    lib.delete()
    lib2.delete()
    response = logged_in_api_client.post(url, {"target": target_actor.fid})

    assert response.status_code == 201

    follow = target_actor.received_follows.latest("id")

    assert follow.approved is None
    assert follow.actor == actor

    dispatch.assert_any_call({"type": "Follow"}, context={"follow": follow})


def test_can_undo_user_follow(factories, logged_in_api_client, mocker):
    dispatch = mocker.patch("funkwhale_api.federation.routes.outbox.dispatch")
    actor = logged_in_api_client.user.create_actor()
    follow = factories["federation.Follow"](actor=actor)
    delete = mocker.patch.object(follow.__class__, "delete")
    url = reverse("api:v2:federation:user-follows-detail", kwargs={"uuid": follow.uuid})
    response = logged_in_api_client.delete(url)

    assert response.status_code == 204

    delete.assert_called_once_with()
    dispatch.assert_called_once_with(
        {"type": "Undo", "object": {"type": "Follow"}}, context={"follow": follow}
    )


@pytest.mark.parametrize("action", ["accept", "reject"])
def test_user_cannot_edit_someone_else_user_follow(
    factories, logged_in_api_client, action
):
    logged_in_api_client.user.create_actor()
    follow = factories["federation.Follow"]()
    url = reverse(
        f"api:v2:federation:user-follows-{action}",
        kwargs={"uuid": follow.uuid},
    )
    response = logged_in_api_client.post(url)

    assert response.status_code == 404


@pytest.mark.parametrize("action,expected", [("accept", True), ("reject", False)])
def test_user_can_accept_or_reject_own_received_follows(
    factories, logged_in_api_client, action, expected, mocker
):
    mocked_dispatch = mocker.patch(
        "funkwhale_api.federation.activity.OutboxRouter.dispatch"
    )
    actor = logged_in_api_client.user.create_actor()
    follow = factories["federation.Follow"](target=actor)
    url = reverse(
        f"api:v2:federation:user-follows-{action}",
        kwargs={"uuid": follow.uuid},
    )
    response = logged_in_api_client.post(url)

    assert response.status_code == 204

    follow.refresh_from_db()

    assert follow.approved is expected

    mocked_dispatch.assert_called_once_with(
        {"type": action.title()}, context={"follow": follow}
    )


def test_user_can_block_actor(factories, logged_in_api_client):
    actor = factories["federation.Actor"]()
    logged_in_api_client.user.create_actor()
    url = reverse(
        "api:v2:federation:actors-block", kwargs={"full_username": actor.full_username}
    )
    response = logged_in_api_client.post(url)
    assert response.status_code == 204


def test_user_can_unblock_actor(factories, logged_in_api_client):
    actor = factories["federation.Actor"]()
    user_actor = logged_in_api_client.user.create_actor()
    factories["federation.BlockedActor"](actor=user_actor, target=actor)
    url = reverse(
        "api:v2:federation:actors-unblock",
        kwargs={"full_username": actor.full_username},
    )
    response = logged_in_api_client.post(url)
    assert response.status_code == 204


def test_user_can_get_blocked_users(factories, logged_in_api_client):
    user_actor = logged_in_api_client.user.create_actor()
    factories["federation.BlockedActor"](actor=user_actor)
    url = reverse(
        "api:v2:federation:actors-blocks",
        kwargs={"full_username": user_actor.full_username},
    )
    response = logged_in_api_client.get(url)
    assert response.status_code == 200


def test_user_cannot_get_blocked_users(factories, api_client):
    blocks = factories["federation.BlockedActor"]()
    url = reverse(
        "api:v2:federation:actors-blocks",
        kwargs={"full_username": blocks.actor.full_username},
    )

    response = api_client.get(url)
    assert response.status_code == 401


def test_domain_follow_post(factories, logged_in_api_client, mocker):
    actor = logged_in_api_client.user.create_actor()
    target_domain = factories["federation.Domain"](with_service_actor=True)
    original_receivers = signals.post_save.receivers.copy()
    signals.post_save.receivers = []

    url = reverse("api:v2:federation:domain-follows-list")
    response = logged_in_api_client.post(url, {"target": target_domain.name})
    assert response.status_code == 403

    actor.user.permission_settings = True
    actor.user.save()
    response = logged_in_api_client.post(url, {"target": target_domain.name})
    assert response.status_code == 201
    assert models.Follow.objects.filter(
        target=target_domain.service_actor, actor=actors.get_service_actor()
    ).exists()

    response = logged_in_api_client.post(url, {"target": target_domain.name})
    assert response.status_code == 400
    signals.post_save.receivers = original_receivers


def test_domain_follow_delete(factories, logged_in_api_client, mocker):
    logged_in_api_client.user.create_actor()
    target_domain = factories["federation.Domain"](with_service_actor=True)
    factories["federation.Follow"](
        target=target_domain.service_actor, actor=actors.get_service_actor()
    )
    user = logged_in_api_client.user
    user.permission_settings = True
    user.superuser = True
    user.save()
    original_receivers = signals.post_save.receivers.copy()
    signals.post_save.receivers = []
    url = reverse("api:v2:federation:domain-follows-list")
    response = logged_in_api_client.delete(url, {"target": target_domain.name})
    assert response.status_code == 204
    assert not models.Follow.objects.filter(
        target=target_domain.service_actor, actor=actors.get_service_actor()
    ).exists()
    signals.post_save.receivers = original_receivers
