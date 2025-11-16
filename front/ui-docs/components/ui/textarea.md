---
layout: page
---

<script setup lang="ts">
import { ref } from 'vue'

import Textarea from '@ui/Textarea.vue'
import Button from '@ui/Button.vue'
import Spacer from '@ui/Spacer.vue'

import FormsA11y from '@/examples/Forms.a11y.vue'

const text = ref('# Funk\nwhale')
const text1 = ref('# Funk\nwhale')
const text2 = ref('0123456789abcdefghij')
const text3 = ref('')

const reset = () => { text.value = '' }
</script>

```ts
import Textarea from "@ui/Textarea.vue"
```

# Textarea

Textareas are input blocks that enable users to write formatted text (format: Markdown). These blocks are used throughout the Funkwhale interface for entering item descriptions, moderation notes, and custom notifications.

<<<@/../src/components/ui/Textarea.vue#props{ts}

<<<@/../src/components/ui/Textarea.vue#model{ts}

Create a textarea and attach its input to a value using a `v-model` of type `string` (required):

```ts
const text = ref("# Funk\nwhale");
```

```vue-html{2}
<Textarea v-model="text" />
```

<Textarea v-model="text1" />

> [!NOTE]
> To convey the intent of the input field, [add either a text label (`label` prop) or a custom, screenreader-friendly label template](#add-a-label). [Read more on form field labelling](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-3-1d)

## Add a label

```vue-html{3-5}
<Spacer size="16" />
<Textarea>
  <template #label>
    About my music <span style="color:red; float:right;">*required</span>
  </template>
</Textarea>
```

<Spacer size="16" />
<Textarea v-model="text">
  <template #label>
    About my music <span style="color:red; float:right;">*required</span>
  </template>
</Textarea>

If you just have a string, we have a convenience prop, so instead you can write:

```vue-html
<Spacer size="16" />
<Textarea v-model="text" label="About my music" />
```

<Spacer size="16" />
<Textarea v-model="text" label="About my music" />

Note that the label text sits atop of the upper end of the component. This way, you can define the distance between baselines (the vertical rhythm) with spacers or gaps.

## Add a placeholder

```vue-html{3}
<Textarea
  v-model="text"
  placeholder="Describe this track here…"
/>
```

<Textarea v-model="text3" placeholder="Describe this track here…" />

## Limit the number of characters

You can set the maximum length (in characters) that a user can enter in a textarea by passing a `charLimit` prop.

```vue-html{3}
<Textarea v-model="text" :charLimit="20" />
```

<Textarea v-model="text2" :charLimit="20" />

::: warning Caveats

- You can still set the model longer than allowed by changing it via a script or another Textarea
- A line break counts as one character, which may confuse users
- The character counting algorithm has not been tested on non-Latin based languages
- Make sure to inform the user beforehand so they know what error to expect (A11y).

:::

## Set the initial height

Specify the number of lines with the `initial-lines` prop (the default is 5):

```vue-html
<Textarea v-model="text" initial-lines="1" />
```

<Textarea v-model="text3" initialLines="1" />

## Autofocus

If you add the `autofocus` attribute, the text input field will receive focus as soon as it is rendered on the page. Make sure to only add this prop to a single component per page!

## Require this form to be filled before submitting

The `required` attribute prevents the `submit` button of this form.

Make sure to also add an indicator such as the text "required" or a star to prevent confusion.

See [mdn on the `required` attribute](https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/required) if you want to know more.

## Additional attributes

Any prop that is not declared in the `Props` type will be added to the `<textarea>` element directly. See [mdn on `textarea` attributes here](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/textarea). Examples: `autocomplete`, `cols`, `minlength`, `readonly`, `wrap`, `disabled` etc.

## Add custom toolbar items

By default, there are text formatting buttons and a 'preview' toggle button in the toolbar. You can add custom content there by adding them into the default slot. They will be drawn before the `preview` button.

```vue-html
<Textarea v-model="text">
  <Button ghost low-height min-content
    v-if="text !== ''"
    icon="bi-arrow-counterclockwise"
    @click.prevent="reset()">Reset</Button>
</Textarea>
```

<Textarea v-model="text">
  <Spacer no-size grow />
  <Button ghost low-height min-content
    v-if="text !== ''"
    icon="bi-arrow-counterclockwise"
    @click.prevent="reset()">Reset</Button>
</Textarea>

---

::: tip Using this component

## A11y Checklist

- [ ] The `label` prop or the accessible elements in the `#label` slot describe the purpose of the textarea. [1.3.1d](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-3-1d)
- [ ] Users are informed about character limit restrictions before they start typing.
  - 3.3.1 (Identifying errors):
    [Practical guide](https://accessibility.education.gov.uk/guidelines/wcag/explorer#3-3-1) -
    [Deep dive](https://www.w3.org/WAI/WCAG22/Understanding/error-identification.html)
  - 3.3.2 (Giving instructions):
    [Practical guide](https://accessibility.education.gov.uk/guidelines/wcag/explorer#3-3-2) -
    [Deep dive](https://www.w3.org/WAI/WCAG22/Understanding/labels-or-instructions.html)

## Accessible textarea

<<<@/examples/Forms.a11y.vue#textarea

Guide: [Creating accessible forms](/forms#accessible-forms)

[See the complete Form example code](/forms#model)

[Test this component in isolation against WCAG2 criteria](/maintaining-accessibility#textarea)

:::
