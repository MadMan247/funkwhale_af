# Privacy features for federation

## General logic

Two level of privacy for activities :

- from the Actor of the activities
- from the Object of the activities

### User level privacy_level

Check is done in `activity_pass_user_privacy_level` but only works if `actor` is passed within the `context`. This applies to object that don't have their own privacy_level settings :

- `Listening`
- `TrackFavorite`

```{warning}
This doesn't apply to Playlits and Uploads
```

### Object privacy_level

`Playlist` and `Library` support they own privacy level. Check is done in `activity_pass_object_privacy_level` for AP activities and on `has_playlist_access` for the federation views. Other objects should be added manually to this function.
`PlaylistTrack` follow the `Playlist` privacy_level setting.
`Upload` follow the `Library` privacy_level setting.

## Followers privacy_level for User

If a user follow a local user we don't need to send ActivityPub activities since the data is already in our db. We can use the local database the fetch the data. That's why Funkwhale outbox will always discard activities that are not public. But this need to be updated to support `followers` privacy level. Some warning should be displayed to the users to explain that setting a privacy_level to `followers` will send the data to remote server (#2532). This means we need to trust the remote server admins to follow our privacy_level wish. In other words when you trust your followers your also trust the admins of your followers.
