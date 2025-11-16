---
layout: page
---

<script setup>
import { ref, computed } from 'vue';

import Select from "@ui/Select.vue";
import Button from "@ui/Button.vue";
import Layout from "@ui/Layout.vue";
import Modal from "@ui/Modal.vue";
import Heading from "@ui/Heading.vue";

const current = ref(2);
const options = ref({1: 'One', 2: 'Two', 3: 'Three'});

const nullable = ref(undefined);

const initial = ref(1);

const isOpen = ref(false);
</script>

```ts
import Select from "@ui/Select.vue"
```

# Select

Select a value from a list of labeled options.

Uses two v-model bindings: `v-model:current` for the selected value and `v-model:options` for the available options. Each option is a `value: label` field where value is `string | number`.

_Note that this component currently extends the native HTML `<select>` element and inherits its frustrating shortcomings, especially when it comes to styleing. For future paths, see [this excellent article on css-tricks](https://css-tricks.com/striking-a-balance-between-native-and-custom-select-elements/)_.

<!-- prettier-ignore-start -->

<Layout flex>

<Layout stack no-gap>

```ts
const current = ref(2);
const options = ref({
  1: 'One',
  2: 'Two',
  3: 'Three'
});

```

```vue-html
<Select
  label="Select an option"
  v-model:current="current"
  v-model:options="options"
/>
```

</Layout>

<div class="preview">
<Select
  label="Select an option"
  v-model:current="current"
  v-model:options="options"
/>
</div>

</Layout>

> [!NOTE]
> To convey the intent of the selection control, [add either a text label (`label` prop) or a custom, screenreader-friendly label template](#add-a-custom-label). [Read more on form field labelling](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-3-1d)
>
> In addition, [use `type` and `autocomplete` attributes to make use of the existing taxonomy of machine-readable semantic markup](https://www.w3.org/WAI/WCAG21/Understanding/identify-input-purpose). (Vue will add any additional attributes to the `<select>` node at compile-time).

## Add a custom label

The select supports a `label` slot for custom label content if the text-only `label` prop is not flexible enough.

<Layout flex>

```vue-html
<Select
  v-model:current="current"
  v-model:options="options"
>
  <template #label>
    <strong>Custom Label</strong>
  </template>
</Select>
```

<div class="preview">

<Select
  v-model:current="current"
  v-model:options="options"
>
  <template #label>
    <i class="bi bi-star"/> Custom Label
  </template>
</Select>

</div>
</Layout>

## Add a prefix icon

Use the `icon` prop to add a Bootstrap icon before the select input.

<Layout flex>

```vue-html
<Select
  label="Navigation"
  icon="bi-house"
  v-model:current="current"
  v-model:options="options"
/>
```

<div class="preview">
<Select
  label="Navigation"
  icon="bi-house"
  v-model:current="current"
  v-model:options="options"
/>
</div>

</Layout>

## Add placeholder text

Use an informative `placeholder` when no valid option is initially selected.
The placeholder cannot be re-selected but stays visible.

<Layout flex>

<Layout stack no-gap>

```ts
const nullable = ref(undefined)
```

```vue-html
<Select
  label="Choose an option"
  placeholder="Select one..."
  v-model:current="nullable"
  v-model:options="options"
/>
```
</Layout>

<div class="preview">
<Select
  label="Choose an option"
  placeholder="Select one..."
  v-model:current="nullable"
  v-model:options="options"
/>
{{ nullable ?? "No option selected" }}
</div>

</Layout>

## Let the user reset to an initial value

Set the `initial` prop. A `reset` button appears when the current value is different from the initial value.

<Layout flex>
<Layout stack no-gap>

```ts
const initial = ref(1)
```

```vue-html
<Select
  label="Resettable selection"
  v-model:current="current"
  v-model:options="options"
  v-model:initial="initial"
/>
```

</Layout>
<div class="preview">
<Select
  label="Resettable selection"
  v-model:current="current"
  v-model:options="options"
  v-model:initial="initial"
/>
</div>

</Layout>

## Auto-focus the component

Use the `autofocus` prop to focus the select input immediately when the component mounts.
Try it out: Click the `Open modal` button, then use the arrow keys to select an option. Close the modal with `ESC` and re-open it with `SPACE`.

<Layout flex>

```vue-html
<Button primary @click="isOpen = true">
  Open modal
</Button>
<Modal v-model="isOpen" title="My modal">
  Modal content
</Modal>
```

<div class="preview">
<Button primary @click="isOpen = true">
  Open modal
</Button>
<Modal v-model="isOpen">
<Select
  autofocus
  v-model:current="current"
  v-model:options="options"
/>
</Modal>
</div>

</Layout>

## Colors and variants

The Select component supports standard color and variant props from [the color composable](../../using-color) including `primary`, `secondary`, `solid`, `ghost`, `outline`, and other styling props.

<Layout flex>

```vue-html
<Select v-for = "color in [
  'primary',
  'ghost',
  'outline',
  'green',
  'destructive',
  'raised'
  ]"
  v-bind="{[color]: true}"
  v-model:current="current"
  v-model:options="options"
/>
```

<Layout stack gap-8 class="preview">
<Select v-for = "color in ['primary', 'ghost', 'outline', 'green', 'destructive', 'raised']"
  v-bind="{[color]: true}"
  v-model:current="current"
  v-model:options="options"
/>
</Layout>

</Layout>

<!-- prettier-ignore-end -->

::: tip Using this component

## A11y Checklist

- [ ] The label clearly describes the input purpose. [1.3.1](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-3-1d)
- [ ] If you are collecting user information, add appropriate `type` and `autocomplete` attributes. [1.3.5](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-3-5)
- [ ] If the select is required, this is clearly indicated in the label. [3.3.2](https://accessibility.education.gov.uk/guidelines/wcag/explorer#3-3-2)
- [ ] Any validation errors are clearly identified and described to the user. [3.3.1](https://accessibility.education.gov.uk/guidelines/wcag/explorer#3-3-1)
- [ ] Error messages suggest how to fix such problems. [3.3.3](https://accessibility.education.gov.uk/guidelines/wcag/explorer#3-3-3)

## Accessible select

<<<@/examples/Forms.a11y.vue#select

[See the complete Form example](/forms#accessible-forms)

[Test this component in isolation against WCAG2 criteria](/maintaining-accessibility#select)

:::
