---
layout: page
---

<script setup>
import { ref } from 'vue'

import Input from "@ui/Input.vue"
import Button from "@ui/Button.vue"
import Layout from "@ui/Layout.vue"
import Spacer from "@ui/Spacer.vue"
import Alert from "@ui/Alert.vue"

import FormsA11y from '@/examples/Forms.a11y.vue'

const value = ref("Preset Value")
const search = ref("")
const user = ref("")
const password = ref("")

const reset = () => { console.log("Hello"); value.value = 'Original value' }
</script>

```ts
import Input from "~/components/ui/Input.vue"
```

# Input

Inputs are areas in which users can enter a single-line text or a number. Several [presets](#presets) are available.

```ts
{
  icon?: string;
  placeholder?: string;
  password?: true;
  search?: true;
  numeric?: true;
  label?: string;
  autofocus?: boolean;
  reset?: () => void;
} & (ColorProps | DefaultProps | PastelProps)
  & VariantProps
  & RaisedProps
  & WidthProps
```

Link a user's input to form data by referencing the data in a `v-model` of type `string | number`.

```ts
const value = ref("Preset Value");
```

```vue-html{2}
<Input v-model="value" placeholder="Your favorite animal" />
```

<Input v-model="value" placeholder="Your favorite animal" />

> [!NOTE]
> To convey the intent of the input field, [add either a text label or a custom, screenreader-friendly label template](#add-a-label). [Read more on form field labelling](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-3-1d)
>
> Define [the `autocomplete` and `type` attributes to add semantic clarity and accessibility for machine assistants](https://www.w3.org/WAI/WCAG21/Understanding/identify-input-purpose). A rich taxonomy exists.

> [!NOTE]
> Make sure that when the user starts typing, the page does not radically change. This is about predictability. Warn users if a context change is unavoidable. [3.2.2](https://www.w3.org/WAI/WCAG22/Understanding/on-input.html)

## Input icons

Add a [Bootstrap icon](https://icons.getbootstrap.com/) to an input to make its purpose more visually clear.

```vue-html{3}
<Input v-model="value" icon="bi-search" />
```

<Input v-model="value" icon="bi-search" />

## Add a label

You can either define a text-only label with the `label` prop, or place a custom template into the `#label` slot:

```vue-html{2-4}
<Input v-model="user">
  <template #label>
    User name
  </template>
</Input>
```

<Input v-model="user">
  <template #label>
      <details>
          <summary>How do you want to be called?</summary>
          I will call you by your name.
      </details>
  </template>
</Input>

If you just have a string, we have a convenience prop, so instead you can write:

```vue-html
<Input v-model="user" label="How do you want to be called?" />
```

<Spacer size-12/>

<Input v-model="user" label="How do you want to be called?" />

## Input-right slot

You can add a template on the right-hand side of the input to guide the user's input.

```vue-html{2-4}
<Input v-model="value" placeholder="🐈">
  <template #input-right>
    Paste your cat!
  </template>
</Input>
```

<Input v-model="search" placeholder="🐈">
  <template #input-right>
      Paste your cat!
  </template>
</Input>

## Color

See [Button](./button.md#button-colors) for a detailed overview of available props.

## Presets

### Search

```vue-html
<Input search v-model="search" />
```

<Input search v-model="search" />

### Credentials

```vue-html
<Spacer :size="64" />
<Layout form stack>
  <Input v-model="user" label="User name" autocomplete="username" />
  <Input password v-model="password" label="Password" />
  <Layout flex>
    <Button primary> Submit </Button>
    <Button @click="()=>{user='';password=''}"> Clear </Button>
  </Layout>
</Layout>
```

<Spacer :size="64" />
<Layout form stack>
  <Input v-model="user" label="User name" autocomplete="username" />
  <Input password v-model="password" label="Password" />
  <Layout flex>
    <Button primary> Submit </Button>
    <Button @click="()=>{user='';password=''}"> Clear </Button>
  </Layout>
</Layout>

::: tip

We use the spacer to simulate the baseline alignment on page layouts (64px between sections)

:::

### Add a reset option

```vue-html
<Input
  v-model="value"
  :reset="() => { value = 'Original value' }">
</Input>
```

<Input
  v-model="value"
  :reset="() => { value = 'Original value' }">
</Input>

## Fallthrough attributes

If you add attributes that are no props, they will be added to the resulting `<input>` element:

```vue-html
<Input v-model="password" required
  field-id="password-field"
/>
```

<Input v-model="password" required
  field-id="password-field"
/>

::: tip Using this component

## A11y Checklist

- [ ] If the input has an icon, it has an appropriate text alternative that describes its purpose. [1.1.1](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-1-1)
- [ ] The input label clearly describes its purpose. [1.3.1](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-3-1d)
- [ ] If the input collects user data, add programmatic attributes/props such as `password` or `autocomplete="username"`. [1.3.5](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-3-5)
- [ ] If some input triggers a context change such as navigating away from the page or opening a modal, make it predictable. [3.2.2](https://accessibility.education.gov.uk/guidelines/wcag/explorer#3-2-2)
- [ ] If you add controls into the slots, those can be operated using only the keyboard. [2.1.1](https://accessibility.education.gov.uk/guidelines/wcag/explorer#2-1-1)
- [ ] If the input is required, this is clearly indicated in the label. [3.3.2](https://accessibility.education.gov.uk/guidelines/wcag/explorer#3-3-2)
- [ ] Any validation errors are clearly identified and described to the user. [3.3.1](https://accessibility.education.gov.uk/guidelines/wcag/explorer#3-3-1)
- [ ] Error messages suggest how to fix the problem (e.g., "Password must be at least 8 characters long"). [3.3.3](https://accessibility.education.gov.uk/guidelines/wcag/explorer#3-3-3)

## Accessible input

<<<@/examples/Forms.a11y.vue#input

[See the complete Form example](/forms#accessible-forms)

[Test this component in isolation against WCAG2 criteria](/maintaining-accessibility#input)
:::
