<script setup lang="ts">
import { ref } from 'vue'
import Pills from '@ui/Pills.vue'
import Layout from '@ui/Layout.vue'

// #region model
const pills = ref < {currents: { type: 'custom' | 'preset', label: string }[]}>({ currents: [{
  type: 'preset',
  label: "A"
}, {
  type: 'custom',
  label: "B"
}, {
  type: 'custom',
  label: "C"
}]})
// #endregion model
</script>

<template>
  <Layout article>
    <!-- #region pills -->
    <Pills
      :get="p => { pills = p }"
      :set="_ => pills"
    />
    <!-- #endregion pills -->
  </Layout>
</template>
