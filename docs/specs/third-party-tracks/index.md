# Third party tracks download

## Issue

Has a user I cannot listen to tracks that are not on the funkwhale Network.

## Proposed solution

Has an admin I can add plugins that support downloading tracks from third party services

## Backend

When a radio or playlist queryset is called if no upload is found we trigger `plugins.TRIGGER_THIRD_PARTY_UPLOAD`.

RadioViewSet.tracks and PlaylistViewSet.tracks are concerned. These endpoints can be called a lot, `THIRD_PARTY_UPLOAD_MAX_UPLOADS` variable allows to limits the amount af requests that are sended to the tird party service.

`handle_stream` should filter the upload queryset to display manual upload before plugin upload

## Plugin

Plugins registering `TRIGGER_THIRD_PARTY_UPLOAD` should :

- trigger celery task. If not the queryset will take a long time to complete.
- create an upload with an associated file
- delete the upload if no file is succefully downloaded
- check if an upload has already been triggered to avoid overloading Celery

An example can be found in `funkwhale_api.contrib.archivedl`

To enable the archive-dl plugin : `FUNKWHALE_PLUGINS=funkwhale_api.contrib.archivedl`

## Follow up

-The frontend should update the track object if `TRIGGER_THIRD_PARTY_UPLOAD`
`channels.group_send("instance_activity", {"type": "event.send", "text": "", "data": data})`
`InstanceActivityConsumer` `/front/src/init/webSocket.ts`

- trigger a channels group send so the frontend can update track qs when/if the upload is ready
- Third party track stream (do not download the file, only pass a stream)

- Allow `THIRD_PARTY_UPLOAD_MAX_UPLOADS` to be set at the plugin level -> allow admin to set plugin conf in ui -> create PluginAdminViewSet
