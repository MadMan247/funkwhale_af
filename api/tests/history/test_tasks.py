import pytest
from django.core.paginator import Paginator

from funkwhale_api.federation import serializers as federation_serializers
from funkwhale_api.history import tasks


def test_scan_listenings_page_fetches_page_and_creates_listenings(
    mocker, factories, r_mock
):
    scan_next = mocker.patch("funkwhale_api.history.tasks.scan_listenings_page.delay")

    save = mocker.patch(
        "funkwhale_api.federation.serializers.ListeningSerializer.save",
        autospec=True,
    )

    actor = factories["federation.Actor"]()

    listenings = [factories["history.Listening"](actor=actor) for _ in range(5)]

    page_conf = {
        "actor": actor,
        "id": actor.fid,
        "page": Paginator(listenings, 3).page(1),
        "item_serializer": federation_serializers.ListeningSerializer,
    }

    listenings[0].__class__.objects.filter(pk__in=[l.pk for l in listenings]).delete()

    page = federation_serializers.CollectionPageSerializer(page_conf)

    r_mock.get(page.data["id"], json=page.data)

    tasks.scan_listenings_page(
        actor_id=actor.pk,
        page_url=page.data["id"],
    )

    # 3 items on page
    assert save.call_count == 3
    scan_next.assert_called_once_with(
        actor_id=actor.pk,
        page_url=page.data["next"],
    )


def test_scan_listenings_page_trigger_next_page_scan_skip_if_same(
    mocker, factories, r_mock
):
    patched_scan = mocker.patch(
        "funkwhale_api.history.tasks.scan_listenings_page.delay"
    )
    mocker.patch(
        "funkwhale_api.federation.serializers.ListeningSerializer.save",
        return_value=None,
    )

    actor = factories["federation.Actor"]()

    listenings = factories["history.Listening"].build_batch(
        size=5,
        actor=actor,
    )

    page_conf = {
        "actor": actor,
        "id": actor.fid,
        "page": Paginator(listenings, 3).page(1),
        "item_serializer": federation_serializers.ListeningSerializer,
    }

    page = federation_serializers.CollectionPageSerializer(page_conf)
    data = page.data
    data["next"] = data["id"]

    r_mock.get(data["id"], json=data)
    tasks.scan_listenings_page(actor_id=actor.pk, page_url=data["id"])

    patched_scan.assert_not_called()


def test_start_listenings_scan_fetches_collection_and_calls_scan_page(
    mocker, factories, r_mock
):
    actor = factories["federation.Actor"]()
    scan = factories["history.ListeningsScan"]()
    factories["history.Listening"].create_batch(size=10, actor=actor)

    scan_page = mocker.patch("funkwhale_api.history.tasks.scan_listenings_page.delay")

    collection = federation_serializers.IndexSerializer(
        {
            "id": actor.fid,
            "type": "Collection",
            "totalItems": 10,
            "first": f"{actor.fid}?page=1",
            "items": factories["history.Listening"].create_batch(size=10, actor=actor),
        }
    )
    collection_url = scan.target.fid + "/listens"
    r_mock.get(collection_url, json=collection.data)

    tasks.start_listenings_scan(listenings_scan_id=scan.pk)

    scan_page.assert_called_once_with(
        actor_id=scan.actor.pk,
        page_url=collection.data["first"],
    )


def test_start_listenings_scan_raises_on_error_response(factories, r_mock):
    actor = factories["federation.Actor"]()

    r_mock.get(
        actor.fid,
        status_code=404,
        json={"detail": "Not found"},
    )

    with pytest.raises(Exception):
        tasks.start_listenings_scan(
            listenings_scan_id=actor.pk,
        )


def test_start_listenings_scan_returns_if_no_first_page(mocker, factories, r_mock):
    actor = factories["federation.Actor"]()
    scan_page = mocker.patch("funkwhale_api.history.tasks.scan_listenings_page.delay")
    scan = factories["history.ListeningsScan"]()

    collection = federation_serializers.IndexSerializer(
        {
            "id": actor.fid,
            "type": "Collection",
            "totalItems": 0,
            "items": [],
        }
    )

    collection_url = scan.target.fid + "/listens"

    r_mock.get(collection_url, json=collection.data)

    tasks.start_listenings_scan(
        listenings_scan_id=scan.pk,
    )

    scan_page.assert_not_called()
