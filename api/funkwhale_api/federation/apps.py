import logging

from django.apps import AppConfig
from dynamic_preferences.signals import preference_updated

logger = logging.getLogger(__name__)


def trigger_tasks_on_preference_update(
    sender, section, name, old_value, new_value, instance, **kwargs
):
    logger.debug(
        f"Preference {name} in section {section} changed from {old_value} to {new_value}"
    )
    if (
        section == "federation"
        and name == "auto_federation"
        and new_value is True
        and new_value != old_value
    ):
        from celery import chain

        from . import tasks

        chain(
            tasks.discover_domains_from_funkwhale_audio.si(),
            tasks.discover_domains_from_known_ones.si(),
        ).apply_async()


class FederationConfig(AppConfig):
    name = "funkwhale_api.federation"

    def ready(self):
        super().ready()
        preference_updated.connect(trigger_tasks_on_preference_update)
