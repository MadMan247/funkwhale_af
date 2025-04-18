<script setup>
import { ref } from 'vue'

import Card from '~/components/ui/Card.vue'
import Alert from '~/components/ui/Alert.vue'
import Layout from '~/components/ui/Layout.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Tab from '~/components/ui/Tab.vue'
import Tabs from '~/components/ui/Tabs.vue'
import Toggle from '~/components/ui/Toggle.vue'
import Button from '~/components/ui/Button.vue'

const isGrowing = ref(true)
const noGap = ref(true)
</script>

🡔 [Layout](../layout)

# Layout `columns`

Let items flow like words on a printed newspaper. Works for long, text-heavy content. Consider using `stack`, `flex` and `grid` instead if you want a homogeneous list of items to flow into multiple responsive columns.

<Layout stack no-gap>

```vue-html
<Layout columns :column-width="120">
  <Button icon="bi-star"/>
  <Button icon="bi-star"/>
  <Button icon="bi-star"/>

Normal paragraph. Text flows like in a newspaper. Set the column width in px. Columns will be equally distributed over the width of the container.

  <Card min-content title="Cards...">...break over columns...</Card>

  <Button icon="bi-star"/>
  <Button icon="bi-star"/>
  <Button icon="bi-star"/>
</Layout>
```

<div class="preview">
<Layout columns column-width="120px">
  <Button icon="bi-star"/>
  <Button icon="bi-star"/>
  <Button icon="bi-star"/>

---

Normal paragraph. Text flows like in a newspaper. Set the column width in px. Columns will be equally distributed over the width of the container.

---

<Card auto title="Cards...">...break over columns...</Card>

---

  <Button icon="bi-star"/>
  <Button icon="bi-star"/>
  <Button icon="bi-star"/>
</Layout>
</div>

</Layout>

Make sure that all elements fit the column width, else they will leak into the neighboring columns.

### `no-rule`: Remove the rule (thin line) between columns

<Layout columns column-width="300px">

```vue-html
<Layout columns column-width="40px">
  <div>Lorem ipsum dolor sit amet.</div>
</Layout>

<Layout columns no-rule column-width="40px">
  <div>Lorem ipsum dolor sit amet.</div>
</Layout>
```

<Layout class="preview">
  <Layout columns column-width="40px">
    <div>Lorem ipsum dolor sit amet.</div>
  </Layout>

  <Layout columns no-rule column-width="40px">
    <div>Lorem ipsum dolor sit amet.</div>
  </Layout>
</Layout>

</Layout>

### Tricks

#### Prevent column breaks

Add the following style to the element that you want to preserve whole:

```css
style="break-inside: avoid;"
```
