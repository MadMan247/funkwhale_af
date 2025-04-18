<script setup lang="ts">
import { ref, watchEffect } from 'vue'

import Alert from '~/components/ui/Alert.vue'
import Button from '~/components/ui/Button.vue'
import Input from '~/components/ui/Input.vue'
import Modal from '~/components/ui/Modal.vue'
import Layout from '~/components/ui/Layout.vue'

const isOpen = ref(false)
const isOpen2 = ref(false)
const isOpen3 = ref(false)

const alertOpen = ref(true)
watchEffect(() => {
  if (isOpen3.value === false) {
    alertOpen.value = true
    }
})

const isOpen4 = ref(false)
const isOpen5 = ref(false)
const isOpen6 = ref(false)
const isOpen7 = ref(false)
const isOpen8 = ref(false)
const isOpen9 = ref(false)
const isOpen10 = ref(false)

const input = ref('Episcosaurus')

</script>

```ts
import Modal from "~/components/ui/Modal.vue"
```

# Modal

| Prop      | Data type         | Required? | Default | Description                        |
| --------- | ----------------- | --------- | ------- | ---------------------------------- |
| `title`   | `string`          | Yes       |         | The modal title                    |
| `v-model` | `true` \| `false` | No        |         | Whether the modal is isOpen or not |

<Layout flex>

```vue-html
<Button @click="isOpen = true">
  Open modal
</Button>

<Modal v-model="isOpen" title="My modal">
  Modal content
</Modal>
```

<div class="preview">
<Button primary @click="isOpen = true">
  Open modal
</Button>
<Modal v-model="isOpen" title="My modal">
  Modal content
</Modal>
</div>

</Layout>

## Add actions

Use the `#actions` slot to add actions to a modal. Actions typically take the form of [buttons](./button).

Make sure to add `autofocus` to the preferred button.

<Layout flex>

```vue-html
<Button @click="isOpen = true">
  Open modal
</Button>

<Modal v-model="isOpen" title="My modal">
  Modal content

  <template #actions>
    <Button secondary @click="isOpen2 = false" icon="bi-arrow-left"/>
    <Button autofocus @click="isOpen = false">
      Ok
    </Button>
  </template>
</Modal>
```

<div class="preview">
  <Button primary @click="isOpen2 = true">
    Open modal
  </Button>
  <Modal v-model="isOpen2" title="My modal">
    Modal content
    <template #actions>
      <Button secondary @click="isOpen2 = false" icon="bi-arrow-left"/>
      <Button primary autofocus @click="isOpen2 = false">
        Ok
      </Button>
    </template>
  </Modal>
</div>

</Layout>

### Add a cancel button

All modals can be closed so it makes sense to add a `cancel` button. Note that `Modal` also implements the `ESC` shortcut by default.

The `cancel` prop accepts a string and will add a cancel button.

Note that the Cancel button has `autofocus`. If you want another button to auto-focus, implement the Cancel button manually inside the `#action` slot.

## Customize the title bar

Use the `icon` prop and/or the `#topleft` slot for indicators such as the user's photo or a search input. You can hide the title by setting it to `""`.

<!-- prettier-ignore-start -->

<Button primary @click="isOpen10 = true">
  Open modal
</Button>
<Modal v-model="isOpen10" title="" icon="bi-info-circle">
  <template #topleft>
    <Input ghost v-model="input" autofocus />
  </template>
  No information pages found for <code>{{ input }}</code>
</Modal>

<!-- prettier-ignore-end -->

## Add a main alert

You can nest [Funkwhale alerts](./alert) to visually highlight content within the modal.

<Layout flex>

```vue-html
<Button @click="isOpen = true">
  Open modal
</Button>

<Modal v-model="isOpen8" title="My modal" cancel="Cancel">
  Modal content

  <template #alert v-if="alertOpen">
    <Alert>
      Alert content

      <template #actions>
        <Button autofocus @click="alertOpen = false">Close alert</Button>
      </template>
    </Alert>
  </template>
</Modal>
```

<div class="preview">
<Button
  primary
  @click="isOpen8 = true"
>
  Open modal
</Button>
<Modal v-model="isOpen8" title="My modal" cancel="Cancel">
  Modal content
  <template #alert v-if="alertOpen">
    <Alert blue>
      Alert content
      <template #actions>
        <Button autofocus @click="alertOpen = false">Close alert</Button>
      </template>
    </Alert>
  </template>
  <template #actions>
    <Button primary @click="isOpen8 = false">
      Ok
    </Button>
  </template>
</Modal>
</div>

</Layout>

## Confirm a dangerous action

Note that confirmation dialogs interrupt the user's workflow. Consider adding a recovery functionality such as "undo" instead.

::: tip Read more about designing user experiences around dangerous actions:

- [How to use visual signals and spacing to differentiate between benign and dangerous options](https://www.nngroup.com/articles/proximity-consequential-options/)

  > If you need to implement dangerous actions, make sure to place them apart from other actions to prevent accidental clicks. Add contextual hints and information so that the user understands the consequences of the action.

- [How to design a confirmation dialog](https://www.nngroup.com/articles/confirmation-dialog/)
  > 1. Let the user confirm potentially destructive actions
  > 2. Do not use confirmation dialogs for routine tasks
  > 3. Be specific about the action and its potential consequences
  > 4. Label the response buttons with their result: "Delete my account" instead of "Yes"
  > 5. Make sure to give the user all information they need to decide

:::

### Destructive Modal

The `destructive` prop is used to visually indicate a potentially dangerous or irreversible action. When set to `true`, the modal will have a distinctive red styling to draw the user's attention and highlight the critical nature of the action.

| Prop          | Data type | Required? | Default | Description                                          |
| ------------- | --------- | --------- | ------- | ---------------------------------------------------- |
| `destructive` | `true`    | No        | `false` | Applies a red styling to emphasize dangerous actions |

### Styling Effects

When the `destructive` prop is set to `true`, the modal will:

- Add a red border
- Style the title in red

To visually distinguish the modal from standard modals

### Best Practices

- Use the `destructive` prop sparingly
- Clearly explain the consequences of the action using `<Alert red>`
- Provide a clear way to cancel the action. If you use the `cancel` prop, the Cancel button will have autofocus, preventing accidental confirmation.
- Use descriptive action button labels

The example in the "Confirm a dangerous action" section demonstrates the recommended usage of the destructive modal.

<Layout flex>

```vue-html
<Button
  @click="isOpen4 = true"
  destructive
>
Delete my account
</Button>
<Modal
  v-model="isOpen4"
  title="Delete Account?"
  destructive
  cancel="Cancel"
>
  <template #alert>
    <Alert red>
      Detailed consequences of the action
    </Alert>
  </template>
  <template #actions>
    <Button
      destructive
      @click="isOpen4 = false"
    >
      Confirm Deletion
    </Button>
  </template>
</Modal>
```

<!-- prettier-ignore-start -->

<Button
  @click="isOpen4 = true"
  destructive
>
Delete my account
</Button>
<Modal
  v-model="isOpen4"
  title="Delete Account?"
  destructive
  cancel="Cancel"
>
  <template #alert>
    <Alert red>
      Detailed consequences of the action
    </Alert>
  </template>
  <template #actions>
    <Button
      destructive
      @click="isOpen4 = false"
    >
      Confirm Deletion
    </Button>
  </template>
</Modal>

<!-- prettier-ignore-end -->

</Layout>

## Nested modals

You can nest modals to allow users to isOpen a modal from inside another modal. This can be useful when creating a multi-step workflow.

<Layout flex>

```vue-html
<Button @click="isOpen = true">
  Open modal
</Button>

<Modal v-model="isOpen" title="My modal">
  <Modal v-model="isOpenNested" title="My modal">
    Nested modal content
  </Modal>

  <Button autofocus @click="isOpenNested = true">
    Open nested modal
  </Button>
</Modal>
```

<div class="preview">
<Button
primary
@click="isOpen6 = true"
>
  Open modal
</Button>
<Modal v-model="isOpen6" title="My modal">
  <Modal v-model="isOpen7" title="My modal">
    Nested modal content
  </Modal>
  <Button autofocus @click="isOpen7 = true">
    Open nested modal
  </Button>
</Modal>
</div>

</Layout>

## Auto-focus the close button

If there are no action slots and no cancel button, the close button is auto-focused.

The `autofocus` prop, when set to `off`, overrides this behavior.

## Responsivity

### Designing for small screens

On slim phones, with the default 32px paddings, the content may only be 260px wide (Galaxy S5). Make sure the content wraps accordingly.
