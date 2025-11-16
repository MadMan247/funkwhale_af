---
layout: page
---

<script setup lang="ts">
import { ref } from 'vue'

import Spacer from "@ui/Spacer.vue"
import Slider from "@ui/Slider.vue"

const options = {
  me: "Only I can find and edit this",
  pod: "Me and other users on the instance can find and edit this",
  everyone: "Everyone can find and edit this"
} as const

const option = ref<keyof typeof options>('pod')

const optionWithUndefined = ref<keyof typeof options | undefined>(undefined)
</script>

```ts
import Slider from "@ui/Slider.vue"
```

# Slider

Let a user select a value along a line.

For each option, provide a description. Markdown is supported.
Select a key from the `options` by setting `v-model`

```ts
const options = {
  me: "Only I can find and edit this",
  pod: "Me and other users on the instance can find and edit this",
  everyone: "Everyone can find and edit this"
} as const;

const option = ref<keyof typeof options>("me");
```

```vue-html
<Slider :options="options" v-model="option" label="Privacy level" />
```

<Spacer />
<Slider :options="options" v-model="option" label="Privacy level" />

> [!NOTE]
> To convey the intent of the input field, [add either a text label (`label` prop) or a custom, screenreader-friendly label template](#add-a-label). [Read more on form field labelling](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-3-1d)

## Add a label

Either specify the `label` prop or add custom Html into the `#label` slot.

## Autofocus

Add the prop `autofocus` to focus the slider as soon as it renders. Make sure to only autofocus one element per page.

## Undefined state

If you want to aggregate potentially mixed states, or start with no initial selection,
you can set v-model to `undefined`.

```ts
const optionWithUndefined = ref<keyof typeof options | undefined>(undefined)
```

```vue-html
<Slider
  v-model="optionWithUndefined"
  label="Privacy level?"
  :options="options"
/>
```

<Spacer />

<Slider
  v-model="optionWithUndefined"
  label="Privacy level?"
  :options="options"
/>

---

**Functionality**

- Define a possible values
- Select zero or one values as active (`v-model`)

**User interaction**

- It mimics the functionality of a single `range` input:
  - to be operated with arrow keys or mouse
  - focus is indicated
  - ticks are indicated

**Design**

- A pin (same as in the toggle component)
- a range (very faint)
- Ticks?
- Constant dimensions, fitting the largest text box

- Not to be confused with a pearls navigation patterns (list of dots; indicates temporal range)

---

::: tip Using this component

## A11y Checklist

- [ ] The `label` prop or accessible elements inside the `#label` slot describe the purpose of the slider. [1.3.1d](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-3-1d)
- [ ] If the value can change without direct input from the user, announce those value changes programmatically when appropriate (use `aria-live` or similar attributes for dynamic updates). [4.1.3](https://accessibility.educity.gov.uk/guidelines/wcag/explorer#4-1-3)

## Accessible slider

<<<@/examples/Forms.a11y.vue#slider

[See the complete Form example](/forms#accessible-forms)

[Test this component in isolation against WCAG2 criteria](/maintaining-accessibility#slider)

:::
