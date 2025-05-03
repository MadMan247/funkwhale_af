<script setup lang="ts">
import type { Channel, BackendError } from '~/types'

import axios from 'axios'

import { watch, computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useModal } from '~/ui/composables/useModal.ts'

import Layout from '~/components/ui/Layout.vue'
import Modal from '~/components/ui/Modal.vue'
import Button from '~/components/ui/Button.vue'
import Input from '~/components/ui/Input.vue'
import Alert from '~/components/ui/Alert.vue'

const { t } = useI18n()

const channel = defineModel<Channel>({ required: true })
const emit = defineEmits(['created'])
const newAlbumTitle = ref<string>('')

const isLoading = ref(false)
const submittable = computed(() => newAlbumTitle.value.length > 0)
const errors = ref<string[]>([])

const isOpen = useModal('album').isOpen

watch(isOpen, () => {
  isLoading.value = false
  newAlbumTitle.value = '' // Reset the title to ensure submittable becomes false
})

const submit = async () => {
  isLoading.value = true
  errors.value = []

  try {
    await axios.post('albums/', {
      title: newAlbumTitle.value,
      artist: channel.value.artist?.id
    })
  } catch (error) {
    errors.value = (error as BackendError).backendErrors
  } finally {
    isLoading.value = false
    emit('created')
    isOpen.value = false
  }
}

defineExpose({
  submit
})
</script>

<template>
  <Modal
    v-model="isOpen"
    :title="channel?.artist?.content_category === 'podcast' ? t('components.channels.AlbumModal.header.newSeries') : t('components.channels.AlbumModal.header.newAlbum')"
    class="small"
    :cancel="t('components.channels.AlbumModal.button.cancel')"
  >
    <template #alert>
      <Alert
        v-if="errors?.length > 0"
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
    </template>

    <Layout
      form
      :class="['ui', {loading: isLoading}, 'form']"
      @submit.stop.prevent
    >
      <Input
        v-model="newAlbumTitle"
        required
        type="text"
        :label="t('components.channels.AlbumForm.label.albumTitle')"
      />
    </Layout>

    <template #actions>
      <Button
        :is-loading="isLoading"
        :disabled="!submittable"
        primary
        @click.stop.prevent="submit()"
      >
        {{ t('components.channels.AlbumModal.button.create') }}
      </Button>
    </template>
  </Modal>
</template>
