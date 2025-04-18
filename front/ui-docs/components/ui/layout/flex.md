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

# Layout `flex`

Items are laid out in a row and wrapped as they overflow the container.
By default, all items in a row assume the same (maximum) height.

```vue-html
<Layout flex>
  <Card title="A" style="width:100px; min-width:100px"></Card>
  <Card title="B" :tags="['funk', 'dunk', 'punk']"></Card>
  <Card title="C" style="width:100px; min-width:100px"></Card>
  <Card title="D"></Card>
</Layout>
```

<Layout flex class="preview">
  <Card title="A" style="width:100px; min-width:100px"></Card>
  <Card title="B" :tags="['funk', 'dunk', 'punk']"></Card>
  <Card title="C" style="width:100px; min-width:100px"></Card>
  <Card title="D"></Card>
</Layout>

## Use additional `flexbox` properties

<Layout flex
class="preview"
style="font-size:11px; font-weight:bold; --gap: 4px;">

--gap: 4px

<Alert red style="align-self: flex-end;">align-self: flex-end</Alert>
<Alert green style="flex-grow: 1;">flex-grow: 1</Alert>
<Alert yellow style="height: 5rem;">height: 5rem</Alert>
<Alert purple style="width: 100%;">width: 100%</Alert>
</Layout>

Find a list of all styles here: [Flexbox guide on css-tricks](https://css-tricks.com/snippets/css/a-guide-to-flexbox/).
