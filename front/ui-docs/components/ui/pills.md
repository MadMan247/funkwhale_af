<script setup lang="ts">
import { ref } from 'vue'
import { unionBy, union } from 'lodash-es'

import Pills from '~/components/ui/Pills.vue';
import Button from '~/components/ui/Button.vue';
import Spacer from '~/components/ui/Spacer.vue';
import Layout from '~/components/ui/Layout.vue';

type Item = { type: 'custom' | 'preset', label: string }
type Model = {
  currents: Item[],
  others?: Item[],
}

const nullModel = ref({
  currents: []
} satisfies Model)

const staticModel = ref<Model>({
  currents: [
    { label: "#noise", type: 'preset' },
    { label: "#fieldRecording", type: 'preset' },
    { label: "#experiment", type: 'preset' }
  ]
});

const simpleCustomModel = ref<Model>({
  currents: [],
  others: []
})

const customModel = ref<Model>({
  ...staticModel.value,
  others: [
    { label: "#myTag1", type: 'custom' },
    { label: "#myTag2", type: 'custom' }
  ]
});

const sharedOthers = ref<Model['others']>(customModel.value.others)
const currentA = ref<Model['currents']>([{ label: 'A', type: 'preset' }])
const currentB = ref<Model['currents']>([])

const updateSharedOthers = (others: Item[]) => {
  sharedOthers.value
      = unionBy(sharedOthers.value, others, 'label')
      .filter(item => [...currentA.value, ...currentB.value].every(({ label }) => item.label !== label ))
}

const tags = ref<string[]>(['1', '2'])
const sharedTags = ref<string[]>(['3'])
const setTags = (v: string[]) => {
  sharedTags.value
    = [...tags.value, ...sharedTags.value].filter(tag => !(v.includes(tag)))
  tags.value
    = v
}
</script>

```ts
import Pills from "~/components/ui/Pills.vue"
```

# Pills

Show a dense list of pills representing tags, categories or options.
Users can select a subset of given options and create new ones.

The model you provide will be mutated by this component:

- `currents`: these items are currently selected
- `others`: these items are currently not selected (but can be selected by the user). This prop is optional. By adding it, you allow users to change the selection.

Each item has a `label` of type `string` as well as a `type` of either:

- `custom`: the user can edit its label or
- `preset`: the user cannot edit its label

```ts
type Item = { type: 'custom' | 'preset', label: string }
type Model = {
  currents: Item[],
  others?: Item[],
}
```

## No pills

```ts
const nullModel = ref({
  currents: []
}) satisfies Model;
```

```vue-html
<Pills v-model="nullModel" />
```

<Pills
  :get="(v) => { return }"
  :set="() => nullModel"
/>

## Static list of pills

```ts
const staticModel = ref({
  currents: [
    { label: "#noise", type: 'preset' },
    { label: "#fieldRecording", type: 'preset' },
    { label: "#experiment", type: 'preset' }
  ]
} satisfies Model);
```

```vue-html
<Pills
  :get="(v) => { return }"
  :set="() => staticModel"
/>
```

<Pills
  :get="(v) => { return }"
  :set="() => staticModel"
/>

## Let users add, remove and edit custom pills

By adding `custom` options, you make the `Pills` instance interactive. Use [reactive](https://vuejs.org/guide/essentials/reactivity-fundamentals.html#reactive-variables-with-ref) methods [such as `computed(...)`](https://vuejs.org/guide/essentials/computed.html) and `watch(...)` to bind the model.

Note that this component will automatically add an empty pill to the end of the model because it made the implementation more straightforward. Use `filter(({ label }) => label !== '') to ignore it when reading the model.

### Minimal example

```ts
const simpleCustomModel = ref({
  currents: [],
  others: []
})
```

```vue-html
<Pills
  :get="(v) => { simpleCustomModel = v }"
  :set="() => staticModel"
/>
```

<Pills
  :get="(v) => { simpleCustomModel = v }"
  :set="() => staticModel"
/>

### Complex example

```ts
const customModel = ref({
  ...staticModel,
  others: [
    { label: "#MyTag1", type: 'custom' },
    { label: "#MyTag2", type: 'custom' }
  ]
} satisfies Model);
```

```vue-html
<Pills
  :get="(v) => { customModel = v }"
  :set="() => customModel"
  label="Custom Tags"
  cancel="Cancel"
/>
```

<Spacer />

<Pills
  :get="(v) => { customModel = v }"
  :set="() => customModel"
  label="Custom Tags"
  cancel="Cancel"
/>

## Bind data with an external sink

In the following example, `others` are shared among two `Pills` lists.

```ts
const sharedOthers = ref<Model['others']>(customModel.value.others)
const currentA = ref<Model['currents']>([{ label: 'A', type: 'preset' }])
const currentB = ref<Model['currents']>([])

const updateSharedOthers = (others: Item[]) => {
  sharedOthers.value
    = unionBy(sharedOthers.value, others, 'label')
    .filter(item =>
      [...currentA.value, ...currentB.value].every(({ label }) =>
        item.label !== label
    ))
}
```

<!-- prettier-ignore-start -->

<Spacer />
<Pills
  :get="({ currents, others }) => {
    currentA = currents;
    updateSharedOthers(others || []);
  }"
  :set="({ currents, others }) => ({ currents: currentA, others: unionBy(sharedOthers, others, 'label') })"
  label="A"
  cancel="Cancel"
/>

<Spacer />
<Pills
  :get="({ currents, others }) => {
    currentB = currents;
    updateSharedOthers(others || []);
  }"
  :set="({ currents, others }) => ({ currents: currentB, others: unionBy(sharedOthers, others, 'label') })"
  label="B"
  cancel="Cancel"
/>

<template
  v-for="_ in [1]"
  :key="[...sharedOthers].join(',')"
>
  <pre> Shared among A and B:
    {{ (sharedOthers || []).map(({ label }) => label).join(', ') }}
  </pre>
</template>

<!-- prettier-ignore-end -->

## Bind data with an external source

You can use the same pattern to influence the model from an outside source:

```ts
const tags = ref<string[]>(['1', '2'])
const sharedTags = ref<string[]>(['3'])
const setTags = (v: string[]) => {
  sharedTags.value
    = [...tags.value, ...sharedTags.value].filter(tag => !(v.includes(tag)))
  tags.value
    = v
}
```

<!-- prettier-ignore-start -->

<Layout
  flex
  gap-8
>
  <Button
    secondary
    @click="setTags([])"
  >
    Set tags=[]
  </Button>
  <Button
    secondary
    @click="setTags(['1', '2', '3'])"
  >
    Set tags=['1', '2', '3']
  </Button>
</Layout>
<hr />
<template
  v-for="_ in [1]"
  :key="[...tags, '*', ...sharedTags].join(',')"
>
  <Layout flex>
    <pre>{{ tags.join(', ') }}</pre>
    <Spacer grow />
    <pre>{{ sharedTags.join(', ') }}</pre>
  </Layout>
  <hr />
  <Spacer />
  <Pills
    :get="({ currents, others }) => {
      setTags(currents.map(({ label }) => label));
      sharedTags
        = union(sharedTags, (others || []).map(({ label }) => label))
    }"
    :set="({ currents, others }) => ({
      currents: tags.map(l => ({ type: 'custom', label: l})),
      others: sharedTags
        .filter(l => currents.every(({ label }) => label !== l))
        .map(l => ({ type: 'custom', label: l}))
    })"
    label="Two-way binding with an array of strings"
    cancel="Cancel"
  />
</template>

<!-- prettier-ignore-end -->
