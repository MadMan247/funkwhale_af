<script setup lang="ts">
import Button from '~/components/ui/Button.vue'
import Layout from '~/components/ui/Layout.vue'

const click = ():Promise<void> => new Promise(resolve => setTimeout(resolve, 1000))
</script>

```ts
import Button from "~/components/ui/Button.vue"
```

# Button

Buttons are UI elements that users can interact with to perform actions and manipulate objects. They are distinct from [Links](link) and will not change the user's position.

```ts
{
  thinFont?: true
  lowHeight?: true

  isActive?: boolean
  isLoading?: boolean

  shadow?: boolean
  round?: boolean
  icon?: string

  onClick?: (...args: any[]) => void | Promise<void>

  autofocus?: boolean
  ariaPressed?: true
} & (ColorProps | DefaultProps)
  & VariantProps
  & RaisedProps
  & WidthProps
  & AlignmentProps
```

## Action

[The default action of buttons is `submit` \[mdn\]](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button#type). Specify an [`onClick` or `@click`](#short-form-click) function to change the behavior of a button.

```vue-html
<form>
  <Button>Without `onClick`</Button>
  <Button :onClick="() => {}">With `onClick`</Button>
</form>
```

<form>
  <Button>Without `onClick`</Button>
  <Button :onClick="() => {}">With `onClick`</Button>
</form>

### Short-form @click

For convenience, you can use the Vue-specific `@click` syntax to add the `onClick` prop. The following two buttons are effectively equal:

```vue-html
  <Button :onClick="() => { console.log('Hi!') }"> Long form </Button>
  <Button @click="console.log('Hi!')"> Short form </Button>
```

<Button :onClick="() => { console.log('Hi!') }"> Long form </Button>
<Button @click="console.log('Hi!')"> Short form </Button>

## Button colors

Buttons come in different types depending on the type of action they represent.

Find [a complete overview of recommended styles on the color page](../../using-color#links-and-buttons).

### Default

Default buttons represent **neutral** actions such as cancelling a change or dismissing a notification.

<Layout grid class="preview transparent">

<div style="grid-column: span 3">

```vue-html
<Button>
  Default button
</Button>
```

</div>

<Button>
  Default button
</Button>

</Layout>

### Primary

The primary button represents the **single positive** action on a page or modal, such as uploading, confirming, and accepting changes.

<Layout grid class="preview">

<div style="grid-column: span 3">

```vue-html
<Button primary>
  Primary button
</Button>
```

</div>

<Button primary>
  Primary button
</Button>

</Layout>

### Secondary

Secondary buttons represent **neutral** actions such as cancelling a change or dismissing a notification.

<Layout grid class="preview secondary">

<div style="grid-column: span 4">

```vue-html
<Button secondary raised>
  Secondary button
</Button>
```

</div>

<Button secondary raised>
  Secondary button
</Button>

</Layout>

Note that on a secondary background, the button needs to be `raised` to make it stand out.

### Destructive

Desctrutive buttons represent **dangerous** actions including deleting items or purging domain information.

<Layout grid class="preview">

<div style="grid-column: span 3">

```vue-html
<Button destructive>
  Destructive button
</Button>
```

</div>

<Button destructive>
  Destructive button
</Button>

</Layout>

## Button variants

Buttons come in different styles that you can use depending on the location of the button.

### Solid

Solid buttons have a filled background. Use these to emphasize the action the button performs.

::: info
This is the default style. If you don't specify a style, a solid button is rendered.
:::

```vue-html
<Button>
  Filled button
</Button>

<Button solid>
  Also filled button
</Button>
```

<Button>
  Filled button
</Button>

<Button solid>
  Also filled button
</Button>

### Outline

Outline buttons have a transparent background. Use these to deemphasize the action the button performs.

```vue-html
<Button outline secondary>
  Outline button
</Button>
```

<Button outline secondary>
  Outline button
</Button>

### Ghost

Ghost buttons have a transparent background and border. Use these to deemphasize the action the button performs.

```vue-html
<Button ghost secondary>
  Ghost button
</Button>
```

<Button ghost secondary>
  Ghost button
</Button>

## Button styles

### Shadow

You can give a button a shadow to add depth.

```vue-html
<Button shadow>
  Shadow button
</Button>
```

<Button shadow>
  Shadow button
</Button>

## Button shapes

You can choose different shapes for buttons depending on their location and use.

### Normal

Normal buttons are slightly rounded rectangles.

::: info
This is the default shape. If you don't specify a type, a normal button is rendered.
:::

```vue-html
<Button>
  Normal button
</Button>
```

<Button>
  Normal button
</Button>

### Round

Round buttons have fully rounded edges.

```vue-html
<Button round>
  Round button
</Button>
```

<Button round>
  Round button
</Button>

## Split button

<Layout class="preview default raised">
<Button split splitIcon="bi-star" splitTitle="Star!" :onSplitClick="()=>console.log('1 star')">I am split</Button>
<Button> I am not split </Button>
<Button disabled> I am not split and I am disabled </Button>
<Button disabled split splitIcon="bi-star" splitTitle="Star!" :onSplitClick="()=>console.log('1 star')">I am split and disabled</Button>
</Layout>

## Button states

### On/Off

You can force an active state by passing an `aria-pressed` prop.

::: tip When do I use a Toggle vs. a Button?

**Use a Button with an `aria-pressed` prop**

- if the semantics of the option change depending whether it's on or off
- to perform asynchronous, stateful and fallible actions

**Examples:**

- Toggle a remote property
- Open/close a section in the UI
- Toolbar buttons that toggle through many options such as "Paragraph/Heading/List"

**Use the [Toggle component](toggle) (a.k.a. switch)**

- for options that don't cause side-effects and never change the Toggle label content based on the Toggle state (think of the traditional checkbox).
- for options that don't have any intermediary state besides "on" and "off"

**Examples:**

- A checkbox in the User settings
- A checkbox in a form that the user submits later

:::

```vue-html
<Button>
  Off
</Button>

<Button aria-pressed>
  On
</Button>
```

**Default:**

<Button>
  Off
</Button>

<Button aria-pressed>
  On
</Button>

---

**Secondary:**

<Button secondary>
  Off
</Button>

<Button secondary aria-pressed>
  On
</Button>

---

**Primary:**

<Button primary>
  Off
</Button>

<Button primary aria-pressed>
  On
</Button>

### Disabled

Disabled buttons are non-interactive and inherit a less bold color than the one provided.

::: tip When do I use `disabled`?

Use the `disabled` property for buttons that the user expects at a certain position, for example in a toolbar or in a row of action buttons.

If there is just one button in a form and its action is disabled, you may instead just remove it.

:::

```vue-html
<Button disabled>
  Disabled button
</Button>
```

<Button disabled>
  Disabled button
</Button>

### Loading

If a user can't interact with a button until something has finished loading, you can add a spinner by passing the `is-loading` prop.

```vue-html
<Button is-loading>
  Loading button
</Button>
```

<Button is-loading>
  Loading button
</Button>

### Promise handling in `@click`

When a function passed to `@click` returns a promise, the button automatically toggles a loading state on click. When the promise resolves or is rejected, the loading state turns off.

::: danger
There is no promise rejection mechanism implemented in the `<Button>` component. Make sure the `@click` handler never rejects.
:::

```vue
<script setup lang="ts">
const click = () => new Promise((resolve) => setTimeout(resolve, 1000));
</script>

<template>
  <Button @click="click"> Click me </Button>
</template>
```

<Button @click="click">
Click me
</Button>

You can override the promise state by passing a false `is-loading` prop.

```vue-html
<Button :is-loading="false">
  Click me
</Button>
```

<Button :is-loading="false">
  Click me
</Button>

## Add an icon

You can use [Bootstrap Icons](https://icons.getbootstrap.com/) in your button component.

::: info

- Icon buttons shrink down to the icon size if you don't pass any content. If you want to keep the button at full width with just an icon, add `button-width` as a prop.
- When combining icons with other content, prefix the icon prop with `right ` to place it after the content.
- To make icons large, add ` large` to the icon prop.

:::

```vue-html
<Button icon="bi-three-dots-vertical" />
<Button round icon="bi-x large" />
<Button primary icon="bi-save" button-width/>
<Button destructive icon="bi-trash">
  Delete
</Button>
<Button low-height icon="right bi-chevron-right">
  Next
</Button>
```

<Layout flex>
<Button icon="bi-three-dots-vertical" />
<Button round secondary icon="bi-x large" />
<Button primary icon="bi-save" button-width/>
<Button destructive icon="bi-trash">
  Delete
</Button>
<Button low-height icon="right bi-chevron-right">
  Next
</Button>
</Layout>

## Set width and alignment

See [Using width](/using-width) and [Using alignment](/using-alignment)

<Layout flex>

```vue-html
    <Button min-content>🐌</Button>
    <Button tiny>🐌</Button>
    <Button buttonWidth>🐌</Button>
    <Button small>🐌</Button>
    <Button auto>🐌</Button>
    <hr />
    <Button alignSelf="start">🐌</Button>
    <Button alignSelf="center">🐌</Button>
    <Button alignSelf="end">🐌</Button>
    <hr />
    <Button alignText="start">🐌</Button>
    <Button alignText="center">🐌</Button>
    <Button alignText="end">🐌</Button>
```

  <Layout class="preview solid primary" stack no-gap>
    <Button min-content>🐌</Button>
    <Button tiny>🐌</Button>
    <Button buttonWidth>🐌</Button>
    <Button small>🐌</Button>
    <Button auto>🐌</Button>
    <hr />
    <Button alignSelf="start">🐌</Button>
    <Button alignSelf="center">🐌</Button>
    <Button alignSelf="end">🐌</Button>
    <hr />
    <Button alignText="start">🐌</Button>
    <Button alignText="center">🐌</Button>
    <Button alignText="end">🐌</Button>
  </Layout>
</Layout>

### Override the cursor

With the css variable `--cursor`, you can override the default (pointer).

<Button style="--cursor: text;">Text cursor here</Button>

### Emphasize a button that responds to SPACE with `autofocus` and ENTER with `fake-focus`

If the user is likely to choose a certain button in a given situation, give it the `autofocus` attribute.
This will put the focus on it so that the user can confirm it by pressing `SPACE` and doesn't need to navigate to it.
The button will be emphasized with a contrasting outline. Primary buttons will draw the outline outside their shape
for increased emphasis and visibility (A11y).

Make sure to not steal focus from a more important control, and to to visibly return focus to whare it was before
after the button is gone. See the `Modal` component ([docs](./modal)) for a complete example.

**If pressing ENTER implicitly activates the button** (and only then), give the button a `fake-focus` attribute.
It indicates that "pressing the enter key has the same effect as pressing this button". An example is a "Best match"
button under an input where the user can search for matching items. This is implemented [in the `Pill` component](./pill)
