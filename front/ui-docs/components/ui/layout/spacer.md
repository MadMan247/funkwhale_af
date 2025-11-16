---
layout: page
---

<script setup lang="ts">
import { ref } from 'vue'

import Alert from '@ui/Alert.vue'
import Button from '@ui/Button.vue'
import Layout from '@ui/Layout.vue'
import Spacer from '@ui/Spacer.vue'
import Input from '@ui/Input.vue'
import Card from '@ui/Card.vue'

import SpacerA11y from '@/examples/Spacer.a11y.vue'

const size = ref(32)
</script>

<style>
  .preview {
    padding:16px 0;
    flex-grow:1;
  }
</style>

```ts
import Spacer from '@ui/Spacer.vue'
```

# Spacer

Add a 16px gap between adjacent items.

##### Without spacer

<Layout flex>

```vue-html
<Alert green">A</Alert>
<Alert red">B</Alert>
```

<div class="preview">

<Alert green>A</Alert>
<Alert purple>B</Alert>

</div>

</Layout>

##### With spacer

<Layout flex>

```vue-html{2}
<Alert green">A</Alert>
<Spacer/>
<Alert red">B</Alert>
```

<div class="preview">
<Alert green>A</Alert>
<Spacer/>
<Alert purple>B</Alert>
</div>

</Layout>

##### Spacers can also be added for horizontal space

<Layout flex>

```vue-html{4}
<Layout flex>
  <Alert blue">A</Alert>
  <Alert yellow">B</Alert>
  <Spacer/>
  <Alert red">C</Alert>
</Layout>
```

<div class="preview">
<Layout flex>
<Alert blue>A</Alert>
<Alert yellow>B</Alert>
<Spacer/>
<Alert red>C</Alert>
</Layout>
</div>
</Layout>

## Modify the size of a Spacer

<Layout flex>

```vue
<script setup>
const size = ref(1);
</script>

<template>
  <Input v-model="size" type="range" />

  <Alert yellow>A</Alert>
  <Spacer :size="+size" />
  <Alert purple>B</Alert>
</template>
```

<div class="preview">
  <Input v-model="size" type="range" style="writing-mode: vertical-lr; direction: rtl"/>
  {{ size }}px
</div>
<div class="preview">
  <Alert yellow>A</Alert>
  <Spacer :size="+size" />
  <Alert purple>B</Alert>
</div>
</Layout>

Note the `+` before `size`. Some browsers will output a string for the `Input` value, and the JavaScript `+` prefix parses it into a number. Spacers need numeric `size` values because positive size values affect the dimensions of the element while negative sizes cause negative margins.

## Make the Spacer elastic (responsive)

<Layout flex>

<div style="width: min-content;">

```vue-html
<Layout stack no-gap
  :style="{ height: size + '%' }"
>
  <Button min-content outline>A</Button>
  <Spacer grow title="grow" />
  <Button min-content outline>B</Button>
  <Button min-content outline>C</Button>
  <Spacer shrink title="shrink" />
  <Button min-content outline>D</Button>
  <Spacer grow shrink title="grow shrink" />
  <Button min-content outline>E</Button>
</Layout>
```

</div>

<div class="preview" style="flex-wrap:nowrap">
<Layout flex style="height:30em">

<Input v-model="size" type="range" style="writing-mode: vertical-lr; height:100%"><template #input-right>{{ size }}%</template></Input>

<Layout stack no-gap :style="{ height: size + '%'}">
  <Button min-content outline>A</Button>
  <Spacer grow title="grow" />
  <Button min-content outline>B</Button>
  <Button min-content outline>C</Button>
  <Spacer shrink title="shrink" />
  <Button min-content outline>D</Button>
  <Spacer grow shrink title="grow shrink" />
  <Button min-content outline>E</Button>
</Layout>

</Layout>

</div>
</Layout>

## Restrict the dimension of a spacer with the `v` and `h` props

By default, a spacer is square. You can make it horizontal with `h` and vertical with `v`. See the example in the following section.

## Use the Spacer to vary an element's dimensions

```vue-html
<Input v-model="size" type="range" />
<Card min-content title="h">
  <Spacer h :size="size * 4" style="border:5px dashed;" />
</Card>
<Card min-content title="v">
  <Spacer v :size="size * 4" style="border:5px dashed;" />
</Card>
```

<Layout flex style="align-items:flex-start">
<Input v-model="size" type="range" />
<Card min-content title="h">
  <Spacer h :size="size * 4" style="border:5px dashed;" />
</Card>
<Card min-content title="v">
  <Spacer v :size="size * 4" style="border:5px dashed;" />
</Card>
</Layout>

::: tip Using this component

## A11y Checklist

- [ ] When spacers create visual hierarchy, make sure the markup corresponds.

## Accessible spacer

<SpacerA11y />

<<<@/examples/Spacer.a11y.vue#snippet{vue-html}

[Test this component in isolation against WCAG2 criteria](/maintaining-accessibility#spacer)

:::
