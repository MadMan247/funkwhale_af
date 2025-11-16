<script setup lang="ts">
import { ref } from 'vue'

import Button from '@ui/Button.vue'
import Layout from '@ui/Layout.vue'
import Alert from '@ui/Alert.vue'
import Spacer from '@ui/Spacer.vue'

const isPreview = ref(false)
const alerts = ref<number[]>([])
</script>

<template>
  <Layout
    flex
    article
    class="default solid"
  >
    <!-- #region snippet -->
    <Button
      ghost
      icon="bi bi-clipboard"
      aria-label="Copy the address"
      @click="alerts.unshift(Date.now())"
    />
    <Button
      ghost
      icon="bi bi-eye"
      aria-label="Toggle Preview"
      :aria-pressed="isPreview"
      @click="isPreview = !isPreview"
    />
    <!-- #endregion snippet -->
    <label v-if="isPreview">Preview</label>
    <Layout
      stack
      style="position: fixed; bottom: 0; right: 0;"
    >
      <Alert
        v-for="(date, index) in alerts"
        :key="index"
        green
        aria-label="Dismiss"
        @click="alerts.splice(index, 1)"
      >
        <Layout flex>
          {{ new Date(date).toLocaleString() }}
          <Spacer grow />
          <Button icon="bi bi-x" />
        </Layout>
      </Alert>
    </Layout>
  </Layout>
</template>
