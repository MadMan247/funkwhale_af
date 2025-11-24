import pytest
from django.urls import reverse


@pytest.mark.parametrize("level", ["instance", "me", "followers"])
def test_privacy_filter(preferences, level, factories, api_client):
    preferences["common__api_authentication_required"] = False
    user = factories["users.User"](privacy_level=level)
    factories["history.Listening"](actor__user=user, privacy_level=level)
    url = reverse("api:v2:history:listenings-list")
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data["count"] == 0


def test_privacy_filter_following(preferences, factories, logged_in_api_client):
    actor = logged_in_api_client.user.create_actor()

    listening = factories["history.Listening"](privacy_level="followers")
    factories["federation.Follow"](actor=actor, target=listening.actor, approved=True)
    url = reverse("api:v2:history:listenings-list")
    response = logged_in_api_client.get(url)
    assert response.status_code == 200
    assert response.data["count"] == 1
