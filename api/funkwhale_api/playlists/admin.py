from funkwhale_api.common import admin

from . import models


@admin.register(models.Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ["name", "actor", "privacy_level", "creation_date"]
    search_fields = ["name"]
    list_select_related = True


@admin.register(models.PlaylistTrack)
class PlaylistTrackAdmin(admin.ModelAdmin):
    list_display = ["playlist", "track", "index"]
    search_fields = ["track__name", "playlist__name"]
    list_select_related = True


@admin.register(models.PlaylistScan)
class LibraryScanAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "playlist",
        "actor",
        "status",
        "creation_date",
        "modification_date",
        "status",
        "total_files",
        "processed_files",
        "errored_files",
    ]
    list_select_related = True
    search_fields = ["actor__username", "playlist__name"]
    list_filter = ["status"]
