---
layout: page
---

<script setup>
import PlayButton from '@ui/button/Play.vue'
import Layout from '@ui/Layout.vue'
</script>

```ts
import PlayButton from "@ui/button/Play.vue"
```

# Play Button

The play button is a specialized button used in many places across the Funkwhale app. Map a function to the `@play` event handler to toggle it on click.

```vue-html
<PlayButton />
```

<Layout article>
  <PlayButton />
</Layout>

This component extends [the Button component](../button)
