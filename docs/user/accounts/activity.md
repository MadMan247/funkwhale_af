# Change your activity visibility

Your **activity visibility** determines who can see your activities on Funkwhale. There are three visibility options:

- **Nobody except me** – only you can see your listening activity.
- **Everyone on this instance** – users who have an account on the same {term}`pod` as you can see your listening activity.
- **Everyone, across all instances** – anybody can see your listening activity.

To change your activity visibility:

::::{tab-set}

:::{tab-item} Desktop
:sync: desktop

1. Log in to your account.
2. Select the cog icon ({fa}`cog`) or your avatar to expand the user menu.
3. Select {guilabel}`Settings`.
4. Find {guilabel}`Activity visibility` in the {guilabel}`Account settings` section.
5. Select your visibility level from the dropdown menu.
6. Select {guilabel}`Update settings` to save your changes.

:::

:::{tab-item} Mobile
:sync: mobile

1. Log in to your account.
2. Select the cog icon ({fa}`cog`) or your avatar to open the {guilabel}`Options` menu.
3. Select {guilabel}`Settings`.
4. Find {guilabel}`Activity visibility` in the {guilabel}`Account settings` section.
5. Select your visibility level from the dropdown menu.
6. Select {guilabel}`Update settings` to save your changes.

:::
::::

That's it! You've updated your activity visibility. This change takes effect as soon as you update your settings.

## Understand where your data goes

Funkwhale is a federated software. It means data is share acfross the networks and some of you personal data might be sended to. When your visibility settings is set to `followers` data will be send to each on of them and to each on of their instance. This means your data will leave your own instance to go to your followers instances. If you delete a user from your follower or if you change your activities visibility your instance should send a request to the remotes servers so they delete your data. But there is nothing we can to to force it to comply. So when you trust a followers, you're also trusting his instance.

## Your activities

Has a user you can produce the following activities:

- Playlist create
- Playlist update
- Playlist delete

- Listening create
- Listening delete

- Track Favorite create
- Track Favorite delete

- Track update
