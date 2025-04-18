<script setup lang="ts">
import type { BackendError, Channel } from '~/types'

import { computed, watch, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'

import Layout from '~/components/ui/Layout.vue'
import Alert from '~/components/ui/Alert.vue'
import Input from '~/components/ui/Input.vue'

interface Events {
  (e: 'submittable', value: boolean): void
  (e: 'loading', value: boolean): void
  (e: 'created'): void
}

const channel = defineModel<Channel>({ required: true })

const { t } = useI18n()

const emit = defineEmits<Events>()

const title = ref('')

const errors = ref([] as string[])
const isLoading = ref(false)
const submit = async () => {
  isLoading.value = true
  errors.value = []

  try {
    await axios.post('albums/', {
      title: title.value,
      artist: channel.value.artist?.id
    })

    emit('created')
  } catch (error) {
    errors.value = (error as BackendError).backendErrors
  }

  isLoading.value = false
}

const submittable = computed(() => title.value.length > 0)
watch(submittable, (value) => emit('submittable', value))
watch(isLoading, (value) => emit('loading', value))

defineExpose({
  submit
})
</script>

<template>
  <Layout
    form
    :class="['ui', {loading: isLoading}, 'form']"
    @submit.stop.prevent
  >
    <Alert
      v-if="errors.length > 0"
      red
    >
      <h4 class="header">
        {{ t('components.channels.AlbumForm.header.error') }}
      </h4>
      <ul class="list">
        <li
          v-for="(error, key) in errors"
          :key="key"
        >
          {{ error }}
        </li>
      </ul>
    </Alert>
    <div class="ui required field">
      <Input
        v-model="title"
        type="text"
        :label="t('components.channels.AlbumForm.label.albumTitle')"
      />
    </div>
  </Layout>
</template>
