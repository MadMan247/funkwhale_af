---
layout: page
---

<script setup lang="ts">
import Toggle from '@ui/Toggle.vue'
import Layout from '@ui/Layout.vue'
import Button from '@ui/Button.vue' // needs to be imported so that we can use colors...

import { ref } from 'vue'

const toggle = ref(false)
</script>

```ts
import Toggle from "@ui/Toggle.vue"
```

# Toggle

Toggles are basic form inputs that visually represent a boolean value.

```ts
{
  big?: boolean
  label: string
}
```

A toggle can be **on** (`true`) or **off** (`false`). For actions with more than 2 states or delayed, fallible, or effectful actions, [consider using a Button with `aria-pressed` logic instead](button#on-off). Use `v-model` to bind a boolean to the toggle state.

<Layout flex class="preview">

```vue-html
<Toggle label="Enable audio input" v-model="toggle" />
```

<Toggle label="Enable audio input" v-model="toggle" />

</Layout>

> [!NOTE]
> To convey the intent of the toggle, [add a meaningful text label](#add-a-label). [Read more on form field labelling](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-3-1d)

## Add label

<Layout flex class="preview">

```vue-html{2}
<Toggle v-model="toggle" label="Option 358" />
```

<Toggle v-model="toggle" label="Option 358" />

</Layout>

## Big toggle

Pass a `big` prop to create a larger toggle.

<Layout flex class="preview">

```vue-html{2}
<Toggle
   big
   v-model="toggle"
   label="I am big"
/>
```

<Toggle
   big
   v-model="toggle"
   label="I am big"
/>

</Layout>

<Button />

::: tip Using this component

## A11y Checklist

- [ ] Provide a clear label that matches the situation when the toggle is 'on'. [2.5.3](https://accessibility.education.gov.uk/guidelines/wcag/explorer#2-5-3)

## Accessible toggle

<<<@/examples/Forms.a11y.vue#toggle

[Test this component in the context of a form against WCAG2 criteria](/maintaining-accessibility#form-fields)

[See the complete Form example](/forms#accessible-forms)

:::
