from django.conf.urls import include
from django.urls import re_path

from funkwhale_api.common import routers as common_routers

from . import api

router = common_routers.OptionalSlashRouter()
v2_patterns = router.urls

v2_patterns += [
    re_path(
        r"^instance/",
        include(("funkwhale_api.instance.urls_v2", "instance"), namespace="instance"),
    ),
    re_path(
        r"^radios/",
        include(("funkwhale_api.radios.urls_v2", "radios"), namespace="radios"),
    ),
    re_path(
        r"^playlists/",
        include(
            ("funkwhale_api.playlists.urls_v2", "playlists"), namespace="playlists"
        ),
    ),
]

v2_paths = {
    pattern.pattern.regex.pattern
    for pattern in v2_patterns
    if hasattr(pattern.pattern, "regex")
}

filtered_v1_patterns = [
    pattern
    for pattern in api.v1_patterns
    if pattern.pattern.regex.pattern not in v2_paths
]

v2_patterns += filtered_v1_patterns

urlpatterns = [re_path("", include((v2_patterns, "v2"), namespace="v2"))]
