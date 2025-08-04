<script setup lang="ts">
import { color, setColors } from "~/composables/color"
import { useRoute } from "vue-router"

import Button from "~/components/ui/Button.vue"
import Card from "~/components/ui/Card.vue"
import Link from "~/components/ui/Link.vue"
import Layout from "~/components/ui/Layout.vue"
import Alert from "~/components/ui/Alert.vue"
import Spacer from "~/components/ui/Spacer.vue"

const route = useRoute();
const here = route.path
</script>

# Using Color

## Add color via props

[Alerts](components/ui/alert) support [Pastel](#pastel) attributes. [Buttons](components/ui/button) accept [Color](#color) and [Variant](#variant) attributes. [Cards](components/ui/card) accept [Pastel](#pastel), [Variant](#variant), [Neutral](#neutral) and [Raised](#raised) attributes.

<Layout flex>

```vue-html
<Card solid red title='🌈' />
```

<div class="preview">
  <Card solid red title='🌈' />
</div>

</Layout>

## Add color to a any component or Html tag

1. Choose either:
   - [base color](#colors) (`primary | secondary | destructive`) or
   - [pastel color](#pastel) (`blue | red | green | yellow`) or
   - [neutral beige or gray](#neutral) (`default`) for surfaces
2. Choose a [variant](#color-variants) (`solid | ghost | outline`)
3. Add [interactivity and raise the surface](#interactive-andor-raised)

<Layout flex>

```vue
<script setup>
import { color } from "~/composables/color.ts";
</script>

<template>
  <div v-bind="color({}, ['primary', 'solid', 'interactive', 'raised'])()" />
</template>
```

<div class="preview">
  <div :class="$style.swatch" v-bind="color({}, ['primary', 'solid', 'interactive', 'raised'])()" />
</div>

</Layout>

## Make your component accept color props

`color` accepts two parameters. The first is your props object, the second is a list of defaults.

In this case, if the user of your component doesn't specify any color, it will be 'primary'.
Since the user cannot specify the variant, it will always be 'default'.

```vue
<script setup>
import { type ColorProps, color } from "~/composables/colors.ts";

const props = defineProps<{
  ...
  } & ColorProps>()
</script>

<template>
  <div v-bind="color(props, ['primary', 'solid'])()" />
</template>
```

## Base colors

Keep most of the screen neutral. Secondary surfaces indicate actionability. Use them sparingly. Primary and destructive surfaces immediately catch the eye. Use them only once or twice per screen.

### Neutral

Use neutral colors for non-interactive surfaces

<Layout flex>
  <div class="force-dark-theme">
    <div v-bind="setColors('default solid')">
      <div :class="$style.swatch" v-bind="setColors('default solid')" />
      <div :class="[$style.swatch, $style.deemphasized]" v-bind="setColors('default solid interactive')" />
    </div><div v-bind="setColors('default solid raised')">
      <div :class="$style.swatch" v-bind="setColors('default solid raised')" />
      <div :class="[$style.swatch, $style.deemphasized]" v-bind="setColors('default solid raised interactive')" />
    </div>
  </div>

  <div class="force-light-theme">
    <div v-bind="setColors('default solid')">
      <div :class="$style.swatch" v-bind="setColors('default solid')" />
      <div :class="[$style.swatch, $style.deemphasized]" v-bind="setColors('default solid interactive')" />
    </div><div v-bind="setColors('default solid raised')">
      <div :class="$style.swatch" v-bind="setColors('default solid raised')" />
      <div :class="[$style.swatch, $style.deemphasized]" v-bind="setColors('default solid raised interactive')" />
    </div>
  </div>
</Layout>

### Color

#### Primary

Only use for at most one call-to-action on a screen

<Layout flex>
  <div class="force-dark-theme">
    <div v-bind="setColors('default solid')">
      <div :class="[$style.swatch, $style.deemphasized]" v-bind="setColors('primary solid')" />
      <div :class="[$style.swatch]" v-bind="setColors('primary solid interactive')" />
    </div><div v-bind="setColors('default solid raised')">
      <div :class="[$style.swatch, $style.deemphasized]" v-bind="setColors('primary solid raised')" />
      <div :class="[$style.swatch]" v-bind="setColors('primary solid raised interactive')" />
    </div>
  </div>

  <div class="force-light-theme">
    <div v-bind="setColors('default solid')">
      <div :class="[$style.swatch, $style.deemphasized]" v-bind="setColors('primary solid')" />
      <div :class="[$style.swatch]" v-bind="setColors('primary solid interactive')" />
    </div><div v-bind="setColors('default solid raised')">
      <div :class="[$style.swatch, $style.deemphasized]" v-bind="setColors('primary solid raised')" />
      <div :class="[$style.swatch]" v-bind="setColors('primary solid raised interactive')" />
    </div>
  </div>
</Layout>

#### Secondary

Use for interactive items and non-permanent surfaces such as menus and modals

<Layout flex>
  <div class="force-dark-theme">
    <div v-bind="setColors('default solid')">
      <div :class="$style.swatch" v-bind="setColors('secondary solid')" />
      <div :class="[$style.swatch]" v-bind="setColors('secondary solid interactive')" />
    </div><div v-bind="setColors('default solid raised')">
      <div :class="$style.swatch" v-bind="setColors('secondary solid raised')" />
      <div :class="[$style.swatch]" v-bind="setColors('secondary solid raised interactive')" />
    </div>
  </div>

  <div class="force-light-theme">
    <div v-bind="setColors('default solid')">
      <div :class="$style.swatch" v-bind="setColors('secondary solid')" />
      <div :class="[$style.swatch]" v-bind="setColors('secondary solid interactive')" />
    </div><div v-bind="setColors('default solid raised')">
      <div :class="$style.swatch" v-bind="setColors('secondary solid raised')" />
      <div :class="[$style.swatch]" v-bind="setColors('secondary solid raised interactive')" />
    </div>
  </div>
</Layout>

#### Destructive

Use for dangerous actions

<Layout flex>
  <div class="force-dark-theme">
    <div v-bind="setColors('default solid')">
      <div :class="[$style.swatch, $style.deemphasized]" v-bind="setColors('destructive solid')" />
      <div :class="[$style.swatch]" v-bind="setColors('destructive solid interactive')" />
    </div><div v-bind="setColors('default solid raised')">
      <div :class="[$style.swatch, $style.deemphasized]" v-bind="setColors('destructive solid raised')" />
      <div :class="[$style.swatch]" v-bind="setColors('destructive solid raised interactive')" />
    </div>
  </div>

  <div class="force-light-theme">
    <div v-bind="setColors('default solid')">
      <div :class="[$style.swatch, $style.deemphasized]" v-bind="setColors('destructive solid')" />
      <div :class="[$style.swatch]" v-bind="setColors('destructive solid interactive')" />
    </div><div v-bind="setColors('default solid raised')">
      <div :class="[$style.swatch, $style.deemphasized]" v-bind="setColors('destructive solid raised')" />
      <div :class="[$style.swatch]" v-bind="setColors('destructive solid raised interactive')" />
    </div>
  </div>
</Layout>

### Pastel

Use `Blue`, `Red`, `Purple`, `Green`, `Yellow` for user-defined tags and for friendly messages such as
Alerts

<div :class="$style.swatch" v-bind="setColors('blue solid interactive')" />
<div :class="$style.swatch" v-bind="setColors('red solid interactive')" />
<div :class="$style.swatch" v-bind="setColors('purple solid interactive')" />
<div :class="$style.swatch" v-bind="setColors('green solid interactive')" />
<div :class="$style.swatch" v-bind="setColors('yellow solid interactive')" />

### Variant

You can de-emphasize interactive elements by hiding their background and/or outline.

`Solid` (default), `Ghost`, `Outline`:

<Button round shadow icon="bi-x" solid />

<div :class="$style.swatch" v-bind="setColors('solid raised')">
  <Button round icon="bi-x" ghost />
  <Spacer />
  <Button round icon="bi-x" outline />
</div>

<br/>

<Button round shadow icon="bi-x" primary solid />

<div :class="$style.swatch" v-bind="setColors('primary solid')">
  <Button round icon="bi-x" primary ghost />
  <Spacer />
  <Button round icon="bi-x" primary outline />
</div>

### Interactive and/or Raised

Use raised surfaces sparingly, about ¼ of the screen. Only use raised surfaces to highlight one area of a component over others. Good examples are `aside`s such as the sidebar or info-boxes.

Space out interactive surfaces.

<Layout>

<div class="force-light-theme">
<Layout flex>
  <div>
    <div v-bind="setColors('default solid')">
      <div :class="[$style.swatch]" v-bind="setColors('solid')" />
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive')" />
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive')" disabled/>
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive')" aria-pressed />
    </div>
    <div v-bind="setColors('secondary solid')">
      <div :class="[$style.swatch]" v-bind="setColors('solid')" />
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive')" />
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive')" disabled/>
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive')" aria-pressed />
    </div>
    <div v-bind="setColors('primary solid')">
      <div :class="[$style.swatch]" v-bind="setColors('solid')" />
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive')" />
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive')" disabled/>
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive')" aria-pressed />
    </div>
  </div><div>
    <div v-bind="setColors('default raised solid')">
      <div :class="[$style.swatch]" v-bind="setColors('solid raised')" />
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive raised')" />
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive raised')" disabled/>
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive raised')" aria-pressed />
    </div>
    <div v-bind="setColors('secondary raised solid')">
      <div :class="[$style.swatch]" v-bind="setColors('solid raised')" />
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive raised')" />
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive raised')" disabled/>
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive raised')" aria-pressed />
    </div>
    <div v-bind="setColors('primary raised solid')">
      <div :class="[$style.swatch]" v-bind="setColors('solid raised')" />
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive raised')" />
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive raised')" disabled/>
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive raised')" aria-pressed />
    </div>
  </div>
</Layout>
</div>

<div class="force-dark-theme">
<Layout flex>
  <div>
    <div v-bind="setColors('default solid')">
      <div :class="[$style.swatch]" v-bind="setColors('solid')" />
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive')" />
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive')" disabled/>
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive')" aria-pressed />
    </div>
    <div v-bind="setColors('secondary solid')">
      <div :class="[$style.swatch]" v-bind="setColors('solid')" />
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive')" />
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive')" disabled/>
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive')" aria-pressed />
    </div>
    <div v-bind="setColors('primary solid')">
      <div :class="[$style.swatch]" v-bind="setColors('solid')" />
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive')" />
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive')" disabled/>
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive')" aria-pressed />
    </div><br/>Normal
  </div><div>
    <div v-bind="setColors('default raised solid')">
      <div :class="[$style.swatch]" v-bind="setColors('solid raised')" />
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive raised')" />
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive raised')" disabled/>
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive raised')" aria-pressed />
    </div>
    <div v-bind="setColors('secondary raised solid')">
      <div :class="[$style.swatch]" v-bind="setColors('solid raised')" />
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive raised')" />
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive raised')" disabled/>
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive raised')" aria-pressed />
    </div>
    <div v-bind="setColors('primary raised solid')">
      <div :class="[$style.swatch]" v-bind="setColors('solid raised')" />
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive raised')" />
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive raised')" disabled/>
      <div :class="[$style.swatch]" v-bind="setColors('solid interactive raised')" aria-pressed />
    </div><br/><strong>Raised</strong>
  </div>
</Layout>
</div>

</Layout>

<Layout flex style="align-items: center;">

| neutral   |
| --------- |
| secondary |
| primary   |

| (normal) | interactive | disabled | pressed |
| -------- | ----------- | -------- | ------- |

</Layout>

## Palette

The color palette consists of Blues, Reds, Grays, Beiges, as well as pastel blue/red/green/yellow.

`fw-blue-010 - 100 - 400..900`

<div :class="[$style.swatch, $style.tiny]" style="background:var(--fw-blue-010)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-blue-100)" />
   
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-blue-400)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-blue-500)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-blue-600)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-blue-700)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-blue-800)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-blue-900)" />

`fw-red-010 - 100 - 400..900`

<div :class="[$style.swatch, $style.tiny]" style="background:var(--fw-red-010)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-red-100)" />
   
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-red-400)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-red-500)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-red-600)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-red-700)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-red-800)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-red-900)" />

`fw-gray-100..800 - 850 - 900 - 950 - 960 - 970`

<div :class="[$style.swatch, $style.small]" style="background:var(--fw-gray-100)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-gray-200)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-gray-300)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-gray-400)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-gray-500)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-gray-600)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-gray-700)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-gray-800)" />
<div :class="[$style.swatch, $style.tiny]" style="background:var(--fw-gray-850)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-gray-900)" />
<div :class="[$style.swatch, $style.tiny]" style="background:var(--fw-gray-950)" />
<div :class="[$style.swatch, $style.tiny]" style="background:var(--fw-gray-960)" />
<div :class="[$style.swatch, $style.tiny]" style="background:var(--fw-gray-970)" />

`fw-beige-100..400`

<div :class="[$style.swatch, $style.small]" style="background:var(--fw-beige-100)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-beige-200)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-beige-300)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-beige-400)" />

---

`fw-pastel-blue-1..4`

<div :class="[$style.swatch, $style.small]" style="background:var(--fw-pastel-blue-1)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-pastel-blue-2)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-pastel-blue-3)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-pastel-blue-4)" />

`fw-pastel-red-1..4`

<div :class="[$style.swatch, $style.small]" style="background:var(--fw-pastel-red-1)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-pastel-red-2)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-pastel-red-3)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-pastel-red-4)" />

`fw-pastel-purple-1..4`

<div :class="[$style.swatch, $style.small]" style="background:var(--fw-pastel-purple-1)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-pastel-purple-2)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-pastel-purple-3)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-pastel-purple-4)" />

`fw-pastel-green-1..4`

<div :class="[$style.swatch, $style.small]" style="background:var(--fw-pastel-green-1)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-pastel-green-2)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-pastel-green-3)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-pastel-green-4)" />

`fw-pastel-yellow-1..4`

<div :class="[$style.swatch, $style.small]" style="background:var(--fw-pastel-yellow-1)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-pastel-yellow-2)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-pastel-yellow-3)" />
<div :class="[$style.swatch, $style.small]" style="background:var(--fw-pastel-yellow-4)" />

---

In addition, we have a single shade of orange used for secondary indicators such as active tabs: `fw-secondary`

<div :class="$style.swatch" style="background:var(--fw-secondary)" />

## Theme

Many browsers automatically turn on "night mode" to lower the light emission of the screen. Users can override the browser theme in their settings menu.

In both "dark mode" and "light mode", the colors must provide adequate contrast and consistency.

Read more about [style modules in the corresponding vue docs](https://vuejs.org/api/sfc-css-features.html#css-modules).

For testing purposes and side-by-side comparisons, you can add the classes `force-dark-theme` and `force-light-theme`.

## Semantic colors

We use semantic color variables that can mean a different shade depending on the currently chosen theme

- primary
- secondary (default)
- destructive

## Color variants

For each semantic color, we set a foreground and a background. In addition, we need to check context: A button should have a stronger shade when the mouse is hovering over it. When a surface is raised over another surface, it should have a stronger shade, too.

**Variants:**

- ghost (default for most things except buttons)

  > affects text color but leaves the border and background transparent.
  > Make sure to provide a surface beneath with adequate contrast.

- outline

  > affects text color and border and leaves the background transparent
  > Make sure to provide a surface beneath with adequate contrast.

- solid (default for buttons)
  > affects text color, border color and background color

[-> Example: #variant](#variant)

**Variants can optionally be made interactive and/or raised:**

- no alteration (default)

- raised

> affects text color, border color and background color

- interactive

  > user interaction affects text color, border color and background color
  >
  > - can be disabled
  > - can be active
  > - can be exact-active
  > - can be hovering

- interactive-raised
  > combine `raised` and `interactive`

[-> Example: #interactive-and-or-raised](#interactive-and-or-raised)

## Theme color definitions

All colors are defined in `front/src/style/colors.scss`.

Its structure is as follows:

<Layout stack style="--width:100%; background:#0002;">

<Card full solid purple title="(1) Palette">

Defining [all funkwhale color values](#palette)

</Card>

<Card full solid blue title="(2) Choosing the semantic colors from the palette">

both for light and dark theme, and both normal and raised:

- default
- secondary
- primary
- destructive
- blue
- red
- purple
- green
- yellow

</Card>

<Card full solid green title="(3) Applying colors">

(for all elements not managed by vitepress)

- (a) Applying colors to things with no explicit Variant props, such as headings and paragraphs, simple links, focusable elements
- (b) Applying colors to things with explicit Variant props: - solid (and default buttons) - ghost - outline

</Card>

</Layout>

## Change a color value

For example, you want to make all blue hues more cyan-ish or mute all reds.

- Find the color value you want to change in **section 1 (Palette)**
- Change it
- Keep this page open and check under [Palette](#palette) if the colors are still in harmony with each other. Also make sure all recommended color combinations still meet the relevant WCGA2 recommendations for contrast

## Alter the shade of a color

In funkwhale components, we use semantic color names such as `primary`, `destructive`, `default` (neutral). Now, you find, for example, that a secondary button has low contrast in light mode, and you decide to alter the text color.

- Find the relevant section in **section 2 (hoosing the semantic colors from the palette)**. In our example, it's `.secondary` under `theme-light`.
- You see that the values are `--color: var(--fw-gray-700);` and `--background-color: var(--fw-gray-200);`, and you change `--color` to `var(--fw-gray-900)`.
- Test your changes. If nothing changes, then there is a Css rule with higher precedence. Find and eliminate these sorts of competing rules.

## Choose a different style for a specific variant

For example, you want to add visible lines around ghost links and buttons when the user hovers over them.

- Find the variant class in **section 3 (Applying colors)**. In our example, it is `.ghost`.
- In our example, we would add the line `border-color: var(--hover-border-color);` under `&:hover` to make the outline on interactive items visible on hover.
- Make sure to test all affected components before committing and merging the changes

## Overview of current styles

Make sure that:

- Contrasts meet WCAG2 requirements
- Colors and outlines communicate the correct dose of prominence
- All styles are different enough from each other to not be confused

Here is the meaning the styles should convey:

- **active**: The user has chosen this option
- **Here**: The user is exactly here
- **raised**: Things on this surface complement the main area (sidebar, aside, ...)
- **default**: Background of the app
- **secondary**: This is interactive! As of now, secondary things need a secondary background.
- **primary**: Important!

### Links and buttons

---

<Layout flex style="--gap:4px;">

<Card min-content title="Default" solid default>
  <span>
    Inline <Link to=""> Link </Link> and <Link to=""> Link </Link>
  </span>

---

  <Layout flex  style="margin: 0 -22px; justify-content:space-evenly;">
    <Layout >
      Here
      <Link ghost :to="here"> ghost </Link>
      <Link outline :to="here"> outline </Link>
      <Link solid raised :to="here"> solid raised </Link>
    </Layout>
    <Layout >
      Elsewhere
      <Link ghost to="-"> ghost </Link>
      <Link outline to="-"> outline </Link>
      <Link solid raised to="-"> solid raised </Link>
    </Layout>
  </Layout>

---

<Button> Button </Button>
<Button ghost> Button ghost </Button>
<Button outline> Button outline </Button>
<Button solid> Button solid </Button>
<Button solid aria-pressed > Button active </Button>
<Button disabled> Button disabled </Button>
<Button primary> Button primary </Button>

---

<Button raised> Button raised </Button>
<Button raised ghost> Button raised ghost </Button>
<Button raised outline> Button raised outline </Button>
<Button raised solid> Button raised solid </Button>
<Button raised aria-pressed > Button active </Button>
<Button raised disabled> Button disabled </Button>
</Card>

<Card min-content title="Default raised" solid default raised>
  <span>
    Inline <Link to=""> Link </Link> and <Link to=""> Link </Link>
  </span>

---

  <Layout flex  style="margin: 0 -22px; justify-content:space-evenly;">
    <Layout >
      Here
      <Link ghost :to="here"> ghost </Link>
      <Link outline :to="here"> outline </Link>
      <Link solid raised :to="here"> solid raised </Link>
    </Layout>
    <Layout >
      Elsewhere
      <Link ghost to="-"> ghost </Link>
      <Link outline to="-"> outline </Link>
      <Link raised to="-"> solid raised </Link>
    </Layout>
  </Layout>

---

<Button> Button </Button>
<Button ghost> Button ghost </Button>
<Button outline> Button outline </Button>
<Button solid> Button solid </Button>
<Button aria-pressed > Button active </Button>
<Button disabled> Button disabled </Button>
<Button primary> Button primary </Button>

---

<Button raised> Button raised </Button>
<Button raised ghost> Button raised ghost </Button>
<Button raised outline> Button raised outline </Button>
<Button raised solid> Button raised solid </Button>
<Button raised aria-pressed > Button active </Button>
<Button raised disabled> Button disabled </Button>
</Card>

<Card min-content title="Secondary" solid secondary>
  <span>
    Inline <Link to=""> Link </Link> and <Link to=""> Link </Link>
  </span>

---

  <Layout flex  style="margin: 0 -22px; justify-content:space-evenly;">
    <Layout >
      Here
      <Link ghost :to="here"> ghost </Link>
      <Link outline :to="here"> outline </Link>
      <Link solid raised :to="here"> solid raised </Link>
    </Layout>
    <Layout >
      Elsewhere
      <Link ghost to="-"> ghost </Link>
      <Link outline to="-"> outline </Link>
      <Link solid raised to="-"> solid raised </Link>
    </Layout>
  </Layout>

---

<Button> Button </Button>
<Button ghost> Button ghost </Button>
<Button outline> Button outline </Button>
<Button solid> Button solid </Button>
<Button aria-pressed > Button active </Button>
<Button disabled> Button disabled </Button>
<Button primary> Button primary </Button>

---

<Button raised> Button raised </Button>
<Button raised ghost> Button raised ghost </Button>
<Button raised outline> Button raised outline </Button>
<Button raised solid> Button raised solid </Button>
<Button raised aria-pressed > Button raised active </Button>
<Button raised disabled> Button raised disabled </Button>
</Card>

<Card min-content title="Secondary raised" solid secondary raised>
  <span>
    Inline <Link to=""> Link </Link> and <Link to=""> Link </Link>
  </span>

---

  <Layout flex  style="margin: 0 -22px; justify-content:space-evenly;">
    <Layout >
      Here
      <Link ghost :to="here"> ghost </Link>
      <Link outline :to="here"> outline </Link>
      <Link solid raised :to="here"> solid raised </Link>
    </Layout>
    <Layout >
      Elsewhere
      <Link ghost to="-"> ghost </Link>
      <Link outline to="-"> outline </Link>
      <Link solid raised to="-"> solid raised </Link>
    </Layout>
  </Layout>

---

<Button> Button </Button>
<Button ghost> Button ghost </Button>
<Button outline> Button outline </Button>
<Button solid> Button solid </Button>
<Button solid aria-pressed > Button active </Button>
<Button disabled> Button disabled </Button>
<Button primary> Button primary </Button>

---

<Button raised> Button raised </Button>
<Button raised ghost> Button raised ghost </Button>
<Button raised outline> Button raised outline </Button>
<Button raised solid> Button raised solid </Button>
<Button raised aria-pressed > Button active </Button>
<Button raised disabled> Button raised disabled </Button>
</Card>

</Layout>

<style module>
    .swatch {
      transition:all .15s, filter 0s;
        border-radius: 2em;
        min-width: 3.2em;
        min-height: 3.2em;
        margin: 1ch;
        display: inline-flex;
        box-shadow: 1px 2px 7px #0003, 0px 0px 1px #0009;
        align-items:center;
        justify-items:center;
        position:relative;

        &::after {
          position:absolute;
          inset:13%;
          content:"fw";
          line-height:2.68em;
          font-size:80%;
          text-align: center;
          transform:rotate(15deg);
          letter-spacing:-.02em;
          font-weight:800;
        }
        &:is(:not(:global(.solid)):not(:hover),:has(*))::after {
          opacity:0
        }
    }
    :not(:hover)>.deemphasized {
      filter:blur(4px);
      opacity:.5;
      &::after {
        opacity:0;
      }
    }

    .small, .tiny {
        margin: .25rem;
        min-width: 1.6em;
        min-height: 1.6em;
        box-shadow: 1px 2px 4px #0002, 0px 0px 1px #0007;
        &::after{
          font-size:43%;
          outline: none;
        }
    }
    .tiny{
        margin:  .5rem .25rem;
        min-width: 1em;
        min-height: 1em;
        box-shadow: 1px 2px 4px #0002, 0px 0px 1px #0007;
        &::after{
          font-size:27%;
        }
    }
</style>
