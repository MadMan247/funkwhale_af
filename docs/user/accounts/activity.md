# Change your activity visibility

Your **activity visibility** determines who can see your activities on Funkwhale. There are four visibility options:

- **Nobody except me** – only you can see your activities.
- **Everyone on this instance** – users who have an account on the same {term}`pod` as you can see your activities.
- **Followers** - users who are following you can see your activities.
- **Everyone, across all instances** – anybody can see your activities.

To change your activity visibility:

1. Log in to your account.
2. Select the cog icon ({fa}`cog`) or your avatar to expand the user menu.
3. Select {guilabel}`Settings`.
4. Find {guilabel}`Activity visibility` in the {guilabel}`Account settings` section.
5. Select your visibility level from the slider.
6. Select {guilabel}`Update settings` to save your changes.

That's it! You've updated your activity visibility. This change takes effect as soon as you update your settings.

:::{note}
The activities from a [Channel](../channels/index.md) are **always** public. This is what channels where designed for. If you want to publish tracks privately as an artist you should upload them to your account and not to your channel.
:::

## Your data

As a user you can produce various activities and their related object, most activities are not saved but are used to ask remote instances to delete or update content (they are not brodcasted to user's inbox or saved into the database for a long time).

## Activities objects

Here is the data that a user can request from your account. This data is saved from a long period of time unless you delete it.

- Followers / user followings
- Listenings
- Favorites
- Uploads
- Owned Channels (always public)
- Subscribed Channels

## All activities

Here is a list of activities you can produce :

- Following accept : when you accept a follow request
- Followers accept : when an account accept your follow request

- Playlist create : when you create a playlist
- Playlist update : when you add tracks or update a playlist
- Playlist delete : when you delete a playlist (not brodcasted to user's inbox or saved)

- Listening create : when you listen to a track
- Listening delete : when you delete a listening (not brodcasted to user's inbox or saved)

- Track Favorite create : when you like a track
- Track Favorite delete : when you delete a liked track (not brodcasted to user's inbox or saved)

- Upload create : when you upload a track to a channel or to your account.
- Upload delete : when you delete a track (not brodcasted to user's inbox or saved)

- Update music object (artist, album or track) : when you edit a music object metadata (not brodcasted to user's inbox or saved)

- Actor update : when you update your public information (not brodcasted to user's inbox or saved)
- Actor delete : when you [delete your account](./delete.md) (we send it to remote instance so they delete your data and we add a `Tombstone` to avoid impersonnation).

## Understand where your data goes

Funkwhale is a federated software. It means data is share across the network and some of you personal data might be sended to remote instances/servers. When your visibility settings is set to `everyone` or to `followers` data will be send to remote pods. For the `followers` privacy level, your data will be sent to each one of them. It mean it will be sent to each one of their instances. If you delete a user from your followers or if you change your activities visibility your instance should send a request to the remotes servers to ask them to delete your data. But there is nothing we can to to force them to comply. So when you trust a followers, you're also trusting his instance.
