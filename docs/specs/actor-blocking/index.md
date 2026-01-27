# Actor-level blocking and muting

## The issue

There are various types of actors within the Funkwhale network: Funkwhale users, ActivityPub actors, artists (has channels or has funkwhale object) and podcasts (only has channels).

Funkwhale users can generate various activities and content on the Funkwhale network. Users should be able to block activities from other ActivityPub actors (which include artists and podcasts channels). Blocked Users should be prevented to interact with the blocking user, even in remotes pods.

## Proposed solution

Give Funkwhale Users the ability to block :

- Artists (already implemented)
- Channels (both artist and podcast channels)
- ActivityPub actors

## Feature behavior

### Blocking users

When one user blocks another, no information may be shared between them. Blocking is a unilateral action that can be taken by both **requesting** and **target** actors to prevent the other from interacting with them.

#### API behavior

New model`BlockedActor` with attributes : `actor`, `target`.

Block requests should be handled by an endpoint using a `POST` request. This request must immediately return a status message to the client.

```text
POST /api/v2/federation/actors/{full_username}/block
```

Each activity request from the blocking actor should filter out blocked actor activities.
Activity request from the blocked actor should not change. The public profile and public data must remain accessible to avoid leaking the fact he his blocked.

List of endpoints to apply the filter to :

- [x] Listenings
- [x] Favorites
- [x] Playlists
- [x] Uploads and denormalization table (this way the blocked actor thinks it still follow the blocking actor but he doesn't have access to the content)

#### ActivityPub behavior

If the the **blocked user** is on a different server than the **blocking user**, the request is handled using the [ActivityPub `Block` activity][block] with the **blocked user's** [`Actor`][actor] as a target.

1. A [`Block` activity][block] is posted to the remote server with the **blocked user's** [`Actor`][actor] the target. The recipient `to` can either be the service actor or the blocked user has mastoton does : https://docs.joinmastodon.org/spec/activitypub/#Block.

:::{warning}
As noted in the ActivityPub spec, the **blocked user** must _not_ be informed of the `Block` activity.
:::

#### Web app behavior

When a **blocking user** blocks a **blocked user**, the UI must update to visually indicate that the action has succeeded. All activities relating to the **blocked user** must be visually hidden.

If a **blocking user** navigates to the profile of a **blocked user** who has blocked them, the UI _must not_ reflect that they are blocked. The **blocking user** must be able to send a follow request which is _not_ sent to the **blocked user**.

### Unblocking users

**Blocking users** can unilaterally reverse blocks they have imposed on **blocked users**. This enables them to request to follow the **blocked user's** activities again.

#### API behavior

Unblock requests should be handled by an endpoint using a `POST` request. This request must immediately return a status message to the client.

```text
POST /api/v2/federation/actors/{full_username}/unblock
```

#### ActivityPub behavior

If the **blocked user** is on a different server to the **blocking user**, the request is handled using the [ActivityPub `Undo` activity][undo].

#### Web app behavior

When a **blocking user** unblocks a **blocked user**, the UI must update to visually indicate that the action has succeeded. The **Follow** button must become active and interactive again.

### Getting the list of blocked actor

```text
GET /api/v2/federation/actors/{full_username}/blocks
```

### Channels blocking

Since each channel has an actor and
The user should be able to click on a button to call
`POST /api/v2/federation/actors/{full_username}/block`

This endpoint should trigger :

1. ActivityPub actors blocking.
2. Funkwhale display blocking (A simple filter into `ChannelFilter` that is called by the channel view.)

### Design

- User block mockups are done : https://design.funkwhale.audio/#/view/e3a187f0-0f5e-11ed-adb9-fff9e854a67c?page-id=e61451a5-6d56-8015-8003-c3dd410c8f50&section=interactions&frame-id=13bd6d1c-f5ce-8074-8003-b82e985e419d&index=3&share-id=a4e0101a-252c-80ef-8003-c7c73d99d4b7
- Maybe we want to add a page to manage blocked users ? Where we can find a list of all blocked users.

Add channels blocked mockup.

## Availability

> Where is this going to be available to end users? [name=Sporiff]

- [ ] Admin panel
- [x] App frontend
- [ ] CLI

## Responsible parties

- Design need to be draw
- Backend need to be implemented
- Frontend need to be implemented

### Next steps

- [ ] blocking an actor should automatically block all channels owned by this actor ?

###### tags: `blocking` `userfollow`
