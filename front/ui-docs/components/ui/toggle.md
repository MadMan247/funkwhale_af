<script setup lang="ts">
import Toggle from '~/components/ui/Toggle.vue'
import Layout from '~/components/ui/Layout.vue'
import Button from '~/components/ui/Button.vue' // needs to be imported so that we can use colors...

import { ref } from 'vue'

const toggle = ref(false)
</script>

```ts
import Toggle from "~/components/ui/Toggle.vue"
```

# Toggle

Toggles are basic form inputs that visually represent a boolean value. Toggles can be **on** (`true`) or **off** (`false`). For actions with more than 2 states or delayed, fallible, or effectful actions, [consider using a Button with `aria-pressed` logic instead](button#on-off).

| Prop            | Data type | Required? | Description                              |
| --------------- | --------- | --------- | ---------------------------------------- |
| `big`           | Boolean   | No        | Controls whether a toggle is big or not. |
| `v-model:value` | Boolean   | Yes       | The value controlled by the toggle.      |

## Normal toggle

Link your toggle to an input using the `v-model` directive.

<Layout flex class="preview">

```vue-html
<Toggle v-model="toggle" />
```

<Toggle v-model="toggle" />

</Layout>

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
