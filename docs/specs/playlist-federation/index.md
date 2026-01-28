# Playlist Federation

## The Issue

Playlists are a useful way to curate content and share curated lists of tracks. Currently, only local playlists are browsable in the pods. A user cannot add a playlist to their library/collection.

## Proposed Solution

Make playlists a federated object to allow them to be added to remote libraries/pods. Send playlist updates via federation activities.

## Feature Behavior

Users will be able to click on a "Follow playlist" button. The playlist content and the playlist itself will be added to the user's library section ("My library").

### Backend

In the context of an user A following user B owner of Playlist B. The User A will receive an `Create` activity when User B create a playlist. `Update` activities with `Playlist` objects will be send to the Instance A service actor. They **don't** contain PlalistTracks, only the playlist metatadat is added to database. Playlist tracks are imported thanks to the playlist scan. Or in some case through playlist track create activity.

Since `PlaylistTrack` object can be updated a lot, instead of sending a bunch of `PlaylistTrack` updates we only send one `Playlist` update (default is on per day, defined in `schedule_scan` function). We use a celery task, it will send an playlist `Update` activity to remote servers if playlist is a local one and will trigger a playlist scan if playlist is a remote one.

To follow activitypub standard and since playlist metadata update shouldn't happen to much we will trigger a playlist scan each time we receive a playlist update activiy.

The scan will get the playlist track by querying the playlist federation endpoint. It return a ordered Collection. Each element of the collection is added to the local database.
When the scan start we delete all `PlaylistTracks` from the playlist. I could be more optimized to send `Delete activities` on `PlaylistTrack` objects. But since were are not sure and since and way more easy to delete the tracks we do it this way for now.

The `PlaylistTrack` object will only support `Create` activities, since update or delete would trigger a lot of them and they are not interesting (we use playlist scan instead).
`Create` activities will be send to User A followers.
If a `PlaylistTrack` `Create` is sent and the index is not the good one it eans the receiving instance isn't up to date -> we trigger a full playlistscan

This will allow to receive notification when a user Add a track to a playlist. Other playlist actions will be silent but the playlist will be kept updated.

### Frontend

- Add a "Follow" button that will call an ActivityPub follow request on the playlist actor.
- Update the playlist request in the "My library/Playlist" section to include followed playlist on top of owned playlist.
- Make a visual distinction between owned and followed playlist in this page (optional)

## Availability

- [ ] Admin panel
- [x] App frontend
- [ ] CLI

## Open Questions

- Frontend design: There isn't any space for followed content in the UI (either for user or playlist follow). A dedicated page could be created. At least a feed page should be create that regroup followed content update (user and playlist follows activities)

## Minimum Viable Product

## Next Steps

- [ ] Add playlist update activities to notifications.
- [ ] Create a frontend thread with Update Playlist activities
- [ ] Update the federation search to include Playlist objects
- [ ] Adding a playlist to a user library as an ActivityPub `Like`
- [ ] Check if sending whole big playlists become a problem.
