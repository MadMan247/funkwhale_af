<script setup lang="ts">
import { useModal, fromProps, notUndefined } from '~/ui/composables/useModal.ts'

import Modal from '~/components/ui/Modal.vue'
import Link from '~/components/ui/Link.vue'
import Button from '~/components/ui/Button.vue'
import Layout from '~/components/ui/Layout.vue'
import Card from '~/components/ui/Card.vue'
import Alert from '~/components/ui/Alert.vue'

const { to, isOpen } = useModal('flag')
</script>

```ts
import Link from "~/components/ui/Link.vue"
```

# Link

Users can navigate by following Links. They expect that in contrast to clicking a [button](button), following a link does not manipulate items or trigger any action.

This component will render as [an `<a>` element [MDN]](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/a).

```vue-html

<Link to="/">
  Home
</Link>

```

<Link to="/">
  Home
</Link>

Instead of a route, you can set the prop `to` to any web address starting with `http`.

## `Active` states

- If any ancestor path matches, the `.router-link-active` class is added
- If the whole path matches, the `.router-link-exact-active` class is added

See the [Vue docs](https://router.vuejs.org/guide/essentials/active-links) for a primer on Path matching.

In addition to the standard Vue `RouterLink` path matching function, we use this algorithm:

- If the destination of the link contains any query parameter _and_ none of these is set (i.e. they are all `undefined`), then the class `.router-link-no-matching-query-flags` is added.

This is particularly useful for modals.

<Link ghost :to="useModal('flag').to">
  Open modal
</Link>

<Modal v-model="isOpen" title="Modal">
</Modal>

## Colors and Variants

See [Using color](/using-color)

<Layout grid solid default style="place-items: baseline;">

<Card full title="">

<p>
  A paragraph of text with an inline (uncolored) link: <Link to="/"> no color </Link>
</p>

<Layout flex>
  <Link default to="/">
    default
  </Link>
  <Link primary to="/">
    primary
  </Link>
  <Link secondary to="/">
    secondary
  </Link>
  <Link destructive to="/">
    destructive
  </Link>
</Layout>

</Card>

<Card default solid raised title="Solid" style="grid-row: span 3;">

<Layout stack>
  <Link default solid to="/">
    default solid
  </Link>
  <Link primary solid to="/">
    primary solid
  </Link>
  <Link secondary solid to="/">
    secondary solid
  </Link>
  <Link destructive solid to="/">
    destructive solid
  </Link>
</Layout>

</Card>

<Card default solid raised title="Outline" style="grid-row: span 4;">

_Only use on top of solid surfaces, else the text may be unreadable!_

<Alert v-for="color in ['default', 'primary', 'secondary', 'destructive']" :class="color">
  <Link outline to="/">
    {{ color }} outline
  </Link>
</Alert>

</Card>

<Card default solid raised title="Ghost">
<Layout stack>
  <Link default ghost to="/">
    default ghost
  </Link>
  <Link primary ghost to="/">
    primary ghost
  </Link>
  <Link secondary ghost to="/">
    secondary ghost
  </Link>
  <Link destructive ghost to="/">
    destructive ghost
  </Link>
</Layout>
</Card>

</Layout>

## Shapes

```vue-html
<Link primary solid round to="/">
  Home
</Link>
```

<Link primary solid round to="/">
  Home
</Link>

## Add an icon

You can use [Bootstrap Icons](https://icons.getbootstrap.com/) in your link component.

::: info

- Icon links shrink down to the icon size if you don't pass any content. If you want to keep the link at full width with just an icon, add `button-width` as a prop.

:::

```vue-html
<Link :to  icon="bi-three-dots-vertical" />
<Link :to primary solid round icon="bi-save"/>
<Link :to solid destructive icon="bi-trash">
  Delete
</Link :to>
<Link :to low-height icon="bi-chevron-right">
  Next
</Link>
```

<Layout flex>
<Link :to  icon="bi-three-dots-vertical" />
<Link :to primary solid round icon="bi-save"/>
<Link :to solid destructive icon="bi-trash">
  Delete
</Link :to>
<Link :to low-height icon="bi-chevron-right">
  Next
</Link>
</Layout>

## Set width and alignment

See [Using width](/using-width) and [Using alignment](/using-alignment).

<Layout flex>

```vue-html
  <Link solid primary min-content to="/">min-content</Link>
  <Link solid primary tiny to="/">tiny</Link>
  <Link solid primary buttonWidth to="/">buttonWidth</Link>
  <Link solid primary small to="/">small</Link>
  <Link solid primary medium to="/">medium</Link>
  <Link solid primary full to="/">full</Link>
  <Link solid primary auto to="/">auto</Link>
  <hr />
  <Link solid primary alignSelf="start" to="/">🐌</Link>
  <Link solid primary alignSelf="center" to="/">🐌</Link>
  <Link solid primary alignSelf="end" to="/">🐌</Link>
  <hr />
  <Link solid primary alignText="left" to="/">🐌</Link>
  <Link solid primary alignText="center" to="/">🐌</Link>
  <Link solid primary alignText="right" to="/">🐌</Link>
```

  <Layout class="preview" stack style="--gap:4px;">
    <Link solid primary min-content to="/">min-content</Link>
    <Link solid primary tiny to="/">tiny</Link>
    <Link solid primary buttonWidth to="/">buttonWidth</Link>
    <Link solid primary small to="/">small</Link>
    <Link solid primary medium to="/">medium</Link>
    <Link solid primary full to="/">full</Link>
    <Link solid primary auto to="/">auto</Link>
    <hr />
    <Link solid primary alignSelf="start" to="/">🐌</Link>
    <Link solid primary alignSelf="center" to="/">🐌</Link>
    <Link solid primary alignSelf="end" to="/">🐌</Link>
    <hr />
    <Link solid primary alignText="left" to="/">🐌</Link>
    <Link solid primary alignText="center" to="/">🐌</Link>
    <Link solid primary alignText="right" to="/">🐌</Link>
  </Layout>
</Layout>
