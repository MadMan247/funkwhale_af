<script setup lang="ts">
import { ref } from 'vue'

import { type Track, type User } from '~/types'

import Card from '~/components/ui/Card.vue'
import Layout from '~/components/ui/Layout.vue'
import Toggle from '~/components/ui/Toggle.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Pill from '~/components/ui/Pill.vue'
import Activity from '~/components/ui/Activity.vue'
import Section from '~/components/ui/Section.vue'

const alignLeft = ref(true)

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

const sections = ref<boolean[]>([false, false, false])
</script>

```ts
import Section from '~/components/ui/Section.vue'
```

# Layout section

Sections divide the page vertically. Choose an appropriate heading level for each section.
You can use all props for [Heading](../heading.md), including `h1` to `h6` and [stylistic variants](../heading.md#visual-sizes-for-page-sections-and-subsections) such as `radio` or `page-heading`.

```vue-html
<Section h1="My title" />
```

<Spacer />

<Section h1="My title" />

```vue-html
<Section
  h2="My title"
  radio
/>
```

<Spacer />

<Section
  h2="My title"
  radio
/>

## Align the section

```vue-html
<Section h2="My title" alignLeft />
```

### Make the section header align with the section contents

The section aligns its title and items to a grid, following the designs. To make sure the header of a section exactly aligns with its contents, set the item width (in number of columns). For example,

<style module>
  .table {
    margin: 0 -184px;
    transform: scale(80%);
  }
  .table div[class*='language-'] {
    margin: -8px -16px !important;
  }
</style>

<Layout grid :class="$style.table">
<Card title="Mixed content">

```vue-html
  :columns-per-item="1"
```

</Card>
<Card title="Normal cards">

```vue-html
  :columns-per-item="3"
```

</Card>
<Card title="Large cards, Activities">

```vue-html
  :columns-per-item="4"
```

</Card>
</Layout>

For a complete overview of column widths for common funkwhale components, see [the table in using-width](../using-width.md#widths-in-the-grid)

### Move individual items within and across grid-cells

For child items, you can use all known CSS grid placement techniques:

<Layout grid :class="$style.table">
<Card title="Stretch over all columns">

```css
  grid-column: 1 / -1;
```

Fill the whole grid, no matter how wide the screen is

</Card>
<Card title="Span multiple rows/columns">

```css
  grid-row: span 3
```

</Card>
<Card title="Move within grid cell">

```css
  align-self: start;
  justify-self: center;
```

Place individual items to the edge of their current cell or cells

</Card>
</Layout>

## Provide an action

The link or button will be shown on the right side of the header. Use `action.text` to set the label (required).
You can use all [`Link` props](../link.md) or [`Button` props](../button.md) inside the `action` prop! Note that the button or link label will be in line with the heading.

```vue-html
<Spacer />
<Layout stack gap-64>
  <Section
    h2="With a link"
    :action="{
      text: 'My library',
      to: '/',
      icon: 'bi-star'
    }"
  />
  <Section
    h2="With a button"
    :action="{
        text: 'Say hello!',
        onClick: ()=>console.log('Hello'),
        primary: true,
        solid: true
    }"
  />
</Layout>
```

<Spacer />
<Layout stack gap-64>
  <Section
    h2="With a link"
    :action="{
      text: 'My library',
      to: '/',
      icon: 'bi-star'
    }"
  />
  <Section
    h2="With a button"
    :action="{
        text: 'Say hello!',
        onClick: ()=>console.log('Hello'),
        primary: true,
        solid: true
    }"
  />
</Layout>

## Add icons and slots

```vue-html
<Section
  icon="bi-heart"
>
  <template #topleft>
    <Pill>#Audiology</Pill>
    <Spacer size-12 />
    <Pill>#Phonologics</Pill>
  </template>
</Section>
```

<Spacer />

<Section
  icon="bi-heart"
>
  <template #topleft>
    <Pill>#Audiology</Pill>
    <Spacer size-12 />
    <Pill>#Phonologics</Pill>
  </template>
</Section>

## Set gaps between consecutive sections

Place consecutive sections into a [Layout stack](../layout) with a 64px gap (`gap-64`) to give them a regular vertical rhythm. Use different sizes for very small or very large headings.

Note the spacer above the layout. By default, sections begin at the baseline of the heading. This enables us to explicitly define the vertical rhythm, independently of the heading's line height.

## Mix sections of different item widths

```vue-html
<Layout flex>
<Toggle v-model="alignLeft" label="Left-align the layout"/>
</Layout>

<Spacer />

<Layout stack gap-64>

  <Section
    :alignLeft="alignLeft"
    :columns-per-item="2"
    h2="Cards (2-wide items)"
    :action="{
      text:'Documentation on Cards',
      to:'../card'
    }"
  >
    <Card small default solid raised title="Relatively Long Album Name">
        Artist Name
    </Card>
    <Card small default solid raised title="Relatively Long Album Name">
        Artist Name
    </Card>
    <Card small default solid raised title="Relatively Long Album Name">
        Artist Name
    </Card>
  </Section>

  <Section
    :alignLeft="alignLeft"
    :columns-per-item="3"
    h2="Activities (3-wide items)"
    :action="{
      text:'Delete selected items',
      onClick:()=>console.log('Deleted :-)')
    }"
  >
    <Activity :track="track" :user="user" />
    <Activity :track="track" :user="user" />
    <Activity :track="track" :user="user" />
  </Section>

</Layout>
```

<Layout flex>
<Toggle v-model="alignLeft" label="Left-align the layout"/>
</Layout>

---

<Spacer />

<Layout stack gap-64 class="preview" style="margin: 0 -40px; padding: 0 25px;">

  <Section
    :alignLeft="alignLeft"
    :columns-per-item="3"
    h2="Cards (2-wide items)"
    :action="{
      text:'Documentation on Cards',
      to:'../card'
    }"
  >
    <Card small default solid raised title="Relatively Long Album Name">
        Artist Name
    </Card>
    <Card small default solid raised title="Relatively Long Album Name">
        Artist Name
    </Card>
    <Card small default solid raised title="Relatively Long Album Name">
        Artist Name
    </Card>
  </Section>

  <Section
    :alignLeft="alignLeft"
    :columns-per-item="4"
    h2="Activities (3-wide items)"
    :action="{
      text:'Delete selected items',
      onClick:()=>console.log('Deleted :-)')
    }"
  >
    <Activity :track="track" :user="user" />
    <Activity :track="track" :user="user" />
    <Activity :track="track" :user="user" />
  </Section>

</Layout>

## Collapse and expand the section

By adding either `collapse` or `expand` to the props, you add Accordion behavior to the section.
The heading will become a clickable button.

```ts
const sections = ref([false, false, false])
```

```vue-html
<Section
  v-for="(section, index) in sections"
  :key="`${index}${section}`"
  :h2="`Section ${index} (${section})`"
  align-left
  v-bind="
    section
      ? { collapse: () => { sections[index] = false } }
      : { expand: () => { sections[index] = true } }
  "
>
  Content {{ section }}
</Section>
```

<Section
  v-for="(section, index) in sections"
  :key="`${index}${section}`"
  :h2="`Section ${index}`"
  align-left
  v-bind="
    section
      ? { collapse: () => { sections[index] = false } }
      : { expand: () => { sections[index] = true } }
  "
>
  <Card
    title="Content"
    full
  />
</Section>

## Responsivity

- Cards and Activities snap to the grid columns. They have intrinsic widths, expressed in the number of columns they span. For `Card`, it is `3` and for `Activity`, it is `4`.
- On a typical laptop screen, you may have 4 album cards or 3 activities side-by-side. On a typical mobile screen, you will have one medium card or two small ones in a row.
- The remaining space is evenly distributed.
- Title rows align with the content below them. The action on the right will always end with the last item in the grid. Resize the window to observe how the items move.
