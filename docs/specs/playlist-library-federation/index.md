# Playlist libraries to share audio files

## The Issue

- As a user I want to share a list of tracks privately to my friends
- As a user I want to have a single container to curate my content (not playlist and libraries, only playlists)

## Proposed Solution

The users can request access to the playlist content to the playlist owner

## Feature Behavior

Users will be able to click on a "Request access to playlist audios files" button. This is a `LibraryFollow` request of the `playlist.library`. Not to be confused with the playlist follow request (see #-followup)

### Backend

#### Data model

`Playlist` one_to_one with `Library` through `library` field
`Upload` many_to_one with `Library` through `library` (reverse is `library.uploads`)
`Upload` has also a many_to_many with `Library` through `playlist_libraries` (the same upload can be share various time through various playlists). Reverse relation is `library.playlist_uploads`

We could migrate from O2M to M2M, but this is super complicated since : - it adds a lot of extra logic (you can't query the m2m if the instance is not save -> this generated problem to validate incoming AP objects) - having a built-in lib and playlist libs make verifications easier (only three built-in lib, playlist_lib are always private)

#### Workflow

Playlist activity -> library_scan(get the uploads) -> playlist_scan (set the upload.playlist_relation and create plts)

#### Federation

Since `Playlist` is the main object here, we use the `Playlist` activities to send the `Library` information on ActivitiPub.
There is no other reason to share the playlit.library to remote.

#### Migrations

1. Remote library are not changed
2. Local lib are not deleted but are assigned to a playlist
3. Libraries Follows are not touched
4. Remote want fetch local libs as always but they will need to update the data or fail (migrating uploads from `library` to `playlist_library`)

#### Done

- [x] `PlaylistViewSet` `add` `clear` `remove` update the uploads.playlist_libraries relationships
- [x] `PlaylistViewSet` `add` `clear` `remove` -> `schedule_scan` -> Update activity to remote -> playlist.library scan on remote
- [x] library and playlist scan delay are long (24h), force on ap update
- [x] make sure only owned upload are added to the playlist.library
- [x] update the "drop library" migrations to use the playlist.library instead of user follow
- [x] make sure user get the new libraries created after library drop
- [x] update the federation api : when we receive a fetch for a library the upload serializer need to know which lib (playlist lib or user lib)
- [x] Support library.playlist_uploads in library scan -> add playlist_uploads in items in library federation viewset
- [x] investigate library scan bug : don't delete old content of the lib (local cache?): we need to empty the playlist before the scan(not ideal but less work)
- [x] check actor has only have three built-in libs and upload.playlist_libraries is private after migration
- [x] Playlist discovery : fetch federation endpoint for playlists
- [ ] Seem like the federation fetch (either with fetch endpoint or retreive_ap_obj) is deleting the `privacy_level` since `audience` can only be public or null. Avoid `privacy_level` to be updated if it a local playlist.

## Follow up

- [ ] Add the frontend playlist button in the new ui
- [ ] Playlist discovery : display playlist fid in the frontend
- [ ] Document : The user that want to federate need to activate remote activities in it's user settings. Even if the library is public the playlist activities will not be sended to remote -> We need to implement a followers activity setting (#2362)
- [ ] allow users to change the upload to another built-in lib, make sure the upload is not delete (we would loose the playlist_library relation) but only updated

- [ ] Playlist discovery : add the playlist to my playlist collection = follow request to playlist
- [ ] Playlist Track activity (to avoid having to refetch the whole playlist)
- [ ] Add a popover button to force playlist scan ? or make playlist scan delay shorter ?
