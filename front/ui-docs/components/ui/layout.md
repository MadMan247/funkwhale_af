---
layout: page
---

<script setup>
import { ref } from 'vue'

import Card from '@ui/Card.vue'
import Alert from '@ui/Alert.vue'
import Layout from '@ui/Layout.vue'
import Spacer from '@ui/Spacer.vue'
import Tab from '@ui/Tab.vue'
import Tabs from '@ui/Tabs.vue'
import Toggle from '@ui/Toggle.vue'
import Button from '@ui/Button.vue'

import LayoutA11y from '@/examples/Layout.a11y.vue'

const isGrowing = ref(true)
const noGap = ref(true)
</script>

```ts
import Layout from "@ui/Layout.vue"
```

# Layout

CSS provides [four methods to arrange items in a container](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout/Relationship_of_grid_layout_with_other_layout_methods): Flow, Columns, Flex and Grid. To make typical alignment tasks in the Funkwhale UI easier, we have created a few useful presets.

By default, the items have a 32px gap. You can [change it with the `gap-x` prop](#gap-x-set-the-gap-to-one-of-the-defaults).

## Apply presets

The following containers are responsive. Change your window's size or select a device preset from your browser's dev tools to see how layouts are affected by available space.

<Layout flex gap-8>
  <Card width="163px" title="flex" to="/components/ui/layout/flex" >
    <Layout flex style="outline: 4px dashed var(--border-color)">
      <Button primary icon="bi-eye" />
      <Button outline icon="bi-eye" />
      <Button destructive icon="bi-eye" />
    </Layout>
  </Card>
  <Card width="163px" title="grid" to="/components/ui/layout/grid" >
    <Layout grid column-width="40" style="outline: 4px dashed var(--border-color)">
      <Button primary icon="bi-eye" />
      <Button outline icon="bi-eye" style="grid-row: span 2; height: 100%;"  />
      <Button destructive icon="bi-eye" />
    </Layout>
  </Card>
  <Card width="163px" title="stack" to="/components/ui/layout/stack">
    <Layout stack no-gap style="margin:-8px; outline: 4px dashed var(--border-color)">
      <Button primary icon="bi-eye" />
      <Button outline icon="bi-eye" />
      <Button destructive icon="bi-eye" />
    </Layout></Card>
  <Card width="163px" title="columns" to="/components/ui/layout/columns" >
    <Layout columns column-width="40" style="outline: 4px dashed var(--border-color)">
      <Button primary icon="bi-eye" />
      <Button outline icon="bi-eye" />
      <Button destructive icon="bi-eye" />
    </Layout></Card>
</Layout>

## Add semantics

Add one of these props to your `Layout` component to turn them into semantic containers (without affecting their presentation):

**Headings:** [`"h1" | "h2" | "h3" | "h4" | "h5"`](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/Heading_Elements#usage_notes)

**Sectioning:** [`"nav" | "aside" | "header" | "footer" | "main"`](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/section#usage_notes)

**Forms:** [`"label" | "form"`](https://developer.mozilla.org/en-US/docs/Web/HTML/Element#forms)

## Common props

### `gap-*`: Set the gap to one of the defaults

```ts
`gap-${'4' | '8' | '12' | '16' | '24' | '32' | '48' | '64' | 'auto'}`
```

### `no-gap`: Remove the gap between items

<Layout flex>

```vue
<script setup>
const noGap = ref(true);
</script>

<template>
  <Toggle v-model="noGap" label="no-gap" />

  <Layout flex :no-gap="noGap || undefined">
    <Card title="A" small />
    <Card title="B" small />
    <Card title="C" small />
    <Card title="D" small />
  </Layout>
</template>
```

<div class="preview solid default" style="width: 8rem">
  <Toggle v-model="noGap" label="no-gap" />

---

  <Layout flex :no-gap="noGap || undefined">
    <Card title="A" tiny />
    <Card title="B" tiny />
    <Card title="C" tiny />
    <Card title="D" tiny />
  </Layout>
</div>

</Layout>

### Add fixed or flexible Spacers

::: info Only available on:

- **stack**
- **flex**

:::

If you add a spacer with attribute `grow`, it will push the other item until the Layout fills the available space. This only works if the parent element itself grows beyond its minimal contents.

<Layout flex>

```vue
<script setup>
const isGrowing = ref(true);
</script>

<template>
  <Toggle v-model="isGrowing" label="Grow spacers" />

  <Layout stack style="height:25em;">
    <Alert red />
    <Alert purple />
    <Spacer :grow="isGrowing || undefined" />
    <Alert blue />
  </Layout>
</template>
```

<div class="preview solid default">
<Toggle v-model="isGrowing" label="Grow spacers" />

---

<Layout stack style="height:25em">
  <Alert red />
  <Alert purple />
  <Spacer :grow="isGrowing || undefined" />
  <Alert blue />
</Layout>
</div>

</Layout>

Multiple spacers will distribute their growth evenly.

Note that you can set the minimum space occupied by the `Spacer` with its `size` prop [(docs)](./layout/spacer). Negative values can offset the gap of the `Layout` (but, due to a limitation of flexbox, not eat into the space occupied by adjacent items):

<Layout flex>

```vue
<template>
  <Toggle v-model="isGrowing" label="Grow spacers" />

  <Layout stack style="height:35em;">
    <Alert blue />
    <Spacer :size="-32" :grow="isGrowing || undefined" />
    <Alert green />
    <Alert yellow />
    <Spacer :size="-32" :grow="isGrowing || undefined" />
    <Alert red />
  </Layout>
</template>
```

<div class="preview" style="width:0">
<Toggle v-model="isGrowing" label="Grow spacers" />

---

<Layout stack style="height:35em;">
    <Alert blue />
    <Spacer :size="-32" :grow="isGrowing || undefined" />
    <Alert green />
    <Alert yellow />
    <Spacer :size="-32" :grow="isGrowing || undefined" />
    <Alert red />
  </Layout>
</div>

</Layout>

::: tip Using this component

## A11y Checklist

- [ ] Choose semantic container types (nav, aside, header, etc.) appropriate to the content's purpose. [1.3.1](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-3-1)
- [ ] Make sure content order in the markup makes sense when read linearly (important for screen readers and small screen devices). [1.3.2](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-3-2)
- [ ] If your layout reflows or changes based on screen size, ensure content remains readable without horizontal scrolling at 400% zoom. [1.4.10](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-4-10)
- [ ] Use consistent layout patterns for similar types of content across pages (e.g., same grid structure for article lists). [3.2.3](https://accessibility.education.gov.uk/guidelines/wcag/explorer#3-2-3)
- [ ] For layouts containing forms or interactive elements, make sure the tab order matches the visual layout. [2.4.3](https://accessibility.education.gov.uk/guidelines/wcag/explorer#2-4-3)

## Accessible layout

<LayoutA11y />

<<<@/examples/Layout.a11y.vue#snippet{vue-html}

[Test this component in isolation against WCAG2 criteria](/maintaining-accessibility#layout)

:::
