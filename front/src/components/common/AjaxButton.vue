<script setup lang="ts">
import type { BackendError } from '~/types'

import { ref } from 'vue'

import axios from 'axios'

import Button from '~/components/ui/Button.vue'

interface Events {
  (e: 'action-done', data: any): void
  (e: 'action-error', error: BackendError): void
}

interface Props {
  method: 'get' | 'post' | 'put' | 'patch' | 'delete'
  url: string
}

const emit = defineEmits<Events>()
const props = defineProps<Props>()

const isLoading = ref(false)
const ajaxCall = async () => {
  isLoading.value = true

  try {
    const response = await axios[props.method](props.url)
    emit('action-done', response.data)
  } catch (error) {
    emit('action-error', error as BackendError)
  }

  isLoading.value = false
}
</script>

<template>
  <Button
    secondary
    low-height
    :class="{loading: isLoading}"
    icon="bi-arrow-clockwise"
    @click="ajaxCall"
  >
    <slot />
  </Button>
</template>
