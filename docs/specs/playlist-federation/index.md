## Playlist Federation

### The Issue

Playlists are a useful way to curate content and share curated lists of tracks. Currently, only local playlists are browsable in the pods. A user cannot add a playlist to their library/collection.

### Proposed Solution

Make playlists a federated object to allow them to be added to remote libraries/pods. Send playlist updates via federation activities.

### Feature Behavior

Users will be able to click on a "Follow playlist" button. The playlist content and the playlist itself will be added to the user's library section ("My library").

#### Backend

Adding a playlist to a library is an ActivityPub `Follow`. The follow request is made to an actor specially created for the playlist.
Endpoints and logic should follow the actual ActivityPub implementation :

- The follow request is accepted automatically if the playlist is public
- When accepted, the playlist is added to the local pod, the playlist actor is created has followed by the local actor

For better understandability, the playlist actor should be named after the playlist name and the user actor owning the playlist. For example, if John has a "Rock" playlist, the actor should be called: john_rock_playlist.
Add playlist update activities to notifications.

#### Frontend

- Add a "Follow" button that will call an ActivityPub follow request on the playlist actor.
- Update the playlist request in the "My library/Playlist" section to include followed playlist on top of owned playlist.
- Make a visual distinction between owned and followed playlist in this page (optional)

### Availability

- [ ] Admin panel
- [x] App frontend
- [ ] CLI

### Open Questions

- Frontend design: There isn't any space for followed content in the UI (either for user or playlist follow). A dedicated page could be created. At least a feed page should be create that regroup followed content update (user and playlist follows activities)

### Minimum Viable Product

### Next Steps
