# Third party tracks download

## Issue

Has a user I cannot listen to tracks that are not on the funkwhale Network.

## Proposed solution

Has an admin I can add plugins that support downloading tracks from third party services

## Backend

When a track queryset is called with `with_playable_uploads` if no upload is found we trigger `plugins.TRIGGER_THIRD_PARTY_UPLOAD`.

`handle_stream` should filter the upload queryset to display manual upload before plugin upload

## Plugin

Plugins registering `TRIGGER_THIRD_PARTY_UPLOAD` should :

- trigger celery task. If not the queryset will take a long time to complete.
- create an upload with an associated file
- delete the upload if no file is succefully downloaded

An example can be found in `funkwhale_api.contrib.archivedl`

## Follow up

-The frontend should update the track object if `TRIGGER_THIRD_PARTY_UPLOAD`
`channels.group_send("instance_activity", {"type": "event.send", "text": "", "data": data})`
`InstanceActivityConsumer` `/front/src/init/webSocket.ts`

- trigger a channels group send so the frontend can update track qs when/if the upload is ready
- Third party track stream (do not download the file, only pass a stream)
