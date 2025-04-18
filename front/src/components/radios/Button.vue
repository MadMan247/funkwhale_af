<script setup lang="ts">
import type { ObjectId, RadioConfig } from '~/store/radios'

import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'
import { computed } from 'vue'

import Button from '~/components/ui/Button.vue'

interface Props {
  customRadioId?: number | null
  type?: string
  clientOnly?: boolean
  objectId?: ObjectId | number | string | null
  radioConfig?: RadioConfig | null
  playOnly?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  customRadioId: null,
  type: '',
  clientOnly: false,
  objectId: null,
  radioConfig: null,
  playOnly: false
})

const store = useStore()
const running = computed(() => {
  if (!store.state.radios.running) {
    return false
  }

  const { current } = store.state.radios
  return current?.type === props.type
    && current?.customRadioId === props.customRadioId
    && (
      (typeof props.objectId === 'object' && current.objectId?.fullUsername === props.objectId?.fullUsername)
        || current.objectId === props.objectId
    )
})

const { t } = useI18n()
const buttonLabel = computed(() => {
  switch (props.radioConfig?.type) {
    case 'tag':
      return running.value
        ? t('components.radios.Button.stopTagsRadio')
        : t('components.radios.Button.startTagsRadio')
    case 'artist':
      return running.value
        ? t('components.radios.Button.stopArtistsRadio')
        : t('components.radios.Button.startArtistsRadio')
    case 'playlist':
      return running.value
        ? t('components.radios.Button.stopPlaylistsRadio')
        : t('components.radios.Button.startPlaylistsRadio')
    default:
      return running.value
        ? t('components.radios.Button.stopRadio')
        : t('components.radios.Button.startRadio')
  }
})

const toggleRadio = () => {
  if (running.value) {
    return store.dispatch('radios/stop')
  }

  return store.dispatch('radios/start', {
    type: props.type,
    objectId: props.objectId,
    customRadioId: props.customRadioId,
    clientOnly: props.clientOnly,
    config: props.radioConfig,
    playOnly: props.playOnly
  })
}
</script>

<template>
  <Button
    :is-active="running"
    primary
    :round="playOnly"
    class="play-button"
    icon="bi-play-fill"
    :square="store.state.auth.authenticated && type === 'custom'"
    @click="toggleRadio"
  >
    <div v-if="!playOnly">
      {{ buttonLabel }}
    </div>
  </Button>
</template>
