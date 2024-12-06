import pytest
from django.http import Http404
from rest_framework.views import APIView

from funkwhale_api.common import permissions


def test_owner_permission_owner_field_ok(nodb_factories, api_request):
    playlist = nodb_factories["playlists.Playlist"]()
    view = APIView.as_view()
    permission = permissions.OwnerPermission()
    request = api_request.get("/")
    setattr(request, "user", playlist.user)
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
    [("me", True), ("followers", False), ("instance", True), ("everyone", True)],
)
def test_privacylevel_permission_me(
    factories, api_request, anonymous_user, privacy_level, expected, mocker
):
    user = factories["users.User"](privacy_level=privacy_level)
    user.create_actor()
    view = APIView.as_view()
    permission = permissions.PrivacyLevelPermission()
    request = api_request.get("/")
    setattr(request, "user", user)

    check = permission.has_object_permission(request, view, user.actor)
    assert check is expected


@pytest.mark.parametrize(
    "privacy_level,expected",
    [("me", False), ("followers", True), ("instance", False), ("everyone", True)],
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
