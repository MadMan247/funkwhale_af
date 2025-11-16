---
layout: page
---

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

# Layout `stack`

Add space between vertically stacked items

<Layout flex>

```vue-html
<Layout stack>
  <Card title="A"></Card>
  <Card title="B"></Card>
  <Card title="C"></Card>
  <Card title="D"></Card>
  <Card title="E"></Card>
</Layout>
```

<div class="preview">
<Layout stack>
  <Card title="A"></Card>
  <Card title="B"></Card>
  <Card title="C"></Card>
  <Card title="D"></Card>
  <Card title="E"></Card>
</Layout>
</div>

</Layout>
