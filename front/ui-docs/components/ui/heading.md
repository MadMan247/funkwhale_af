---
layout: page
---

<script setup>
import Heading from "@ui/Heading.vue"

import HeadingAlly from '@/examples/Heading.a11y.vue'
</script>

```ts
import Heading from "@ui/Heading.vue"
```

# Heading

Use a heading when the content or the page structure requires it. Define the visual style independently from the logical hierarchy.

- Each page has exactly one `h1` with the visual size `page-heading`.
- Headings always describe the content below. Do not use headings for input captions.
- Try to avoid gaps in the hierarchy.

## Semantic heading level

Use heading levels wherever you want to add logical (not necessarily visual) hierarchy.

Consult [the allyproject for a comprehensive guide on headings](https://www.a11yproject.com/posts/how-to-accessible-heading-structure/).

## Visual sizes for page sections and subsections

---

```vue-html
<Heading h1="Page heading" page-heading />
```

<Heading h1="Page heading" page-heading />

Use this visual size on the main heading of the page.

---

```vue-html
<Heading h3="Section heading" section-heading />
```

<Heading h3="Section heading" section-heading />

Use section headings to subdivide the main content on the page. Also use for modal headings. This is the default visual size.

---

```vue-html
<Heading h3="Subsection heading" subsection-heading />
```

<Heading h3="Subsection heading" subsection-heading />

Use subsection headings to break long sections or forms with several groups into digestible subsections.

## Visual sizes for special elements

---

```vue-html
<Heading h4="Caption" caption />
```

<Heading h4="Caption" caption />

Caption-style headings are found only within forms.

---

```vue-html
<Heading h3="Title" title />
```

<Heading h3="Title" title />

Use this visual size to title [Tabs](/components/ui/tabs), Channels, [Cards](/components/ui/card) and [Activities](/components/ui/activity).

---

```vue-html
<Heading h3="Radio" radio />
```

<Heading h3="Radio" radio />

Radio cards have giant titles.

---

```vue-html
<Heading h3="Secondary" secondary />
```

<Heading h3="Secondary" secondary />

A card may have a secondary title, [as exemplified in the designs](https://design.funkwhale.audio/#/workspace/a4e0101a-252c-80ef-8003-918b4c2c3927/e3a187f0-0f5e-11ed-adb9-fff9e854a67c?page-id=5e293790-52d3-11ed-9497-8deeaf0bfa97).

## Add content to the left and to the right

```vue-html
<Heading h2="Heading" page-heading>
  <template #before>
    (Before)
  </template>
  <template #after>
    (After)
  </template>
</Heading>
```

<Heading h2="Heading" page-heading>
  <template #before>
    (Before)
  </template>
  <template #after>
    (After)
  </template>
</Heading>

::: tip Using this component

## A11y Checklist

- [ ] Content is organized under headings that describe the following section. [1.3.1](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-3-1)
- [ ] Heading text clearly and concisely describes the section content. [1.3.1](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-3-1)
- [ ] Heading levels follow a logical order and, if possible, don't skip a level. [1.3.1](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-3-1)
- [ ] Each page has exactly one main heading (h1). [1.3.1](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-3-1)
- [ ] Heading text has sufficient contrast (4.5:1) against its background. [1.4.3](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-4-3)
- [ ] Headings are used to label page sections, not for styling text. Visual sizes help users understand the relative importance of headings. [2.4.6](https://accessibility.education.gov.uk/guidelines/wcag/explorer#2-4-6)
- [ ] If using `before` or `after` slots, ensure the added content maintains heading semantics. [4.1.2](https://accessibility.education.gov.uk/guidelines/wcag/explorer#4-1-2)

## Accessible heading

<HeadingA11y />

<<<@/examples/Heading.a11y.vue#snippet{vue-html}

[Test this component in isolation against WCAG2 criteria](/maintaining-accessibility#heading)

:::
