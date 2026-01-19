# Followers privacy level

## The issue

> As a user I want to share my audio file with my followers

Implement the followers privacy level for UserFollow and Playlist

## ActivityPub

### Bulk update upload

We use bulk updates to move `Uploads` from one built-in library to another one. We need to create a new `Activity` that send a collection of `Uploads` (`Audio` in AS vocabulary) to avoid rescanning the whole library.

- [x] Create a new `AudioCollection` AP object
- [x] Create `Update` and `Delete` activities for `AudioCollection`
- [x] Create `AudioCollectionSerializers` to bulk_update the uploads
- [x] Trigger the activity on bulk_update uploads

### Side development

To only send activities to one remote actor in a simple way we allow the library to be fetched by remote services actor if their domain has a approced follow. This is done in `Library.viewable_by`
