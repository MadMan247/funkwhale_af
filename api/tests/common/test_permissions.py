import pytest
from django.http import Http404
from rest_framework.views import APIView

from funkwhale_api.common import permissions


def test_owner_permission_owner_field_ok(nodb_factories, api_request):
    playlist = nodb_factories["playlists.Playlist"]()
    nodb_factories["users.User"](actor=playlist.actor)
    view = APIView.as_view()
    permission = permissions.OwnerPermission()
    request = api_request.get("/")
    setattr(request, "user", playlist.actor.user)
    setattr(view, "owner_field", "actor.user")
    check = permission.has_object_permission(request, view, playlist)

    assert check is True


def test_owner_permission_owner_field_not_ok(
    anonymous_user, nodb_factories, api_request
):
    playlist = nodb_factories["playlists.Playlist"]()
    view = APIView.as_view()
    permission = permissions.OwnerPermission()
    request = api_request.get("/")
    setattr(request, "user", anonymous_user)
    setattr(view, "owner_field", "actor.user")
    with pytest.raises(Http404):
        permission.has_object_permission(request, view, playlist)


def test_owner_permission_read_only(anonymous_user, nodb_factories, api_request):
    playlist = nodb_factories["playlists.Playlist"]()
    view = APIView.as_view()
    setattr(view, "owner_checks", ["write"])
    permission = permissions.OwnerPermission()
    request = api_request.get("/")
    setattr(request, "user", anonymous_user)
    check = permission.has_object_permission(request, view, playlist)

    assert check is True


@pytest.mark.parametrize(
    "privacy_level,expected",
    [("me", False), ("followers", False), ("instance", False), ("everyone", True)],
)
def test_privacylevel_permission_anonymous(
    factories, api_request, anonymous_user, privacy_level, expected
):
    user = factories["users.User"](privacy_level=privacy_level)
    user.create_actor()
    view = APIView.as_view()
    permission = permissions.PrivacyLevelPermission()
    request = api_request.get("/")
    setattr(request, "user", anonymous_user)

    check = permission.has_object_permission(request, view, user.actor)
    assert check is expected


@pytest.mark.parametrize(
    "privacy_level,expected",
    [("me", False), ("followers", False), ("instance", True), ("everyone", True)],
)
def test_privacylevel_permission_instance(
    factories, api_request, anonymous_user, privacy_level, expected, mocker
):
    user = factories["users.User"](privacy_level=privacy_level)
    user.create_actor()
    request_user = factories["users.User"](with_actor=True)
    view = APIView.as_view()
    permission = permissions.PrivacyLevelPermission()
    request = api_request.get("/")
    setattr(request, "user", request_user)

    check = permission.has_object_permission(request, view, user.actor)
    assert check is expected


@pytest.mark.parametrize(
    "privacy_level,expected",
    [("me", True), ("followers", True), ("instance", True), ("everyone", True)],
)
def test_privacylevel_permission_me(
    factories, api_request, privacy_level, expected, mocker
):
    user = factories["users.User"](privacy_level=privacy_level)
    user.create_actor()
    view = APIView.as_view()
    permission = permissions.PrivacyLevelPermission()
    request = api_request.get("/")
    setattr(request, "user", user)

    check = permission.has_object_permission(request, view, user.actor)
    assert check is expected


# "me" expects true since the object can be private but share with followers
@pytest.mark.parametrize(
    "privacy_level,expected",
    [("me", True), ("followers", True), ("instance", False), ("everyone", True)],
)
def test_privacylevel_permission_followers(
    factories, api_request, anonymous_user, privacy_level, expected, mocker
):
    user = factories["users.User"](privacy_level=privacy_level)
    user.create_actor()
    user_follow = factories["federation.Follow"](target=user.actor, approved=True)
    view = APIView.as_view()
    permission = permissions.PrivacyLevelPermission()
    request = api_request.get("/")
    setattr(request, "user", anonymous_user)
    setattr(request, "actor", user_follow.actor)

    check = permission.has_object_permission(request, view, user.actor)
    assert check is expected


def test_privacylevel_permission_block_actor(
    factories,
    api_request,
    anonymous_user,
):
    user = factories["users.User"](privacy_level="everyone")
    user.create_actor()
    blocks = factories["federation.BlockedActor"](target=user.actor)
    view = APIView.as_view()
    permission = permissions.PrivacyLevelPermission()
    request = api_request.get("/")
    setattr(request, "user", anonymous_user)
    setattr(request, "actor", blocks.actor)

    check = permission.has_object_permission(request, view, user.actor)
    assert check is False

    blocks = factories["federation.BlockedActor"](actor=user.actor)
    setattr(request, "user", anonymous_user)
    setattr(request, "actor", blocks.target)

    check = permission.has_object_permission(request, view, user.actor)
    assert check is False
