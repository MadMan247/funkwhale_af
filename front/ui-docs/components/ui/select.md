<script setup>
import { ref, computed } from 'vue';

import Select from "~/components/ui/Select.vue";
import Button from "~/components/ui/Button.vue";
import Layout from "~/components/ui/Layout.vue";
import Modal from "~/components/ui/Modal.vue";
import Heading from "~/components/ui/Heading.vue";

const current = ref(2);
const options = ref({1: 'One', 2: 'Two', 3: 'Three'});

const nullable = ref(undefined);

const initial = ref(1);

const isOpen = ref(false);
</script>

```ts
import Select from "~/components/ui/Select.vue"
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

## Add a custom label

The select supports a `label` slot for custom label content instead of using the `label` prop.

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
