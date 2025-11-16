---
layout: page
outline: [2, 3]
---

<script setup lang="ts">
  import Card from '@ui/Card.vue'
  import Button from '@ui/Button.vue'
  import Link from '@ui/Link.vue'
  import Layout from '@ui/Layout.vue'
  import OptionsButton from '@ui/button/Options.vue'
  import Spacer from '@ui/Spacer.vue'
  import Section from '@ui/Section.vue'

  import CardLink from '@/examples/Card.link.vue'
  import CardCombined from '@/examples/Card.combined.vue'
  import CardCategory from '@/examples/Card.category.vue'
  import CardAlert from '@/examples/Card.alert.vue'
  import CardIcon from '@/examples/Card.icon.vue'
  import CardImage from '@/examples/Card.image.vue'
  import CardTags from '@/examples/Card.tags.vue'
  import CardSlots from '@/examples/Card.slots.vue'
  import CardA11y from '@/examples/Card.a11y.vue'

  const alert = ( message: string ) => window?.alert(message)
</script>

```ts
import Card from "@ui/Card.vue"
```

# Card

Organize textual information, links, and interactive buttons in card-sized sections

<<<@/../src/components/ui/Card.vue#props{ts}

## Card as a Link

Add a `:to` prop, either containing an external link (`"https://..."`) or a Vue Router destination:

<Card-link />

<<<@/examples/Card.link.vue#snippet{vue-html}

If you add interactive elements, only the surrounding surfaces will be linked.

::: details Avoid overlapping interactive elements

Avoid adding buttons and links on top of a [linked card](#card-as-a-link). This is an uncommon pattern and will confuse users.

<Card-combined />

<<<@/examples/Card.combined.vue#snippet{vue-html}

:::

## Card as a Category header

Category cards are basic cards that contain only a title. To create a category card, pass a `category` prop.

<Card-category />

::: info Choosing the right heading level

Make sure to implement [accessible heading trees. Do not skip heading levels (h1..h7).](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-3-1a)

The default title will be rendered as a `h6`. To override, set `category="h3"`. Note that this behavior will change in the next update.

:::

<<<@/examples/Card.category.vue#snippet{vue-html 1,5}

::: info

For details on link behavior, [consult the Vue Router docs on `RouterLink`](https://router.vuejs.org/guide/advanced/extending-router-link).

:::

## Add an Image

Pass an image source to the `image` prop or set both `image.src` and `image.style` by passing an object.

::: info

Make sure to pass a `label` parameter to the `image` prop unless it is purely decorative.

:::

<Card-image />

<<<@/examples/Card.image.vue#snippet{vue-html}

## Add an Icon

<Card-icon />

<<<@/examples/Card.icon.vue#snippet{vue-html}

You can combine this prop with any other prop configuration. If you combine it with an image, keep an eye on the contrast ratio between the icon color and the image.

## Add an Alert

::: info

To add props to the alert, add the `alert-props` property to the card. Check out [the Alert component docs](/components/ui/alert) to find out which props are supported;

:::

<Card-alert />

<<<@/examples/Card.alert.vue#snippet{vue-html 2-4}

## Use slots

<Card-slots />

<<<@/examples/Card.slots.vue#snippet{vue-html}

## Add Tags

You can include tags on a card by adding a list of `tags`. These are rendered as [pills](./pill.md).

<Card-tags />

<<<@/examples/Card.tags.vue#snippet{vue-html}

## Differentiate mixed cards visually

Consider differentiating cards by color, size and shadow when mixing several of the following types:

- Cards used for organizing the page spatially
- Cards that represent objects
- Interactive cards (buttons or links)

### Add color

- Choose a color: `default`, `primary`, `secondary`, `destructive`, or a Pastel (red, yellow, purple, green or blue)
- Choose a variant: `raised`, `solid`, `outline`,...

Read more: [Using Color](/using-color)

### Set size

`large` (304px), `medium` (208px), `auto`, `small`, ...

Read more: [Using Width](/using-width)

### Remove shadow

Use the `flat` attribute to remove the automatic shadow. This helps reduce visual noise and differentiates cards.

::: tip Using this component

## A11y Checklist

- [ ] All non-text content like images, charts, icons and infographics, have an appropriate text equivalent. Purely decorative images have `alt=''`. [1.1.1](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-1-1)
- [ ] Text in the card has a 4.5:1 color contrast against the background. Large text needs a 3:1 contrast. Decorative, inactive, logo or incidental text may have any contrast. [1.4.3](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-4-3)
- [ ] Icons and important affordances for interactivity have a contrast of 3:1. [1.4.11](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-4-11)
- [ ] The user can operate all interactive elements inside the card with their keyboard [2.1.1](https://accessibility.education.gov.uk/guidelines/wcag/explorer#2-1-1)
- [ ] The user can tab through the interactive elements contained in the card, in a way that makes sense. [2.4.3](https://accessibility.education.gov.uk/guidelines/wcag/explorer#2-4-3)
- [ ] If the card [is used as a link](#card-as-a-link), then its title or some text at the bottom says exactly where it navigates to [2.4.4](https://accessibility.education.gov.uk/guidelines/wcag/explorer#2-4-4)
- [ ] Else, the title describes the purpose or contents of the card so that a user can skip it if it's not relevant for them. [2.4.6](https://accessibility.education.gov.uk/guidelines/wcag/explorer#2-4-6)
- [ ] If the card has an image or icon with text in them, assistive technology can read this text (e.g. through an `aria-label` attribute or the `title` prop). The visible label (image, icon or title) is not different from the invisible name (e.g. aria-label). [2.5.3](https://accessibility.education.gov.uk/guidelines/wcag/explorer#2-5-3)

## Accessible card

<CardA11y flex level="h3" />

<<<@/examples/Card.a11y.vue#snippet{vue-html}

[Test this example in isolation against WCAG2 criteria](/maintaining-accessibility#card)

:::
