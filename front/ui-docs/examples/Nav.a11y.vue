<script setup lang="ts">
import { ref } from 'vue'

import Nav from '@ui/Nav.vue'
import Layout from '@ui/Layout.vue'
import Toggle from '@ui/Toggle.vue'

// #region model
const tabs = ref([{
  title: "Tab A",
  badge: 1
}, {
  title: "Tab B"
}, {
  title: "Tab C",
  badge: 3
}])
// #endregion model
const isOn=ref<boolean[]>([false, true, false])
</script>

<template>
  <Layout
    article
    class="default"
  >
    <!-- #region snippet -->
    <Nav
      v-slot="{ tabpanels }"
      v-model="tabs"
      tab-query-field="tab"
    >
      <div
        v-for="({ isActive, ...panel }, index) in tabpanels"
        v-show="isActive"
        v-bind="panel"
        :key="panel.key"
        :class="`solid ${['green', 'blue', 'purple'][index]}`"
      >
        Tab content {{ ['1 (green)', '2 (blue)', '3 (purple)'][index] }}
        <hr>
        <Toggle
          v-model="isOn[index]"
          :label="`Toggle ${index}`"
        />
      </div>
    </Nav>
    <!-- #endregion snippet -->
  </Layout>
</template>
