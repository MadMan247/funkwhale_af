import pytest
from django import urls


@pytest.mark.parametrize(
    "url",
    [
        "/api/v2/artists",
        "/api/v2/albums",
        "/api/v2/tracks",
        "/api/v2/libraries",
        "/api/v2/uploads",
        "/api/v2/playlists",
        "/api/v2/favorites/tracks",
        "/api/v2/auth/registration/verify-email",
        "/api/v2/auth/registration/change-password",
        "/api/v2/auth/registration/account-confirm-email/key",
        "/api/v2/history/listenings",
        "/api/v2/radios/sessions",
        "/api/v2/users/me",
        "/api/v2/federation/follows/library",
        "/api/v2/manage/accounts",
        "/api/v2/oauth/apps",
        "/api/v2/moderation/content-filters",
        "/api/v2/instance/settings",
        "/api/v2/instance/nodeinfo/2.1",
    ],
)
@pytest.mark.parametrize("suffix", ["", "/"])
def test_optional_trailing_slash(url, suffix):
    match = urls.resolve(url + suffix)
    assert match is not None
