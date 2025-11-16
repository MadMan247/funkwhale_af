<script setup lang="ts">
import { ref } from 'vue'
import Alert from '@ui/Alert.vue'
import Button from '@ui/Button.vue'
import Slider from '@ui/Slider.vue'
import Layout from '@ui/Layout.vue'

const isAlertStatus = ref(false)
const isAlertUrgent = ref(false)
const timeout = ref<keyof typeof options>('0')

const options = {
  '0': "Toggle instantly",
  '200ms': "⅕ second delay",
  '1000ms': "1s delay",
  '3000ms': "3s delay"
} as const;

const toggleStatus = () => {
  setTimeout(() => {
    isAlertStatus.value = !isAlertStatus.value
  }, parseInt(timeout.value));
}

const toggleUrgent = () => {
  setTimeout(() => {
    isAlertUrgent.value = !isAlertUrgent.value
  }, parseInt(timeout.value));
}
</script>

<template>
  <Layout
    article
    class="solid default"
  >
    <Slider
      v-model="timeout"
      :options
      label="Delay"
    />
    <Layout flex>
      <Button @click="toggleStatus">
        Toggle status message
      </Button>
      <Button @click="toggleUrgent">
        Toggle urgent alert
      </Button>
    </Layout>

    <Layout style="height: 16rem; border: .5px solid;">
      <!-- #region snippet -->
      <Alert
        v-if="isAlertStatus"
        role="status"
        blue
      >
        Your settings have been saved successfully.
      </Alert>

      <Alert
        v-if="isAlertUrgent"
        role="alert"
        red
      >
        Connection lost. Please check your internet connection and try again.
        <template #actions>
          <Button
            aria-label="Close 'connection lost' alert"
            @click="toggleUrgent"
          >
            Dismiss
          </Button>
        </template>
      </Alert>
      <!-- #endregion snippet -->
    </Layout>
  </Layout>
</template>
