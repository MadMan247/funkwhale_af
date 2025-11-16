---
layout: page
---

<script setup lang="ts">
import Header from '@ui/Header.vue'
import Layout from '@ui/Layout.vue'
import Spacer from '@ui/Spacer.vue'
import Button from '@ui/Button.vue'

import HeaderA11y from '@/examples/Header.a11y.vue'
</script>

```ts
import Header from '@ui/Header.vue'
```

# Page header

Place the `Header` at the beginning of a page. Choose an appropriate heading level: `h1` or `h2` or `h3`. Choose `h1` unless the header is part of a page subsection or a modal. You can use all props for [Heading](../heading.md), including the [stylistic variants](../heading.md#visual-sizes-for-page-sections-and-subsections) such as `radio` or `page-heading`.

<<<@/../src/components/ui/Header.vue#props{ts}

For a detailed explanation of the props, read [the entry on `Section`](section.md)

```vue-html
<Header
  page-heading
  h1="My title"
/>
```

<Layout article>
<Header
  page-heading
  h1="My title"
/>
</Layout>

## Add an image

Use the `<template #image>` slot to place a picture to the left of the header.

<HeaderA11y article />

<<<@/examples/Header.a11y.vue#snippet{vue-html}

## Add an action to the right of the heading

-> Use the `action` prop [which is the same as in the `Section` component](/components/ui/layout/section#provide-an-action).

::: tip Tuning the layout

## Responsive design

On narrow screens, the header will first wrap between image and title/content area.

Make sure to keep the minimum width of the title and the content area narrow to prevent unnecessary wrapping.

## Consistent spacing

The distance between the image and the content area is 24px (`gap-24`). The title baseline is at 68px below top.

[-> Reference design (Penpot)](https://design.funkwhale.audio/#/workspace/a4e0101a-252c-80ef-8003-918b4c2c3927/e3a187f0-0f5e-11ed-adb9-fff9e854a67c?page-id=6ca536f0-0f5f-11ed-adb9-fff9e854a67c)

:::

::: tip Using this component

## A11y Checklist

- [ ] Content is organized under headers that describe the following section. [1.3.1](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-3-1)
- [ ] Heading text (prop: `h1`, `h2` etc.) clearly and concisely describes the section content. [1.3.1](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-3-1)
- [ ] Heading levels follow a logical order and, if possible, don't skip a level. [1.3.1](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-3-1)
- [ ] Each page has exactly one main heading (h1). [1.3.1](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-3-1)
- [ ] Make sure content order in the markup makes sense when read linearly (important for screen readers and small screen devices). [1.3.2](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-3-2)
- [ ] If your layout reflows or changes based on screen size, ensure content remains readable without horizontal scrolling at 400% zoom. [1.4.10](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-4-10)
- [ ] For headers containing forms or interactive elements, make sure the tab order matches the visual layout. [2.4.3](https://accessibility.education.gov.uk/guidelines/wcag/explorer#2-4-3)

## Accessible header

<HeaderA11y class="solid" />

<<<@/examples/Header.a11y.vue#snippet{vue-html}

[Test this component in isolation against WCAG2 criteria](/maintaining-accessibility#header)

:::
