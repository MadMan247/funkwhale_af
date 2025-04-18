<script setup>
import { ref } from 'vue'

import Input from "~/components/ui/Input.vue"
import Button from "~/components/ui/Button.vue"
import Layout from "~/components/ui/Layout.vue"
import Spacer from "~/components/ui/Spacer.vue"
import Alert from "~/components/ui/Alert.vue"

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

| Prop          | Data type | Required? | Description                                                                 |
| ------------- | --------- | --------- | --------------------------------------------------------------------------- |
| `placeholder` | String    | No        | The placeholder text that appears when the input is empty.                  |
| `icon`        | String    | No        | The [Bootstrap icon](https://icons.getbootstrap.com/) to show on the input. |
| `v-model`     | String    | Yes       | The text entered in the input.                                              |

Link a user's input to form data by referencing the data in a `v-model` of type `string`.

```ts
const value = ref("Preset Value");
```

```vue-html{2}
<Input v-model="value" placeholder="Your favorite animal" />
```

<Input v-model="value" placeholder="Your favorite animal" />

## Input icons

Add a [Bootstrap icon](https://icons.getbootstrap.com/) to an input to make its purpose more visually clear.

```vue-html{3}
<Input v-model="value" icon="bi-search" />
```

<Input v-model="value" icon="bi-search" />

## Label slot

```vue-html{2-4}
<Input v-model="user">
  <template #label>
    User name
  </template>
</Input>
```

<Input v-model="user">
  <template #label>
    User name
  </template>
</Input>

If you just have a string, we have a convenience prop, so instead you can write:

```vue-html
<Input v-model="user" label="User name" />
```

<Input v-model="user" label="User name" />

## Input-right slot

You can add a template on the right-hand side of the input to guide the user's input.

```vue-html{2-4}
<Input v-model="value" placeholder="Search">
  <template #input-right>
    suffix
  </template>
</Input>
```

<Input v-model="search" placeholder="Search">
  <template #input-right>
    suffix
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

### Password

```vue-html
<Spacer :size="64" />
<Layout form stack>
  <Input v-model="user" label="User name" />
  <Input password v-model="password" label="Password" />
  <Layout flex>
    <Button primary> Submit </Button>
    <Button> Cancel </Button>
  </Layout>
</Layout>
```

<Spacer :size="64" />
<Layout form stack>
  <Input v-model="user" label="User name" />
  <Input password v-model="password" label="Password" />
  <Layout flex>
    <Button primary> Submit </Button>
    <Button> Cancel </Button>
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

If you add attributes that are no props, they will be added to the component:

```vue-html
<Input v-model="password" required
  field-id="password-field"
/>
```

<Input v-model="password" required
  field-id="password-field"
/>
