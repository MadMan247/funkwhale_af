<script setup lang="ts">
import { ref } from 'vue'

import Input from '~/components/ui/Input.vue'
import Tabs from '~/components/ui/Tabs.vue'
import Tab from '~/components/ui/Tab.vue'

const search = ref('')
</script>

```ts
import Tabs from "~/components/ui/Tabs.vue"
```

# Tabs

Tabs are used to hide information until a user chooses to see it. You can use tabs to show two sets of information on the same page without the user needing to navigate away.

| Prop    | Data type | Required? | Description          |
| ------- | --------- | --------- | -------------------- |
| `title` | String    | Yes       | The title of the tab |

## Tabbed elements

::: warning
The `<Tab>` component must be nested inside a `<Tabs>` component.
:::

```vue-html
<Tabs>
  <Tab title="Overview">Overview content</Tab>
  <Tab title="Activity">Activity content</Tab>
</Tabs>
```

<Tabs>
  <Tab title="Overview">Overview content</Tab>
  <Tab title="Activity">Activity content</Tab>
</Tabs>

::: info
If you add the same tab multiple times, the tab is rendered once with the combined content from the duplicates.
:::

```vue-html{2,4}
<Tabs>
  <Tab title="Overview">Overview content</Tab>
  <Tab title="Activity">Activity content</Tab>
  <Tab title="Overview">More overview content</Tab>
</Tabs>
```

<Tabs>
  <Tab title="Overview">Overview content</Tab>
  <Tab title="Activity">Activity content</Tab>
  <Tab title="Overview">More overview content</Tab>
</Tabs>

## Tabs-right slot

You can add a template to the right side of the tabs using the `#tabs-right` directive.

```vue-html{5-7}
<Tabs>
  <Tab title="Overview">Overview content</Tab>
  <Tab title="Activity">Activity content</Tab>

  <template #tabs-right>
    <Input icon="bi-search" placeholder="Search" />
  </template>
</Tabs>
```

<Tabs>
  <Tab title="Overview">Overview content</Tab>
  <Tab title="Activity">Activity content</Tab>

<template #tabs-right>
<Input v-model="search" icon="bi-search" placeholder="Search" />
</template>
</Tabs>

## Tabs and routes

If the tab content covers most of the page, users will expect that they can navigate to the previous tab with the "back" button of the browser ([See Navigation](./navigation.md)).

In this case, add the `:to` prop to each tab, and place a `RouterView` with the intended props of the route's component into its default slot.

Note that this only compares the name. Make sure to add a `name` field to identify paths in your router config!
