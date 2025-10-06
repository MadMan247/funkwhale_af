# Followers privacy level

## The issue

> Has a user I want to share my audio file with my followers

Implement the followers privacy level for UserFollow and Playlist

## ActivityPub

### Bulk update upload

We use bulk updates to moove `Uploads` from on built-in library to another one. We need to create a new `Activity` that send a collection of `Uploads` (`Audio` in AS vocabulary) to avoid rescanning the whole library.

- [ ] Create a new `AudioCollection` AP object
- [ ] Create `Update` activity for `AudioCollection`
- [ ] Create `AudioCollectionSerializers` to bulk_update the uploads
- [ ] Trigger the activity on bulk_update uploads
