<script setup lang="ts">
import { ref } from 'vue'

import Card from '~/components/ui/Card.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Section from '~/components/ui/Section.vue'

const alignLeft = ref(false)
</script>

# Designing Pages

## Grid

The page grid consists of 46px wide tracks, separated by 32px wide gaps. [See examples on design.funkwhale.audio](https://design.funkwhale.audio/#/workspace/582e7be1-0cc7-11ed-87a1-ae44a720651d/e3a00150-0f5e-11ed-adb9-fff9e854a67c?page-id=e7a90671-0f5e-11ed-adb9-fff9e854a67c)

## Page sections

Use the [Layout Section component](/components/ui/layout/section) to structure the page into separate sections, each with a heading. Make sure the heading level hierarchy makes sense.

```vue-html
<Section
    :alignLeft="alignLeft"
    :columns-per-item="3"
    h2="My albums"
    :action="{
        text:'Go to library',
        to:'/'
    }"
>
    <Card small solid yellow title="Album 1" />
    <Card small solid green title="Album 2" />
    <Card small solid blue title="Album 3" />
</Section>
```

<Spacer :size="32" />

<Section
    :alignLeft="alignLeft"
    :columns-per-item="3"
    h2="My albums"
    :action="{
        text:'Go to library',
        to:'/'
    }"
>
    <Card small solid yellow title="Album 1" />
    <Card small solid green title="Album 2" />
    <Card small solid blue title="Album 3" />
</Section>

Sections and their contents are automatically aligned to the default grid.

---

<Card to="navigation"
    title="Designing user navigation and routes"
    min-content
  />
