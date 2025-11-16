---
layout: page
---

<script setup lang="ts">
import Table from "@ui/Table.vue";
import Link from "@ui/Link.vue";
import Button from "@ui/Button.vue"; // Need to import this, else vitepress will not load the stylesheet with the colors.

import TableA11y from "@/examples/Table.a11y.vue"
</script>

```ts
import Table from '@ui/Table.vue'
```

# Table

Arrange cells in a grid.

For every row, add exactly one element per column.

<Link
    to="https://design.funkwhale.audio/#/workspace/a4e0101a-252c-80ef-8003-918b4c2c3927/e3a187f0-0f5e-11ed-adb9-fff9e854a67c?page-id=6ca536f0-0f5f-11ed-adb9-fff9e854a67c">
    Design [Penpot]
</Link>

**Prop** `grid-template-columns`: An array of the column widths. You can make a column either fixed-width or use part of the available space:

- `100px`: Exactly this width
- `auto`: The the widest cell in the column
- `1fr`: A certain fraction of the remaining space

The whole table always has a width of 100% (or `stretch`, if inside a flex or grid context). If the minimum sizes don't fit, all cells will shrink proportionally.

```vue-html
<Table :grid-template-columns="['100px', 'auto', '2fr', '1fr']">
    <b>100px</b>
    <b>auto</b>
    <b>2fr</b>
    <b>1fr</b>
</Table>
```

<Table :grid-template-columns="['100px', 'auto', '2fr', '1fr']">
    <b>100px</b>
    <b>auto</b>
    <b>2fr</b>
    <b>1fr</b>
</Table>

## Add a table header

Use the `#header` slot to add items to the header. Make sure to add one item per column.

```vue-html
<Table :grid-template-columns="['3fr', '1fr']">
    <template #header>
        <label >Column 1</label>
        <label >Column 2</label>
    </template>
    <label>A</label>
    <label>B</label>
</Table>
```

<Table :grid-template-columns="['3fr', '1fr']">
    <template #header>
        <label >Column 1</label>
        <label >Column 2</label>
    </template>
    <label>A</label>
    <label>B</label>
</Table>

## Let cells span multiple rows or columns

- Cells automatically expand into the **next column** if the following item is empty. Make sure the first element in each row is not empty!
- You can let elements span **multiple rows** by adding `style=grid-row: span 3`. In this case, you have to remove the corresponding cells directly below.

```vue-html
<Table :grid-template-columns="['48px', '48px', 'auto', 'auto', 'auto', '48px', '64px', '48px']">
  <template #header>
    <label></label>
    <label></label>
    <label>Title</label>
    <label>Album</label>
    <label>Artist</label>
    <label></label>
    <label>⏱</label>
    <label></label>
  </template>

  <!-- Row 1 -->
  <div> </div>
  <div>C1</div>
  <div>Title 1</div>
  <div></div>
  <div>Artist 1</div>
  <div></div>
  <div>D1</div>
  <div>⌄</div>

  <!-- Row 2 -->
  <div>B2</div>
  <div>C2</div>
  <div>Title 2</div>
  <div style="grid-row: span 2; height: auto; background: blue;">Album 2</div>
  <div>Artist 2</div>
  <div>F2</div>
  <div>D2</div>
  <div>⌄</div>

  <!-- Row 3 -->
  <div>B3</div>
  <div>C3</div>
  <div>Title 3</div>
  <div>Artist 3</div>
  <div>F3</div>
  <div>D3</div>
  <div>⌄</div>

  <!-- Row 4 -->
  <div>B4</div>
  <div>C4</div>
  <div>Title 4</div>
  <div></div>
  <div></div>
  <div>F4</div>
  <div>D4</div>
  <div>⌄</div>
</Table>
```

<Table :grid-template-columns="['48px', '48px', 'auto', 'auto', 'auto', '48px', '64px', '48px']">
  <template #header>
    <label></label>
    <label></label>
    <label>Title</label>
    <label>Album</label>
    <label>Artist</label>
    <label></label>
    <label>⏱</label>
    <label></label>
  </template>

  <!-- Row 1 -->
  <div> </div>
  <div>C1</div>
  <div>Title 1</div>
  <div></div>
  <div>Artist 1</div>
  <div></div>
  <div>D1</div>
  <div>⌄</div>

  <!-- Row 2 -->
  <div>B2</div>
  <div>C2</div>
  <div>Title 2</div>
  <div style="grid-row: span 2; height: auto; background: blue;">Album 2</div>
  <div>Artist 2</div>
  <div>F2</div>
  <div>D2</div>
  <div>⌄</div>

  <!-- Row 3 -->
  <div>B3</div>
  <div>C3</div>
  <div>Title 3</div>
  <div>Artist 3</div>
  <div>F3</div>
  <div>D3</div>
  <div>⌄</div>

  <!-- Row 4 -->
  <div>B4</div>
  <div>C4</div>
  <div>Title 4</div>
  <div></div>
  <div></div>
  <div>F4</div>
  <div>D4</div>
  <div>⌄</div>
</Table>

## Add props to the table header

To add class names and other properties to the table header, set the `header-props` prop. In the following example, the whole header section is made inert.

Note that `style` properties may not have an effect because the header section is `display: contents`. Instead, add a custom attribute and add scoped style rule targeting your attribute.

```vue-html
<Table
    :grid-template-columns="['1fr', '1fr']"
    :header-props="{ inert: '' }"
>
  <template #header>
    <label>
        <Button low-height primary @click="console.log('clicked 1')">1</Button>
    </label>
    <label>
        <Button low-height primary @click="console.log('clicked 2')">2</Button>
    </label>
  </template>
</Table>
```

<Table
    :grid-template-columns="['1fr', '1fr']"
    :header-props="{ inert: '' }"
>
  <template #header>
    <Button low-height primary @click="console.log('clicked 1')">1</Button>
    <Button low-height primary @click="console.log('clicked 2')">2</Button>
  </template>
</Table>

::: tip Using this component

## A11y Checklist

- [ ] Make sure content order in the markup makes sense when read linearly (important for screen readers and small screen devices). [1.3.2](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-3-2)
- [ ] If your layout reflows or changes based on screen size, ensure content remains readable without horizontal scrolling at 400% zoom. [1.4.10](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-4-10)
- [ ] For table cells containing forms or interactive elements, make sure the tab order matches the visual layout. [2.4.3](https://accessibility.education.gov.uk/guidelines/wcag/explorer#2-4-3)

Note that the current implementation does not use the semantic HTML5 element `<table>` by default. You may want to use semantic elements for the table slots to ensure screen readers and other assistive technology recognizes it as a table.

## Accessible table

<Layout article flex>
  <Table-a11y />
</Layout>

<<<@/examples/Table.a11y.vue#snippet{vue-html}

[Test this component in isolation against WCAG2 criteria](/maintaining-accessibility#table)

:::
