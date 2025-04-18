<script setup lang="ts">
import Loader from '~/components/ui/Loader.vue'
</script>

<style>
.docs-loader-container div[style^=width] {
  border: 1px solid #666;
  height: 2em;
}
</style>

```ts
import Loader from "~/components/ui/Loader.vue"
```

# Loader

Loaders visually indicate when an operation is loading. This makes it visually clear that the user can't interact with the element until the loading process is complete.

| Prop        | Data type | Required? | Description                                  |
| ----------- | --------- | --------- | -------------------------------------------- |
| `container` | Boolean   | No        | Whether to create a container for the loader |

## Normal loader

```vue-html
<div style="width: 50%">
  <Loader />
</div>
```

<div class="docs-loader-container">
  <div style="width: 50%">
    <Loader />
  </div>
</div>

## No container

By default the `<fw-loader />` component creates a container that takes up 100% of its parent's height. You can disable this by passing a `:container="false"` property. The loader renders centered in the middle of the first parent that has `position: relative` set.

```vue-html
<div style="position: relative">
  <div style="width: 50%">
    <Loader :container="false" />
  </div>
</div>
```

<div class="docs-loader-container">
  <div style="position: relative">
    <div style="width: 50%">
      <Loader :container="false" />
    </div>
  </div>
</div>
