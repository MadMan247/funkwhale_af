# Data structure

## Channel

- has a one to one relationship with `Artist`, `Library`, `Actor` (unique to the channel, used for federation), `Actor` (attributed_to, the actor owning the channel).
- can be an **Artist channel** if the channel.artist.content_category == "music", or a **Podcast channel** if channel.artist.content_category == "podcast", in which case artist.album are podcast series,and tracks are podcast episodes.
