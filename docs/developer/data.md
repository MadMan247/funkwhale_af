# Data structure

## Channel

- has a one to one relationship with `Artist`, `Library`, `Actor` (unique to the channel, used for federation), `Actor` (attributed_to, the actor owning the channel).
- can be an **Artist channel** if the channel.artist.content_category == "music", or a **Podcast channel** if channel.artist.content_category == "podcast", in which case artist.album are podcast series,and tracks are podcast episodes.
- for channels, track.fid is an upload fid and not a track fid (why?)
- channel.fid == actor.fid (== artist fid) if not imported through rss. If imported though rss we create an actor to allow AP follow but we don't return the actor on the ChannelSerializer.

### Fetching / AP

We dont support fid fetch only channel.actor can be fetch. Updates are passed using the Actor AP routes

#### Consederations for future features

> has a user I want the artist metadata I use to be automatically associated with the artist channel.

Possible bug -> if the channel.artist has a mbid that already exist on the db -> db fails. This could append on `create_or_update_channel` while `retrieve_ap_object` on artist
Another problem is if we delete the channel we delete the artist, this could be changed.

In consequence Channel.artist can't have a mbid. We could create channel.mbid to solve this issue -> this doesn't link the tracks to the channel.artist.

### Music Rss feed

To have music rss feed we want to rely eavily on Mbid -> channel.artist should be allowed to have mbid -> where the metadata comes from ? (AP, MB or Rss)
MB -> allows centralization and verification (we rely on mb moderation)
AP -> no way to ensure the is no fraud
RSS -> the source of the feed can lie

- rss-feed -> actor and artist creation for channels. -> can have a mbid -> cannot edit links manually (they comes from rss feed or musicbrainz) -> if another pod import the same rss feed -> new actor. This means the source of truth is not the actor/pod. -> we should be careful to make sure this actors are not followed by remote pod ?

channel creation -> the pod is the source of truth -> conflict with mbid.

audio metadata -> artist with mbid -> musicbrainz is the source of truth
audio metadata -> artist without mbid -> pod is the source of truth
