<script setup lang="ts">
import type { BackendError } from '~/types'

import axios from 'axios'

import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'

import useLogger from '~/composables/useLogger'

import Modal from '~/components/ui/Modal.vue'
import Alert from '~/components/ui/Alert.vue'
import Button from '~/components/ui/Button.vue'

const logger = useLogger()
const { t } = useI18n()

const store = useStore()
const show = computed({
  get: () => store.state.moderation.showFilterModal,
  set: (value) => {
    store.commit('moderation/showFilterModal', value)
    errors.value = []
  }
})

const type = computed(() => store.state.moderation.filterModalTarget.type)
const target = computed(() => store.state.moderation.filterModalTarget.target)

const errors = ref([] as string[])
const isLoading = ref(false)

const hide = async () => {
  isLoading.value = true

  const artistPayload = {
    target: {
      type: type.value,
      id: target.value?.id
    }
  }

  try {
    if (type.value === 'artist') {
      const response = await axios.post('moderation/content-filters/', artistPayload)
      logger.info(`Successfully hidden ${type.value} ${target.value?.id}`)
      show.value = false
      store.state.moderation.lastUpdate = new Date()
      store.commit('moderation/contentFilter', response.data)
      store.commit('ui/addMessage', {
        content: t('components.moderation.FilterModal.message.success'),
        date: new Date()
      })
    } else if (type.value === 'actor') {
      await store.dispatch('moderation/blockActor', target.value?.name)
      logger.info(`Successfully hidden ${type.value} ${target.value?.name}`)
      show.value = false
      store.state.moderation.lastUpdate = new Date()
      store.commit('ui/addMessage', {
        content: t('components.moderation.FilterModal.message.success'),
        date: new Date()
      })
    }
  } catch (error) {
    logger.error(`Error while hiding ${type.value} ${target.value?.id}`)
    errors.value = (error as BackendError).backendErrors
  }

  isLoading.value = false
}
</script>

<template>
  <Modal
    v-model="show"
    is-destructive
    :title="type==='artist' ? t('components.moderation.FilterModal.header.artistModal', {name: target?.name}) : type==='actor' ? t('components.moderation.FilterModal.header.actorModal', {name: target?.name}) : errors.length > 0 ? t('components.moderation.FilterModal.header.failure') : ''"
    :cancel="t('components.moderation.FilterModal.button.cancel')"
  >
    <div class="scrolling content">
      <div class="description">
        <Alert
          v-if="errors.length > 0"
          red
        >
          <ul class="list">
            <li
              v-for="(error, key) in errors"
              :key="key"
            >
              {{ error }}
            </li>
          </ul>
        </Alert>
        <p v-if="type === 'actor'">
          {{ t('components.moderation.FilterModal.warning.createFilter.listActorIntro') }}
        </p>
        <p v-if="type === 'artist'">
          {{ t('components.moderation.FilterModal.warning.createFilter.listArtistIntro') }}
        </p>
        <ul>
          <li>
            {{ t('components.moderation.FilterModal.warning.createFilter.listItem1') }}
          </li>
          <li>
            {{ t('components.moderation.FilterModal.warning.createFilter.listItem2') }}
          </li>
          <li>
            {{ t('components.moderation.FilterModal.warning.createFilter.listItem3') }}
          </li>
          <li>
            {{ t('components.moderation.FilterModal.warning.createFilter.listItem4') }}
          </li>
          <li v-if="type === 'actor'">
            {{ t('components.moderation.FilterModal.warning.createFilter.listItem5') }}
          </li>
        </ul>
        <p>
          {{ t('components.moderation.FilterModal.help.createFilter') }}
        </p>
      </div>
    </div>
    <template #actions>
      <Button
        destructive
        :class="[{loading: isLoading}]"
        @click="hide"
      >
        {{ t('components.moderation.FilterModal.button.hide') }}
      </Button>
    </template>
  </Modal>
</template>
