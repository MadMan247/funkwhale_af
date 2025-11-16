---
layout: page
---

<script setup lang="ts">
import { useModal } from '~/ui/composables/useModal.ts'

import Modal from '@ui/Modal.vue'
import Link from '@ui/Link.vue'
import Layout from '@ui/Layout.vue'

import LinkA11y from '@/examples/Link.a11y.vue'

const { to, isOpen } = useModal('flag')
</script>

```ts
import Link from "~/components/ui/Link.vue"
```

# Link

Users can navigate by following Links. They expect that in contrast to clicking a [button](button), following a link does not manipulate items or trigger any action.

This component will render inline as [an `<a>` element [MDN]](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/a): <Link to="/">Home</Link>

```vue-html
<Link to="/">
  Home
</Link>
```

Instead of a route, you can set the prop `to` to any web address starting with `http`.

## `Active` states

- If any ancestor path matches, the `.router-link-active` class is added
- If the whole path matches, the `.router-link-exact-active` class is added

See the [Vue docs](https://router.vuejs.org/guide/essentials/active-links) for a primer on Path matching.

In addition to the standard Vue `RouterLink` path matching function, we use this algorithm:

- If the destination of the link contains any query parameter _and_ none of these is set (i.e. they are all `undefined`), then the class `.router-link-no-matching-query-flags` is added.

This is particularly useful for modals.

<Link ghost :to>
  Open modal
</Link>

<Modal v-model="isOpen" title="Modal">
</Modal>

## Colors and Variants

See [Using color](/using-color)

<!--<Layout grid solid default style="place-items: baseline;" class="funkwhale">

<Card full title="">-->

<p>
  A paragraph of text with an inline (uncolored) link: <Link to="https://funkwhale.audio"> no color </Link>
</p>

<!--<Layout flex>
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

<Alert v-for="class in ['default', 'primary', 'secondary', 'destructive']" :class>
  <Link outline to="/">
    {{ class }} outline
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

</Layout>-->

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
<Link :to icon="bi-three-dots-vertical" />
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
    <Link solid primary alignText="start" to="/">🐌</Link>
    <Link solid primary alignText="center" to="/">🐌</Link>
    <Link solid primary alignText="end" to="/">🐌</Link>
  </Layout>
</Layout>

## Add an icon

::: info

The hidden label of an icon-only link defaults to the icon's name. Use text labels for better accessibility. In a future version, this component will support authoring a hidden label.

Note that buttons without any visible label create barriers for the users, and only use them where the icon itself is a specific and recognisable label (for example for "Play" or "Pause"). Cases such as Ellipsis, Caret or Hamburger icons for progressive disclosure, or Pencil icons for "Edit" links need to be tested in actual use situations.

:::

Use [Bootstrap Icons](https://icons.getbootstrap.com/) such as 'list-check' or 'list-ol' for the `icon` prop.

::: tip How-to

**Full-width icon button**: Icon buttons shrink down to the icon size if you don't pass any content. If you want to keep the button at full width with just an icon, add `button-width` as a prop.

**Right-aligned icon**: When combining icons with other content, prefix the icon prop with `right ` to place it after the content.

**Large icon**: To make icons large, add ` large` to the icon prop.

:::

---

::: tip Using this component

## A11y Checklist

- [ ] Link text clearly indicates its destination or purpose without relying on surrounding context. [1.1.1](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-1-1)
- [ ] If using an icon-only link, provide a meaningful label via `aria-label` that describes the destination. [1.1.1](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-1-1)
- [ ] Links have sufficient contrast (4.5:1) against their background. Choose appropriate color props. [1.4.3](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-4-3)
- [ ] Link purpose can be determined from the link text alone (when the link is not part of a larger element like a Card). [2.4.4](https://accessibility.education.gov.uk/guidelines/wcag/explorer#2-4-4)

## Accessible links

<LinkA11y />

<<<@/examples/Link.a11y.vue#snippet{vue-html}

[Test this component in isolation against WCAG2 criteria](/maintaining-accessibility#link)

:::
