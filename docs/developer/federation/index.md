# Funkwhale federation

```{note}
We aim to keep this document up-to-date to reflect the current state of federation. If you notice an issue, please open a thread on [our forum](https://forum.funkwhale.audio/t/documentation).
```

Funkwhale is a federated platform. Funkwhale pods can share information between one another, and can also communicate with other {term}`Fediverse` software. This article outlines which tools we use, our approach to federation, and how we implement standards.

```{contents}
:local:
:depth: 2
```

```{toctree}
---
maxdepth: 1
---

objects
```

## Technologies and standards

Funkwhale's federation is built on top of the following technologies:

- [`ActivityPub`](https://www.w3.org/TR/activitypub/): Our federation protocol
- [`HTTP Signatures`](https://www.ietf.org/archive/id/draft-ietf-httpbis-message-signatures-01.html): A library for authenticating messages sent over the federation
- [`Webfinger`](https://tools.ietf.org/html/rfc7033): A protocol for discovering resources using readable names
- [`ActivityStreams`](https://www.w3.org/TR/activitystreams-core/) and [`ActivityStreams vocabulary`](https://www.w3.org/TR/activitystreams-vocabulary/): Our approach to structuring messages

We plan for support [`JSON-LD signatures`](https://w3c-dvcg.github.io/ld-signatures/) in the future as an alternative to `HTTP Signatures`.

## Our philosophy

Funkwhale aims to align with the above specifications where possible to maintain compatibility with other ActivityPub-aware platforms. This documentation covers where we have departed from the specifications.

While we will always aim for compatibility with other services where it makes sense, Funkwhale to Funkwhale interaction is our focus. We use these standards to support activities and objects that fit in with our use cases, such as **follows** and **likes**.

## Internal logic

This section covers how we handle federation within the Funkwhale ecosystem.

### Database schema

We use ActivityPub entities as a guide when creating [our models](https://dev.funkwhale.audio/funkwhale/funkwhale/blob/develop/api/funkwhale_api/federation/models.py) and database schemas. This ensures compatibility with other ActivityPub projects.

Funkwhale pods store received activities payloads in the database before attempting to process or deliver them. This enables us to debug federation issues, resend messages, or process historical activities that weren't previously supported.

Funkwhale users are associated to an `Actor`. Remote and local actors are stord in the same database table. Any federated entities, such as uploads, are linked to the `Actor` rather than the user. We don't distinguish between local and remote users on the database level.

### Activity creation and delivery

Actions carried out by a local actor can trigger an `Activity`. This is the equivalent to posting an activity to an object. Funkwhale creates an object with the activity payload and stores it in the `Activity` table. Funkwhale triggers 2 types of deliveries:

1. Local recipients: Funkwhale creates an `InboxItem` linked to the activity for each local recipient. Funkwhale then creates a feed of available inbox items for each local actor. Items in this feed have both a `Read` and `Unread` status to allow users to mark items as handled.
2. Remote recipients: Funkwhale collects the inboxes and shared inbox URLs of all remote recipients. Funkwhale then creates a `Delivery` object and linked to the initial activity and the inbox or shared inbox URL. The worker uses this `Delivery` object to post the activity to the correct inbox.

When a local inbox receives an activity from a remote actor, it ends up in their inbox for them to handle.

Funkwhale doesn't support all activities. Our routing logic enables the software to handle supported activities and discard unsupported ones. When Funkwhale receives an activity it checks if there is a route to handle it. If there is, Funkwhale calls a dedicated handler.

For example: if Funkwhale receives an [`activity-create`](#create) activity for an `object-audio` object, Funkwhale calls a handler to:

- Persist the data in the local `Upload` table
- Retrieve data associated with the audio

You can find the code for our routing logic here:

- [Routing logic for activities](https://dev.funkwhale.audio/funkwhale/funkwhale/blob/develop/api/funkwhale_api/federation/routes.py)
- [Delivery logic for activities](https://dev.funkwhale.audio/funkwhale/funkwhale/blob/develop/api/funkwhale_api/federation/tasks.py)

## Service actor

Funkwhale uses a dedicated service actor to send messages or authenticate fetches. This actor isn't associated to a user.

You can query a pod's nodeinfo endpoint to return the ID of the service actor in the `metadata > actorId` field. See the [API explorer](https://docs.funkwhale.audio/swagger/) for more information about this endpoint.

Funkwhale considers a pod's service actor to be an authoritative source for activities associated with **all** objects on its pod's domain. If the service actor sends an activity linked to an object on its domain, remote pods will recognize its authority.

## Audio fetching on restricted libraries

[`Library` objects](#library) and [`Audio` objects] are subject to the following access rules:

::::{tab-set}

:::{tab-item} Library

- Public libraries can be accessed by actors without restriction
- Restricted libraries can only be accessed if the HTTP request is signed by an actor who has an associated **approved** [`Follow` activity](#follow)

:::

:::{tab-item} Audio

- Audio items in public libraries can be accessed by actors without restriction
- Audio items in restricted libraries can only be accessed if the HTTP request is signed by an actor who has an associated **approved** [`Follow` activity](#follow)

:::

::::

## Supported activities

### Follow

A **follow** enables actors to access and retrieve content from other actors as soon as it updates.

::::{dropdown} Supported on

- [Library objects](#library)
- [Actor](https://www.w3.org/TR/activitypub/#actors)

::::

#### Internal logic

When Funkwhale receives a follow on a [library object](#library), it performs one of the following actions depending on the library's visibility:

- Automatically accept: If the library is public, Funkwhale automatically accepts the follow activity. Funkwhale sends a notification to the owner of the library and an [`Accept`](#accept) activity to the actor who sent the follow
- Accept request: If the library isn't public, Funkwhale sends a notification to the library owner. If the owner approves the request, Funkwhale sends an [`Accept`](#accept) activity to the actor who sent the follow

Funkwhale uses the library follow status to grant access to the actor who sent the follow request. If the library isn't public and the owner doesn't send an approval, the requesting actor can't access the library's content.

For User's actors the logic is the same but we use the privacy_level of the user instead of the public to automaically accept the Follow.

#### Checks

Funkwhale ensures the activity is being sent to the library's owner before handling it.

#### Example

In this example, **Alice** sends a follow activity for a [library object](#library) owned by **Bob**.

```{code-block} json
{
  "@context": [
      "https://www.w3.org/ns/activitystreams",
      "https://w3id.org/security/v1",
      {}
  ],
  "type": "Follow",
  "id": "https://music.rocks/federation/actors/Alice#follows/99fc40d7-9bc8-4c4a-add1-f637339e1ded",
  "actor": "https://music.rocks/federation/actors/Alice",
  "to": ["https://awesome.music/federation/actors/Bob"],
  "object": "https://awesome.music/federation/music/libraries/dc702491-f6ce-441b-9da0-cecbed08bcc6"
}
```

#### Supported Activities

Activities sent to followings users (or to the world if the account is set to public) are :

- [Listen](#listen)
- [Likes](#like)

### Accept

The `Accept` activity sends a positive response, such as confirming a [`Follow` activity](#follow).

::::{dropdown} Supported on

- `Activity` objects

::::

#### Internal logic

When Funkwhale receives an `Accept` activity related to a [`Follow`](#follow) activity, it marks the `Follow` as accepted in the database. If the `Follow` activity relates to a [`Library` object](#library), the requester receives future activities associated with the library. This includes [`Create`](#create), [`Audio`](#audio), and [`Delete`](#delete) activities. They can also browse and download the library's audio files. See the section on [Audio fetching on restricted libraries](./index.md#audio-fetching-on-restricted-libraries) for more details.

#### Checks

Funkwhale ensures the activity is sent by the library's owner before handling it.

#### Example

In this example, **Bob** accepts a follow request from **Alice**.

```{code-block} json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/security/v1",
    {}
  ],
  "type": "Accept",
  "id": "https://music.rocks/federation/actors/Alice#follows/99fc40d7-9bc8-4c4a-add1-f637339e1ded/accept",
  "to": ["https://music.rocks/federation/actors/Alice"],
  "actor": "https://awesome.music/federation/actors/Bob",
  "object": {
    "id": "https://music.rocks/federation/actors/Alice#follows/99fc40d7-9bc8-4c4a-add1-f637339e1ded",
    "type": "Follow",
    "actor": "https://music.rocks/federation/actors/Alice",
    "object": "https://awesome.music/federation/music/libraries/dc702491-f6ce-441b-9da0-cecbed08bcc6",
  },
}
```

### Undo

::::{dropdown} Supported on

- [`Follow` objects](#follow)

::::

#### Internal logic

When Funkwhale receives an `Undo` activity, it deletes the corresponding `Follow` from the database.

#### Checks

Funkwhale ensures the request actor is the same actor who sent the `Follow` activity before handling it.

#### Example

In this example, **Alice** notifies **Bob** that she's undoing her follow.

```{code-block} json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/security/v1",
    {}
  ],
  "type": "Undo",
  "id": "https://music.rocks/federation/actors/Alice#follows/99fc40d7-9bc8-4c4a-add1-f637339e1ded/accept",
  "to": ["https://awesome.music/federation/actors/Bob"],
  "actor": "https://music.rocks/federation/actors/Alice",
  "object": {
    "id": "https://music.rocks/federation/actors/Alice#follows/99fc40d7-9bc8-4c4a-add1-f637339e1ded",
    "type": "Follow",
    "actor": "https://music.rocks/federation/actors/Alice",
    "object": "https://awesome.music/federation/music/libraries/dc702491-f6ce-441b-9da0-cecbed08bcc6",
  },
}
```

### Create

::::{dropdown} Supported on

- [`Audio` objects](#audio)

::::

#### Internal logic

```{note}
See [the `Audio` object reference](#audio) for details on the object's structure.
```

When Funkwhale receives a `Create` activity with an [`Audio` object](#audio), it persists a local upload in the database. It then associates the upload to related library and track information. If no track matches the audio metadata, Funkwhale creates on using the `metadata` attribute in the object.

#### Checks

Funkwhale ensures the activity actor and library owner are the same before handling the activity. If the associated library has no local followers, Funkwhale discards the activity.

#### Example

In this example, **Bob** creates new content in his library and sends a message to its followers.

```{code-block} json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/security/v1",
    {}
  ],
  "to": [
    "https://awesome.music/federation/music/libraries/dc702491-f6ce-441b-9da0-cecbed08bcc6/followers"
  ],
  "type": "Create",
  "actor": "https://awesome.music/federation/actors/Bob",
  "object": {}
}
```

### Update

::::{dropdown} Supported on

- [`Library` objects](#library)
- [`Track` objects](#track)

::::

#### Internal logic

```{note}
See [the `Track` object reference](#track) and [`Library` object reference](#library) for details on the object's structure.
```

When Funkwhale receives an update associated with a [`Library`](#library) or [`Track`](#track) object, it attempts to update the corresponding object in its database.

#### Checks

Funkwhale performs different checks depending on the target of the update:

- For [`Library`](#library) objects, Funkwhale ensures the actor sending the message is the library owner
- For [`Track`](#track) objects, Funkwhale ensures the actor sending the message **either**:
  - Matches the [`attributedTo`](./index.md#attributedto) property on the local copy of the object
  - Is the [service actor](./index.md#service-actor)

#### Example

In this example, **Bob** updates his library and sends a message to its followers.

```{code-block} json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/security/v1",
    {}
  ],
  "to": [
    "https://awesome.music/federation/music/libraries/dc702491-f6ce-441b-9da0-cecbed08bcc6/followers"
  ],
  "type": "Update",
  "actor": "https://awesome.music/federation/actors/Bob",
  "object": {}
}
```

### Delete

::::{dropdown} Supported on

- [`Audio` objects](#audio)
- [`Library` objects](#library)
- [`Listen` activity](#listen)

::::

#### Internal logic

When Funkwhale receives a `Delete` activity, it deletes the associated object from the database.

#### Checks

Funkwhale ensures the actor initiating the activity is the owner of the associated object before handling it.

#### Example

::::{tab-set}

:::{tab-item} Library

In this example, **Bob** deletes a library and notifies its followers.

```{code-block} json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/security/v1",
    {}
  ],
  "type": "Delete",
  "to": [
    "https://awesome.music/federation/music/libraries/dc702491-f6ce-441b-9da0-cecbed08bcc6/followers"
  ],
  "actor": "https://awesome.music/federation/actors/Bob",
  "object": {
    "type": "Library",
    "id": "https://awesome.music/federation/music/libraries/dc702491-f6ce-441b-9da0-cecbed08bcc6"
  }
}
```

:::

:::{tab-item} Audio

In this example, **Bob** deletes three audio objects in a library and notifies the library's followers.

```{code-block} json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/security/v1",
    {}
  ],
  "type": "Delete",
  "to": [
    "https://awesome.music/federation/music/libraries/dc702491-f6ce-441b-9da0-cecbed08bcc6/followers"
  ],
  "actor": "https://awesome.music/federation/actors/Bob",
  "object": {
    "type": "Audio",
    "id": [
      "https://awesome.music/federation/music/uploads/19420073-3572-48a9-8c6c-b385ee1b7905",
      "https://awesome.music/federation/music/uploads/11d99680-23c6-4f72-997a-073b980ab204",
      "https://awesome.music/federation/music/uploads/1efadc1c-a704-4b8a-a71a-b288b1d1f423"
    ]
  }
}
```

:::

::::

### Like

We send the [Like](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-like) object with its type : this allow proper routing and avoid useless database and network queries.

::::{dropdown} Supported on

- [`Track` objects](#track)

::::

#### Example

```{code-block} json
{
    "type": "Like",
    "id": "https://burn.patriachy//7b54d361-c513-4756-a085-13f97573237b",
    ""object": {
        "Type": "Track",
        "id": "https://Le_Rn.areRacists//aebd2be4-49a1-4ef5-aadf-27bff1001d4d",
    },
    "@context": [
        "https://www.w3.org/ns/activitystreams",
        "https://w3id.org/security/v1",
        "https://funkwhale.audio/ns",
        {
            "manuallyApprovesFollowers": "as:manuallyApprovesFollowers",
            "Hashtag": "as:Hashtag",
        },
    ],
}
```

### Dislike

We send the [Dislike](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-dislike) object with its type : this allow proper routing and avoid useless database and network queries.

::::{dropdown} Supported on

- [`Track` objects](#track)

::::

#### Example

```{code-block} json
{
    "type": "Dislike",
    "id": "https://burn.patriachy//7b54d361-c513-4756-a085-13f97573237b",
    ""object": {
        "Type": "Track",
        "id": "https://Le_Rn.areRacists//aebd2be4-49a1-4ef5-aadf-27bff1001d4d",
    },
    "@context": [
        "https://www.w3.org/ns/activitystreams",
        "https://w3id.org/security/v1",
        "https://funkwhale.audio/ns",
        {
            "manuallyApprovesFollowers": "as:manuallyApprovesFollowers",
            "Hashtag": "as:Hashtag",
        },
    ],
}
```

### Listen

We send the [Listen](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-listen) object with its type : this allow proper routing and avoid useless database and network queries.

::::{dropdown} Supported on

- [`Track` objects](#track)

::::

#### Example

```{code-block} json
{
    "type": "Listen",
    "id": "https://makerichpeoplepay.forclimatechange//5355f8b7-bbcc-4285-9c13-d21748084cc1",
    "object": {
        "Type": "Track",
        "id": "https://Le_Rn.areRacists//aebd2be4-49a1-4ef5-aadf-27bff1001d4d",
    },
    "@context": [
        "https://www.w3.org/ns/activitystreams",
        "https://w3id.org/security/v1",
        "https://funkwhale.audio/ns",
        {
            "manuallyApprovesFollowers": "as:manuallyApprovesFollowers",
            "Hashtag": "as:Hashtag",
        },
    ],
}
```

## Supported objects

### Artist

An `Artist` is a custom object used to store musical artist and podcast creator information.

#### Properties

```{list-table}
:header-rows: 1

  * - Property
    - Data type
    - Description
  * - `type`*
    - String
    - The object type (`Artist`)
  * - `id`*
    - String (URI)
    - A URI that identifies the artist over federation
  * - `name`*
    - String
    - The artist's name
  * - `published`*
    - Datetime
    - The date on which the artist was published over the federation
  * - `musicbrainzId`
    - String (UUID)
    - The Musicbrainz artist ID
```

#### Example

```{code-block} json
{
  "type": "Artist",
  "id": "https://awesome.music/federation/music/artists/73c32807-a199-4682-8068-e967f734a320",
  "name": "Krav Boca",
  "published": "2018-04-08T12:19:05.920415+00:00",
  "musicbrainzId": "65f4f0c5-ef9e-490c-aee3-909e7ae6b2ab"
}
```

### ArtistCredit

An `ArtistCredit` is a custom object used to store information about how artists are credited in music objects. We followed [Musicbrainz data structure](https://musicbrainz.org/doc/Artist_Credits).

#### Properties

```{list-table}
:header-rows: 1

  * - Property
    - Data type
    - Description
  * - `type`*
    - String
    - The object type (`ArtistCredit`)
  * - `id`*
    - String (URI)
    - A URI that identifies the artist over federation
  * - `artist`*
    - [`Artist` object](#artist)
    - The credited Artist
  * - `credit`*
    - String
    - How the artist is credited in the object. Can differ from artist.name
  * - `joinphrase`
    - String
    - Concatenated after artist credit. Join the present ArtistCredit with the next one.
  * - `published`*
    - Datetime
    - The date on which the artist was published over the federation
```

#### Example

```{code-block} json
{
    "type": "ArtistCredit",
    "id": "https://test.federation/federation/music/artistcredit/6dc0071c-0186-4f27-a234-fa5858774400",
    "artist": {
        "type": "Artist",
        "id": "https://white.info//6dc0071c-0186-4f27-a234-fa5858774400",
        "name": "Krav Boca",
        "published": "2024-12-22T21:54:46.391743+00:00",
        "musicbrainzId": "6dc0071c-0186-4f27-a234-fa5858774400",
        "attributedTo": None,
        "tag": [],
        "image": None,
    },
    "joinphrase": "feat. ",
    "credit": "Crav Boka",
    "index": None,
    "published": "2024-12-22T21:54:46.392309+00:00",
}

```

### Album

An `Album` is a custom object used to store album and podcast series information.

#### Properties

```{list-table}
:header-rows: 1

  * - Property
    - Data type
    - Description
  * - `type`*
    - String
    - The object type (`Album`)
  * - `id`*
    - String (URI)
    - A URI that identifies the album over federation
  * - `name`*
    - String
    - The album's title
  * - `artist_credit`
    - Array of strings
    - A list of [`ArtistCredit` objects](#artistcredit) associated with the albums
  * - `published`*
    - Datetime
    - The date on which the artist was published over the federation
  * - `released`
    - Datetime
    - The date on which the album was released
  * - `musicbrainzId`
    - String (UUID)
    - The Musicbrainz release ID
  * - `cover`
    - [`Link` object](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-link)
    - A `Link` object representing the album cover
```

#### Example

```{code-block} json
{
  "type": "Album",
  "id": "https://awesome.music/federation/music/albums/69d488b5-fdf6-4803-b47c-9bb7098ea57e",
  "name": "Ride the Lightning",
  "released": "1984-01-01",
  "published": "2018-10-02T19:49:17.412546+00:00",
  "musicbrainzId": "589ff96d-0be8-3f82-bdd2-299592e51b40",
  "cover": {
    "href": "https://awesome.music/media/albums/covers/2018/10/02/b69d398b5-fdf6-4803-b47c-9bb7098ea57e.jpg",
    "type": "Link",
    "mediaType": "image/jpeg"
  },
  "artist_credit": [
    {}
  ]
}
```

### Track

A `Track` is a custom object used to store track information.

#### Properties

```{list-table}
:header-rows: 1

  * - Property
    - Data type
    - Description
  * - `type`*
    - String
    - The object type (`Track`)
  * - `id`*
    - String (URI)
    - A URI that identifies the track over federation
  * - `name`*
    - String
    - The track title
  * - `position`*
    - Integer
    - The position of the track in the album
  * - `published`*
    - Datetime
    - The date on which the track was published over the federation
  * - `musicbrainzId`
    - String (UUID)
    - The Musicbrainz recording ID
  * - `album`
    - [`Album` object](#album)
    - The album that contains the track
  * - `artist_credit`
    - Array of strings
    - A list of [`ArtistCredit` objects](#artistcredit) associated with the track. This can differ from the album artists
```

#### Example

```{code-block} json
{
  "type": "Track",
  "id": "https://awesome.music/federation/music/tracks/82ece296-6397-4e26-be90-bac5f9990240",
  "name": "Shock! Extinction de masse",
  "position": 3,
  "published": "2018-10-02T19:49:35.822537+00:00",
  "musicbrainzId": "771ab043-8821-44f9-b8e0-2733c3126c6d",
  "artist_credit": [
    {}
  ],
  "album": {}
}
```

### Library

```{note}
Crawling library pages requires authentication and an approved follow unless the library is public.
```

A `Library` is a custom object used to store music collection information. It inherits its behavior and properties from ActivityPub's [`Actor`](https://www.w3.org/TR/activitypub/#actors) and [`Collection`](https://www.w3.org/TR/activitypub/#collections) objects.

#### Properties

```{list-table}
:header-rows: 1

  * - Property
    - Data type
    - Description
  * - `type`*
    - String
    - The object type (`Library`)
  * - `id`*
    - String (URI)
    - A URI that identifies the library over federation
  * - `name`*
    - String
    - The library's name
  * - `followers`*
    - String (URI)
    - The ID of the library's followers collection
  * - `totalItems`*
    - Integer
    - The number of [`Audio` objects](#audio) in the library
  * - `first`*
    - String (URI)
    - The URL of the library's first page
  * - `last`*
    - String (URI)
    - The URL of the library's last page
  * - `summary`
    - String
    - The library's description
```

#### Example

```{code-block} json
{
  "type": "Library",
  "id": "https://awesome.music/federation/music/libraries/dc702491-f6ce-441b-9da0-cecbed08bcc6",
  "attributedTo": "https://awesome.music/federation/actors/Alice",
  "name": "My awesome library",
  "followers": "https://awesome.music/federation/music/libraries/dc702491-f6ce-441b-9da0-cecbed08bcc6/followers",
  "summary": "This library is for restricted use only",
  "totalItems": 4234,
  "first": "https://awesome.music/federation/music/libraries/dc702491-f6ce-441b-9da0-cecbed08bcc6?page=1",
  "last": "https://awesome.music/federation/music/libraries/dc702491-f6ce-441b-9da0-cecbed08bcc6?page=56",
}
```

### Audio

```{note}
Accessing audio files requires authentication and an approved follow for the containing library unless the library is public.
```

An `Audio` object is a custom object used to store upload information. It extends the [ActivityStreams Audio object](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-audio) with custom attributes.

#### Properties

```{list-table}
:header-rows: 1

  * - Property
    - Data type
    - Description
  * - `type`*
    - String
    - The object type (`Audio`)
  * - `id`*
    - String (URI)
    - A URI that identifies the audio over federation
  * - `name`*
    - String
    - A readable title for the order. Funkwhale concatenates the track name, album title, and artist name
  * - `size`*
    - Integer
    - The size of the audio in bytes
  * - `bitrate`*
    - Integer
    - The bitrate of the audio in bytes/s
  * - `duration`*
    - The duration of the audio as defined in [as](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-duration)
  * - `library`*
    - String (URI)
    - The ID of the audio's containing [`Library` object](#library)
  * - `published`*
    - Datetime
    - The date on which the audio was published over the federation
  * - `updated`*
    - Datetime
    - The date on which the audio was last updated over the federation
  * - `url`*
    - [`Link` object](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-link)
    - A `Link` object object containing the download location of the audio file
  * - `track`
    - [`Track` object](#track)
    - The track associated with the audio file
```

#### Example

```{code-block} json
{
  "type": "Audio",
  "id": "https://awesome.music/federation/music/uploads/88f0bc20-d7fd-461d-a641-dd9ac485e096",
  "name": "Krav Boca - Mortem",
  "size": 8656581,
  "bitrate": 320000,
  "duration": "PT1312S,
  "library": "https://awesome.music/federation/music/libraries/dc702491-f6ce-441b-9da0-cecbed08bcc6",
  "updated": "2018-10-02T19:49:35.646372+00:00",
  "published": "2018-10-02T19:49:35.646359+00:00",
  "track": {},
  "url": {
    "href": "https://awesome.music/api/v1/listen/82ece296-6397-4e26-be90-bac5f9990240/?upload=88f0bc20-d7fd-461d-a641-dd9ac485e096",
    "type": "Link",
    "mediaType": "audio/mpeg"
  }
}
```

## Custom properties

### attributedTo

Funkwhale uses the `attributedTo` property to denote the actor responsible for an object. If an object has an `attributedTo` attributed, the associated actor can perform activities to it, including [`Update`](#update) and [`Delete`](#delete).

Funkwhale also attributes all objects on a domain with the domain's [Service actor](#service-actor)

## Scapping Collections

Playlists objects are a custom ordered collection[Ordered Collection](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-orderedcollection) containing `PlaylistTracks` objects.
The `id` of the playlist is the endpoint where playlist information can be gathered. If no page is specified it will only give the playlist metadata :

```{code-block} json
{
    "id": "https://node1.funkwhale.test/federation/music/playlists/c1c36f15-f49e-4da6-abd4-17b9b438c348",
    "attributedTo": "https://node1.funkwhale.test/federation/actors/node1",
    "totalItems": 0,
    "type": "Playlist",
    "current": "https://node1.funkwhale.test/federation/music/playlists/c1c36f15-f49e-4da6-abd4-17b9b438c348?page=1",
    "first": "https://node1.funkwhale.test/federation/music/playlists/c1c36f15-f49e-4da6-abd4-17b9b438c348?page=1",
    "last": "https://node1.funkwhale.test/federation/music/playlists/c1c36f15-f49e-4da6-abd4-17b9b438c348?page=1",
    "name": "zef",
    "@context": [
        "https://www.w3.org/ns/activitystreams",
        "https://w3id.org/security/v1",
        "https://funkwhale.audio/ns",
        {
            "manuallyApprovesFollowers": "as:manuallyApprovesFollowers",
            "Hashtag": "as:Hashtag",
        },
    ],
}

```

Note that a limited amount of information is send. Full [Playlist](###Playlist) objects are sent through Activities.

The [PlaylisTracks](###PlaylistTrack) will be sent in a [CollectionPage](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-collectionpage) if a page is specified in the playlist url :

```{code-block} json
{
    "id": "https://test.federation/federation/music/playlists/1efba9b2-8218-4ac2-bdce-f9dd8bbd510c?page=1",
    "partOf": "https://test.federation/federation/music/playlists/1efba9b2-8218-4ac2-bdce-f9dd8bbd510c",
    "totalItems": 5,
    "type": "CollectionPage",
    "first": "https://test.federation/federation/music/playlists/1efba9b2-8218-4ac2-bdce-f9dd8bbd510c?page=1",
    "last": "https://test.federation/federation/music/playlists/1efba9b2-8218-4ac2-bdce-f9dd8bbd510c?page=1",
    "items": [
        {
            "type": "PlaylistTrack",
            "id": "https://test.federation/federation/music/playlists/2861fc4a-f3b6-4740-8586-c4573140b994",
            "track": "https://simon.biz//34d56bbd-5096-4ac7-ada9-2d11ea731317",
            "index": 0,
            "attributedTo": "https://wallace-salazar.com/users/ryanrachel953",
            "published": "2024-12-04T11:50:16.625013+00:00",
            "playlist": "https://test.federation/federation/music/playlists/1efba9b2-8218-4ac2-bdce-f9dd8bbd510c",
        },
        {
            "type": "PlaylistTrack",
            "id": "https://test.federation/federation/music/playlists/96a46881-9544-438a-9e34-b7a1b5ecbc7a",
            "track": "https://fuller.info//a8977c57-5704-469a-a2ae-fa7b213bb370",
            "index": 1,
            "attributedTo": "https://wallace-salazar.com/users/ryanrachel953",
            "published": "2024-12-04T11:50:16.631200+00:00",
            "playlist": "https://test.federation/federation/music/playlists/1efba9b2-8218-4ac2-bdce-f9dd8bbd510c",
        },
    ],
    "attributedTo": "https://wallace-salazar.com/users/ryanrachel953",
    "@context": [
        "https://www.w3.org/ns/activitystreams",
        "https://w3id.org/security/v1",
        "https://funkwhale.audio/ns",
        {
            "manuallyApprovesFollowers": "as:manuallyApprovesFollowers",
            "Hashtag": "as:Hashtag",
        },
    ],
}

```
