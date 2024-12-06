# Funkwhale federation

```{toctree}
---
maxdepth: 1
---

frontend
copy
api

```

```{note}
We aim to keep this document up-to-date to reflect the current state of federation. If you notice an issue, please open a thread on [our forum](https://forum.funkwhale.audio/t/documentation).
```

Funkwhale is a federated platform. Funkwhale pods can share information between one another, and can also communicate with other {term}`Fediverse` software. This article outlines which tools we use, our approach to federation, and how we implement standards.

```{contents}
:local:
:depth: 2
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

## Custom properties

### attributedTo

Funkwhale uses the `attributedTo` property to denote the actor responsible for an object. If an object has an `attributedTo` attributed, the associated actor can perform activities to it, including [`Update`](#update) and [`Delete`](#delete).

Funkwhale also attributes all objects on a domain with the domain's [Service actor](#service-actor)
