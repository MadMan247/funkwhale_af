# Library drop in favor of playlist

## Issue

We now have playlist, use complained about library not being clearly defined.

## Proposed solution

## Backend

A new endpoint to move upload from one library to another : `PATCH` on `api/v2/uploads/bulk-update` with `[{"uuid": "uuid1", "privacy_level": "public"}]`

### Migration from Libraries to Playlist

New `description` field on playlist, to inherit from the `description` field of Library

Library Follows will be transformed to user follow.
The schedule_scan function of the library still exist and allow federation of audio content

During user creation, built-in libraries are generated automatically by `create_user_libraries`
