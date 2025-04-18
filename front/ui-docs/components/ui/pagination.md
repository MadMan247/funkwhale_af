<script setup lang="ts">
import { ref } from 'vue'

import Pagination from "~/components/ui/Pagination.vue"

const page = ref(1)
</script>

```ts
import Pagination from "~/components/ui/Pagination.vue"
```

# Pagination

The pagination component helps users navigate through large lists of results by splitting them up into pages.

| Prop           | Data type | Required? | Description                            |
| -------------- | --------- | --------- | -------------------------------------- |
| `pages`        | Number    | Yes       | The total number of pages to paginate. |
| `v-model:page` | Number    | Yes       | The page number of the current page.   |

## Pagination model

Create a pagination bar by passing the number of pages to the `pages` prop. Use `v-model` to sync the selected page to your page data. Users can click on each button or input a specific page and hit `return`.

```vue-html
<Pagination :pages="8" v-model:page="page" />
```

<Pagination :pages="9" v-model:page="page" />
