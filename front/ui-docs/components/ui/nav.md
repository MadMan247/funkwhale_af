<script setup lang="ts">
import { ref } from 'vue'

import Nav from '~/components/ui/Nav.vue'

const nav = ref([{ title: 'Go up', to: '../' }, { title: 'Home', to: './', badge: "2" }])
</script>

```ts
import Nav from "~/components/ui/Nav.vue"
```

# Nav

This is just a list of links, styled like tabs.

You can add a `badge` or an `icon` to each tab link.

<Link to="/">Hello</Link>

```ts
import { ref } from 'vue'

const nav = ref([{ title: 'Go up', to: '../' }, { title: 'Home', to: './', badge: "2" }])
```

```vue-html
<Nav v-model="nav" />
```

<Nav v-model="nav" />
