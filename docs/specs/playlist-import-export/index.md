# Playlist Import export

## The Issue

Playlists cannot be imported/exported.

## Proposed Solution

Add endpoints to allow import/export.

## Feature Behavior

Users will be able to click on a "Download playlist" or "Rebuild playlist" button. The playlist content and the playlist itself will be added to the user's library section ("My library").

### Backend

GET from the `/api/v2/playlists/{guid}` endpoint and receive either:

- `application/json`: a summary of the playlist
- `application/octet-stream`: the full exported XSPF file

PATCH the `/api/v2/playlists/{guid}` endpoint using either:

- `application/json`: updated fields for the playlist metadata
- `application/octet-stream`: an updated XSPF file containing updated information about the playlist7

POST to the `/api/v2/playlists` endpoint and post either:

- `application/json`: a small amount of metadata about the created playlist
- `application/octet-stream`: an XSPF file containing the playlist data

GET from the `/api/v2/playlists/{guid}/artists` endpoint and receive either:

- `application/json`: a list a artist present in the playlist

GET from the `/api/v2/playlists/{guid}/albums` endpoint and receive either:

- `application/json`: a list a albums present in the playlist
