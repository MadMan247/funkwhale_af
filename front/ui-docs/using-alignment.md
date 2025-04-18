<script setup>
import Card from "~/components/ui/Card.vue"
import Layout from "~/components/ui/Layout.vue"
import Button from "~/components/ui/Button.vue"
</script>

# Using alignments

You can align items inside `flex` and `grid` layouts.

## Align a component relative to its container with `align-self`

<Layout grid class="preview">

<template
v-for="alignment in ['start', 'center', 'end', 'auto', 'baseline', 'stretch']"
:key="alignment">

  <div style="position:relative;place-self:stretch; grid-area: span 2 / span 2; min-height: 72px; border:.5px solid red; display:grid; grid: 1fr / 1fr; grid-auto-flow: column;"
  >
  <Button auto primary :align-self="alignment">🐌</Button>
_

<span style="position:absolute; right: 0; margin-left:-20px; bottom:0;">align-self={{ alignment }}</span>

  </div>
</template>

<template
v-for="alignment in ['center', 'stretch']"
:key="alignment">

<div style="position:relative;place-self:stretch; grid-area: span 2 / span 2; min-height: 72px; border:.5px solid red; display:grid; grid: 1fr / 1fr; grid-auto-flow: column;"
>
<Button auto primary v-bind="{[alignment]:true}">🐌</Button>
_
<span style="position:absolute; right: 0; bottom:0;">{{ alignment }}</span>
</div>
</template>
</Layout>

## Align the content of a component with `align-text`

<Layout flex class="preview">

```vue-html
  <Button align-text="start">🐌</Button>
  <Button align-text="center">🐌</Button>
  <Button align-text="end">🐌</Button>
  <Button icon="bi-star" align-text="stretch">🐌</Button>
  <Button icon="bi-star" align-text="space-out">🐌</Button>
```

  <Layout class="preview solid primary" stack no-gap>
    <Button align-text="start">🐌</Button>
    <Button align-text="center">🐌</Button>
    <Button align-text="end">🐌</Button>
    <Button icon="bi-star" align-text="stretch">🐌</Button>
    <Button icon="bi-star" align-text="space-out">🐌</Button>
  </Layout>
</Layout>
