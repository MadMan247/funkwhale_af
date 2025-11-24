from django.conf.urls import include
from django.urls import re_path

from funkwhale_api.common import routers as common_routers

router = common_routers.OptionalSlashRouter()
v1_patterns = router.urls

v1_patterns += [
    re_path(
        r"^instance/",
        include(("funkwhale_api.instance.urls", "instance"), namespace="instance"),
    ),
]

urlpatterns = [re_path("", include((v1_patterns, "v1"), namespace="v1"))]
