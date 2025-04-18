<script setup lang="ts">
import type { Track, User } from "~/types";

import Activity from "~/components/ui/Activity.vue"

const track: Track = {
  id: 0,
  fid: "",

  title: 'Some lovely track',
  description: {
    content_type: 'text/markdown',
    text: `**New:** Music for the eyes!`
  },
  cover: {
    uuid: "",
    urls: {
      original: 'https://images.unsplash.com/photo-1524650359799-842906ca1c06?ixlib=rb-1.2.1&dl=te-nguyen-Wt7XT1R6sjU-unsplash.jpg&w=640&q=80&fm=jpg&crop=entropy&cs=tinysrgb',
      medium_square_crop: 'https://images.unsplash.com/photo-1524650359799-842906ca1c06?ixlib=rb-1.2.1&dl=te-nguyen-Wt7XT1R6sjU-unsplash.jpg&w=640&q=80&fm=jpg&crop=entropy&cs=tinysrgb',
      large_square_crop: 'https://images.unsplash.com/photo-1524650359799-842906ca1c06?ixlib=rb-1.2.1&dl=te-nguyen-Wt7XT1R6sjU-unsplash.jpg&w=640&q=80&fm=jpg&crop=entropy&cs=tinysrgb'
    }
  },
  tags: ["example"],
  uploads: [],
  downloads_count: 1927549377,
  artist_credit: [{
    artist: {
      id: 0,
      fid: "",

      name: "The Artist",
      description: {
        content_type: 'text/markdown',
        text: `I'm a musician based on the internet.

  Find all my music on [Funkwhale](https://funkwhale.audio)!`},
      tags: [],

      content_category: 'music',
      albums: [],
      tracks_count: 1,
      attributed_to: {
        id: 0,
        summary: "",
        preferred_username: "User12345",
        full_username: "User12345",
        is_local: false,
        domain: "myDomain.io"
      },
      is_local: false,
      is_playable: true
    },
    credit: "",
    joinphrase: " and ",
    index: 22
  }],
  disc_number: 7,

  listen_url: "https://funkwhale.audio",
  creation_date: "12345",
  attributed_to: {
    id: 0,
    summary: "",
    preferred_username: "User12345",
    full_username: "User12345",
    is_local: false,
    domain: "myDomain.io"
  },

  is_playable: true,
  is_local: false
}

const user: User = {
  id: 12,
  avatar: {
    uuid: "",
    urls: {
      original: 'https://images.unsplash.com/photo-1524650359799-842906ca1c06?ixlib=rb-1.2.1&dl=te-nguyen-Wt7XT1R6sjU-unsplash.jpg&w=640&q=80&fm=jpg&crop=entropy&cs=tinysrgb',
      medium_square_crop: 'https://images.unsplash.com/photo-1524650359799-842906ca1c06?ixlib=rb-1.2.1&dl=te-nguyen-Wt7XT1R6sjU-unsplash.jpg&w=640&q=80&fm=jpg&crop=entropy&cs=tinysrgb',
      large_square_crop: 'https://images.unsplash.com/photo-1524650359799-842906ca1c06?ixlib=rb-1.2.1&dl=te-nguyen-Wt7XT1R6sjU-unsplash.jpg&w=640&q=80&fm=jpg&crop=entropy&cs=tinysrgb'
    }
  },
  email: "user12345@example.org",
  summary: { text: "Hi! I'm Example from The Internet.", content_type: "text" },
  username: "user12345",
  full_username: "user12345",
  instance_support_message_display_date: "?",
  funkwhale_support_message_display_date: "?",
  is_superuser: true,
  privacy_level: "everyone"
}
</script>

```ts
import Activity from "~/components/ui/Activity.vue"
```

# Activity

Activities display history entries for a Funkwhale pod. Each item contains the following information:

- An image
- A track title
- An artist name
- A username
- A [popover](./popover.md)

| Prop    | Data type    | Required? | Description                                  |
| ------- | ------------ | --------- | -------------------------------------------- |
| `track` | Track object | Yes       | The track to render in the activity entry.   |
| `user`  | User object  | Yes       | The user associated with the activity entry. |

## Single items

You can render a single activity item by passing the track and user information to the `<Activity>` component.

```vue-html
<Activity :track="track" :user="user" />
```

  <Activity :track="track" :user="user" />

## Activity lists

You can display a list of activity items by passing a `v-for` directive and adding a `key` to the item. The `key` must
be unique to the list.

::: info
Items in a list are visually separated by a 1px border.
:::

```vue-html{4-5}
<Activity :track="track" :user="user" v-for="i in 3" :key="i" />
```

  <Activity :track="track" :user="user" v-for="i in 3" :key="i" />
