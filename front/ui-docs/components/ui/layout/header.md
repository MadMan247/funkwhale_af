<script setup lang="ts">
import Header from '~/components/ui/Header.vue'
import Layout from '~/components/ui/Layout.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Button from '~/components/ui/Button.vue'
</script>

```ts
import Header from '~/components/ui/Header.vue'
```

# Page header

Place the `Header` at the beginning of a page. Choose an appropriate heading level: `h1` or `h2` or `h3`. Choose `h1` unless the header is part of a page subsection or a modal. You can use all props for [Heading](../heading.md), including the [stylistic variants](../heading.md#visual-sizes-for-page-sections-and-subsections) such as `radio` or `page-heading`.

```vue-html
<Header
  page-heading
  h1="My title"
/>
```

<Header
  page-heading
  h1="My title"
/>

For a detailed explanation of the props, read [the entry on `Section`](section.md)

### Add an image

Use the `<template #image>` slot to place a picture to the left of the header.

```vue-html
<Header h1="My title">
  <template #image>
    <img
    style="width: 196px;"
    src="https://images.unsplash.com/photo-1524650359799-842906ca1c06?ixlib=rb-1.2.1&dl=te-nguyen-Wt7XT1R6sjU-unsplash.jpg&w=640&q=80&fm=jpg&crop=entropy&cs=tinysrgb" />
  </template>
  <div style="height: 48px;">
    My subtitle
  </div>
  <Layout flex gap-8>
    <Button outline square>A</Button>
    <Button outline square>B</Button>
    <Spacer h grow />
    <Button outline square>C</Button>
  </Layout>
</Header>
```

<Header h1="My title">
  <template #image>
    <img
    style="width: 196px;"
    src="https://images.unsplash.com/photo-1524650359799-842906ca1c06?ixlib=rb-1.2.1&dl=te-nguyen-Wt7XT1R6sjU-unsplash.jpg&w=640&q=80&fm=jpg&crop=entropy&cs=tinysrgb" />
  </template>
  <div style="height: 48px;">
    My subtitle
  </div>
  <Layout flex gap-8>
    <Button outline square>A</Button>
    <Button outline square>B</Button>
    <Spacer h grow />
    <Button outline square>C</Button>
  </Layout>
</Header>

::: tip Responsive layout:

On narrow screens, the header will first wrap between image and title/content area.

Make sure to keep the minimum width of the title and the content area narrow to prevent unnecessary wrapping.

:::

::: tip Spacing:

The distance between the image and the content area is 24px (`gap-24`). The title baseline is at 68px below top.

[-> Reference design (Penpot)](https://design.funkwhale.audio/#/workspace/a4e0101a-252c-80ef-8003-918b4c2c3927/e3a187f0-0f5e-11ed-adb9-fff9e854a67c?page-id=6ca536f0-0f5f-11ed-adb9-fff9e854a67c)

:::

### Add an action to the right of the heading

-> Use the `action` prop [which is the same as in the `Section` component](/components/ui/layout/section#provide-an-action).
