import logging

from config import plugins
from funkwhale_api.contrib.archivedl import tasks

from .funkwhale_startup import PLUGIN

logger = logging.getLogger(__name__)


@plugins.register_hook(plugins.TRIGGER_THIRD_PARTY_UPLOAD, PLUGIN)
def lauch_download(track, conf={}):
    tasks.archive_download.delay(track_id=track.pk, conf=conf)
