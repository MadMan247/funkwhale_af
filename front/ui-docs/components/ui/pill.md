---
layout: page
---

<script setup lang="ts">
import { computed, ref } from 'vue'

import Pill from '@ui/Pill.vue'
import Button from '@ui/Button.vue'
import Spacer from '@ui/Spacer.vue'
import Layout from '@ui/Layout.vue'

import PillA11y from "@/examples/Pill.a11y.vue"

type Item = { type: 'preset' | 'custom', label: string }

const current = ref<Item>({ type: 'custom', label: 'I-am-custom.-Change-me!' })
const others = ref<Item[]>([
    { type: 'preset', label: 'Preset-1' },
    { type: 'preset', label: 'Preset-2' },
    { type: 'preset', label: 'Preset-3' },
  ])

const alert = ( message: string ) => window?.alert(message);
</script>

```ts
import Pill from "@ui/Pill.vue"
```

# Pill

Pills are decorative elements that display information about content they attach to. They can be links to other content or simple colored labels.

You can add text to pills by adding it between the `<Pill>` tags. Alternatively, you can set `v-model` and [make the pill editable](#editable-pill).

```ts
{ noUnderline?: true,
  cancel?: string,
  autofocus?: boolean
} & (PastelProps | ColorProps | DefaultProps)
  & VariantProps
  & RaisedProps
```

-> [Let the user create lists of pills](./pills)

> [!NOTE]
> Make sure to convey the intent of the pill in an accessible way. Do not omit the text content. If you are forced to use only icons/images as the contents of a pill, label them with meaningful `alt` text. [Read more on form field labelling](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-3-1d)

### Primary

Primary pills convey **positive** information.

```vue-html
<Pill primary>
  Primary pill
</Pill>
```

<Pill primary>
  Primary pill
</Pill>

### Secondary

Secondary pills convey **neutral** or simple decorational information such as genre tags.

::: info
This is the default type for pills. If you don't specify a type, a **secondary** pill is rendered.
:::

```vue-html
<Pill>
  Secondary pill
</Pill>
```

<Pill>
  Secondary pill
</Pill>

### Destructive

Destructive pills convey **destructive** or **negative** information. Use these to indicate that information could cause issues such as data loss.

```vue-html
<Pill destructive>
  Destructive pill
</Pill>
```

<Pill destructive>
  Destructive pill
</Pill>

## Pill colors

Funkwhale pills support a range of pastel colors to create visually appealing interfaces.

### Blue

```vue-html
<Pill blue>
  Blue pill
</Pill>
```

<Pill blue>
  Blue pill
</Pill>

### Red

```vue-html
<Pill red>
  Red pill
</Pill>
```

<Pill red>
  Red pill
</Pill>

### Purple

```vue-html
<Pill purple>
  Purple pill
</Pill>
```

<Pill purple>
  Purple pill
</Pill>

### Green

```vue-html
<Pill green>
  Green pill
</Pill>
```

<Pill green>
  Green pill
</Pill>

### Yellow

```vue-html
<Pill yellow>
  Yellow pill
</Pill>
```

<Pill yellow>
  Yellow pill
</Pill>

## Add an image

Image pills contain a small circular image on their left. These can be used for decorative links such as artist links. To created an image pill, insert a link to the image between the pill tags as a `<template>`.

```vue-html{2-4}
<Pill>
  <template #image>
    <div style="background-color: #ff0" />
  </template>
  Awesome artist
</Pill>
```

<Pill>
  <template #image>
    <div style="background-color: #ff0" />
  </template>
  Awesome artist
</Pill>

### Reduce space between image/icon and text

```vue-html{5}
<Pill>
  <template #image>
    <div style="background-color: currentcolor; width: 8px; height: 8px; margin: 8px;" />
  </template>
  <span style="margin-left: -12px;">
    Awesome artist
  </span>
</Pill>
```

<Pill>
  <template #image>
    <div style="background-color: currentcolor; width: 8px; height: 8px; margin: 8px;" />
  </template>
  <span style="margin-left: -12px;">
    Awesome artist
  </span>
</Pill>

## Editable pill

Add `v-model="..."` to link the pill content to a `ref` with one `current` item and zero or more `others`. Set each item's `type` to `preset` or `custom`.

- The `current` item can be changed by the user.
- The `other` items can be selected instead of the `current`.
- Items with type `custom` can be edited and deleted by the user. `preset` items can only be selected or deselected.

```ts
import { ref } from "vue"
const current = ref({ type: 'custom', label: 'I-am-custom.-Change-me!' })
const others = ref([
    { type: 'preset', label: 'Preset-1' },
    { type: 'preset', label: 'Preset-2' },
    { type: 'preset', label: 'Preset-3' },
  ])
```

```vue-html
<Pill
  v-model:current="current"
  v-model:others="others"
/>
```

<Pill
  v-model:current="current"
  v-model:others="others"
/>

## Add a primary action

```vue-html
<Pill @click="alert('Primary')"> Open alert on click </Pill>
```

<Pill @click="alert('Primary')"> Open alert on click </Pill>

If the pill content does not describe what the pill does, add an accessible label:

<Pill
@click="alert('Deleted')"
aria-label="Delete the pill">
<template #image>
<i class="bi bi-trash" />
</template>I want to be deleted
</Pill>

## Add a secondary action

<Pill
@click="alert('Edited')"
aria-label="Edit the pill">
I can be edited
<template #action>
<Button ghost primary round icon="bi-x"
aria-label="Deselect"
@click.stop.prevent="alert('Deselected')"
/>
</template>
</Pill>

```vue-html
<Pill
  v-model:current="current"
  v-model:others="others"
>
  <template #action>
    <Button ghost primary round icon="bi-x"
    aria-label="Deselect"
      title="Deselect"
      @click.stop.prevent="() => {
        if (customTag.current.type === 'custom')
          customTag.others.push({...customTag.current});
        customTag.current = {label: '', type: 'custom'}
      }"
    />
  </template>
</Pill>
```

<!-- prettier-ignore-start -->

<Pill
  v-model:current="current"
  v-model:others="others"
>
  <template #action>
    <Button ghost primary round icon="bi-x"
      title="Deselect"
      @click.stop.prevent="() => {
        if (current.type === 'custom')
          others.push({...current});
        current = {label: '', type: 'custom'}
      }"
    />
  </template>
</Pill>

{{ current }} (+ {{ others.length }} other options)

<!-- prettier-ignore-end -->

### Override the cursor

With the css variable `--cursor`, you can override the default (pointer):

```css
--cursor: text;
```

::: tip Using this component

## A11y Checklist

- [ ] Pill content is meaningful and descriptive. If using only images/icons, provide appropriate text alternatives. [1.1.1](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-1-1)
- [ ] When using colors to convey information (e.g., status or categories), ensure the information is also conveyed through text. [1.4.1](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-4-1)
- [ ] Action buttons (like delete or edit) have clear, descriptive labels. [2.4.6](https://accessibility.education.gov.uk/guidelines/wcag/explorer#2-4-6)

## Accessible pill

<PillA11y />

[Test this component in isolation against WCAG2 criteria](/maintaining-accessibility#pill)

:::
