<script setup lang="ts">
  import Button from '~/components/ui/Button.vue'
  import Link from '~/components/ui/Link.vue'
  import Card from '~/components/ui/Card.vue'
  import Layout from '~/components/ui/Layout.vue'
  import OptionsButton from '~/components/ui/button/Options.vue'
  import Spacer from '~/components/ui/Spacer.vue'

  const alert = ( message: string ) => window.alert(message)
</script>

```ts
import Card from "~/components/ui/Card.vue"
```

# Card

Funkwhale cards are used to contain textual information, links, and interactive buttons. You can use these to create visually pleasing links to content or to present information.

::: details Props

```ts
{
  title: string
  category?: true | "h1" | "h2" | "h3" | "h4" | "h5"

  tags?: string[]
  image?: string | { src: string, style?: "withPadding" }
  icon?: string

  alertProps?: PastelProps
} & Partial<RouterLinkProps>
  & (PastelProps | ColorProps | DefaultProps)
  & RaisedProps
  & VariantProps
  & WidthProps
```

:::

<Layout grid class="preview">

<div style="grid-column: span 5; grid-row: span 2;">

```vue-html
<Card large
  title="For music lovers"
>
  Access your personal music
  collection from anywhere.
  Funkwhale gives you access to
  publication and sharing tools
  you can use to promote that
  your content across the web.
</Card>
```

</div>

<Card medium title="For music lovers">
  Access your personal music collection from anywhere. Funkwhale gives you access to publication and sharing tools that you can use to promote your content across the web.
</Card>

</Layout>

## Card as a Link

Add a `:to` prop, either containing an external link (`"https://..."`) or a Vue Router destination:

<Layout flex class="preview">

```ts
<Card min-content title="Link"
  :to="{name: 'library.albums.detail', params: {id: album.id}}"
/>
```

<Card min-content title="Link"
  :to="{name: 'library.albums.detail', params: {id: 1}}"
/>
</Layout>

If you add interactive elements, only the surrounding surfaces will be linked.
For details, see the section on [interactive elements on top of a linked card](#interactive-elements-on-top-of-a-linked-card)

## Card as a Category header

Category cards are basic cards that contain only a title. To create a category card, pass a `category` prop.

<Layout flex class="preview">

```vue-html{1,5}
<Card category min-content
  title="Good Translations"
/>

<Card category
  title="Bad Translations"
/>
```

<Layout stack>
  <Card category min-content
  title="Good Translations"
  />
  <Card category
  title="Bad Translations"
  />
</Layout>
</Layout>

## Add an Image

Pass an image source to the `image` prop or set both `image.src` and `image.style` by passing an object.

<Layout grid class="preview">

<div style="grid-column: span 5; grid-row: span 2">

```vue-html{3,8-9}
<Card
  title=" smallFor music lovers"
  image="https://images.unsplash.com/photo-1524650359799-842906ca1c06?ixlib=rb-1.2.1&dl=te-nguyen-Wt7XT1R6sjU-unsplash.jpg&w=640&q=80&fm=jpg&crop=entropy&cs=tinysrgb">
/>

<Card small
  title="For music lovers"
  :image="{ src:'https://images.unsplash.com/photo-1524650359799-842906ca1c06?ixlib=rb-1.2.1&dl=te-nguyen-Wt7XT1R6sjU-unsplash.jpg&w=640&q=80&fm=jpg&crop=entropy&cs=tinysrgb',
            style:'withPadding' }"
/>
```

</div>
<Card small
  title="For music lovers"
  image="https://images.unsplash.com/photo-1524650359799-842906ca1c06?ixlib=rb-1.2.1&dl=te-nguyen-Wt7XT1R6sjU-unsplash.jpg&w=640&q=80&fm=jpg&crop=entropy&cs=tinysrgb"
/>

<Card small
    title="For music lovers"
    :image="{ src:'https://images.unsplash.com/photo-1524650359799-842906ca1c06?ixlib=rb-1.2.1&dl=te-nguyen-Wt7XT1R6sjU-unsplash.jpg&w=640&q=80&fm=jpg&crop=entropy&cs=tinysrgb',
              style:'withPadding' }"
  />
</Layout>

## Add an Icon

<Layout grid class="preview">

<div style="grid-column: span 5; grid-row: span 2;">

```vue-html{4,10}
<Card
  title="Uploading..."
  image="https://images.unsplash.com/photo-1524650359799-842906ca1c06?ixlib=rb-1.2.1&dl=te-nguyen-Wt7XT1R6sjU-unsplash.jpg&w=640&q=80&fm=jpg&crop=entropy&cs=tinysrgb"
  icon="bi-cloud-arrow-up-fill"
/>


<Card
  to="./"
  title="Find out more"
  icon="bi-box-arrow-up-right"
>
Visit the Docs and learn more about developing Funkwhale
</Card>
```

</div>

<Card
  title="Uploading..."
  image="https://images.unsplash.com/photo-1524650359799-842906ca1c06?ixlib=rb-1.2.1&dl=te-nguyen-Wt7XT1R6sjU-unsplash.jpg&w=640&q=80&fm=jpg&crop=entropy&cs=tinysrgb"
  icon="bi-cloud-arrow-up-fill"
/>

<Card
  to="./"
  title="Find out more"
  icon="bi-box-arrow-up-right">

Visit the Docs and learn more about developing Funkwhale

</Card>
</Layout>

You can combine this prop with any other prop configuration. If you combine it with an image, keep an eye on the contrast ratio between the icon color and the image.

## Add an Alert

```vue-html{2-4}
<Card title="Your Collection" :alertProps="{ red: true }">
  <template #alert>
    Please annotate all items with the required metadata.
  </template>
</Card>
```

<div class="preview">
<Card title="Your Collection" :alertProps="{ red: true }">
  <template #alert>Please annotate all items with the required metadata.</template>
</Card>
</div>

::: info

To add props to the alert, add the `alert-props` property to the card. Check out [the Alert component docs](/components/ui/alert) to find out which props are supported

:::

## Add a topright action

```vue-html
<Card title="Topright action">
  <template #topright>
    <OptionsButton square-small />
  </template>
</Card>
```

<Card title="Topright action">
  <template #topright>
    <OptionsButton square-small />
  </template>
</Card>

## Add a Footer

Items in this region are secondary and will be displayed smaller than the main content.

```vue-html{3-9}
<Card large title="My items">
  <template #alert> There are no items in this list </template>
  <template #footer>
    <Button outline icon="bi-upload" @click="alert('Uploaded. Press OK!')">
      Upload
    </Button>
    <Spacer style="flex-grow: 1" />
    <OptionsButton />
  </template>
</Card>
```

<div class="preview">
<Card medium title="My items">

<template #alert>There are no items in this list
</template>

<template #footer>
<Button outline icon="bi-upload" @click="alert('Uploaded. Press OK!')">Upload</Button>
<Spacer style="flex-grow: 1" />
<OptionsButton />
</template>

</Card>
</div>

## Add an Action

Large Buttons or links at the bottom edge of the card serve as Call-to-Actions (CTA).

```vue-html{3-6}
<Card large
  title="Join an existing pod"
>
  The easiest way to get started with Funkwhale is to register an account on a public pod.
  <template #action>
    <Button secondary full @click="alert('Open the pod picker')">Action!
    </Button>
  </template>
</Card>
```

<div class="preview">
  <Card medium
    title="Join an existing pod"
  >
    The easiest way to get started with Funkwhale is to register an account on a public pod.
    <template #action>
      <Button secondary full @click="alert('Open the pod picker')">Action!
      </Button>
    </template>
  </Card>
</div>

If there are multiple actions, they will be presented in a row:

```vue-html{4,7}
<Card title="Creating a new playlist...">
  All items have been assimilated. Ready to go!
  <template #action>
    <Button secondary ghost style="justify-content: flex-start;" icon="bi-chevron-left">
      Back
    </Button>
    <Button style="flex-grow:0;" primary @click="alert('Yay')">
      Create
    </Button>
  </template>
</Card>
```

<div class="preview">
  <Card full  title="Creating a new playlist...">
    All items have been assimilated. Ready to go!
    <template #action>
      <Button secondary ghost min-content
        align-text="start"
        icon="bi-chevron-left"
      >
        Items
      </Button>
      <Spacer h grow />
      <Button primary @click="alert('Yay')">
        OK
      </Button>
      <Button destructive  @click="alert('Yay')">
        Cancel
      </Button>
    </template>
  </Card>
</div>

## Add Tags

You can include tags on a card by adding a list of `tags`. These are rendered as [pills](./pill.md).

```vue-html{3}
<Card
  title="For music lovers"
  :tags="['rock', 'folk', 'punk']"
>
  Access your personal music collection from anywhere. Funkwhale gives you access to publication and sharing tools that you can use to promote your content across the web.
</Card>
```

<div class="preview">
  <Card medium
    title="For music lovers"
    :tags="['rock', 'folk', 'punk']"
  >
    Access your personal music collection from anywhere. Funkwhale gives you access to publication and sharing tools that you can use to promote your content across the web.
  </Card>
</div>

## Interactive elements on top of a linked card

Avoid adding buttons and links on top of a [linked card](#card-as-a-link). This is an uncommon pattern and will confuse users.

```vue-html
<Card
  full
  title="Linked card with interactive elements"
  to="./card.md"
  :tags="['rock', 'folk', 'punk']"
  icon="bi-exclamation large"
>
  <Button primary low-height :onClick="()=>alert('Button clicked')">Click me!</Button>
  <Link secondary to="./card.md" align-text="end">Open this file in a new window</Link>
</Card>
```

<!-- prettier-ignore-start -->

<Card
  full
  title="Linked card with interactive elements"
  to="./card.md"
  :tags="['rock', 'folk', 'punk']"
  icon="bi-exclamation large"
>
  <Button primary low-height :onClick="()=>alert('Button clicked')">Click me!</Button>
  <Link secondary to="./card.md" align-text="end">Open this file in a new window</Link>
</Card>

<!-- prettier-ignore-end -->

Instead, use the [action area](#add-an-action) to offer the primary link:

```vue-html
<Card
  full
  title="Card with interactive elements"
  :tags="['rock', 'folk', 'punk']"
  icon="bi-check-lg large"
>
  <Button secondary low-height :onClick="()=>alert('Button clicked')">Click me!</Button>
  <Link secondary to="./card.md" align-text="end">Open this file in a new window</Link>
  <template #action>
    <Link solid full primary to="./card.md" align-text="center">Details</Link>
  </template>
</Card>
```

<!-- prettier-ignore-start -->

<Card
  full
  title="Card with interactive elements"
  :tags="['rock', 'folk', 'punk']"
  icon="bi-check-lg large"
>
  <Button secondary low-height :onClick="()=>alert('Button clicked')">Click me!</Button>
  <Link secondary to="./card.md" align-text="end">Open this file in a new window</Link>
  <template #action>
    <Link solid full primary to="./card.md" align-text="center">Details</Link>
  </template>
</Card>

<!-- prettier-ignore-end -->

## Add color

- Choose a color: `default`, `primary`, `secondary`, `destructive`, or a Pastel (red, yellow, purple, green or blue)
- Choose a variant: `raised`, `solid`, `outline`,...

Read more: [Using Color](/using-color)

## Set size

`large` (304px), `medium` (208px), `auto`, `small`, ...

Read more: [Using Width](/using-width)
