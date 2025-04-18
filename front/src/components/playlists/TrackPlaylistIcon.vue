<script setup lang="ts">
import type { QueueTrack } from '~/composables/audio/queue'
import type { Track } from '~/types'

import { useI18n } from 'vue-i18n'
import { computed } from 'vue'
import { useStore } from '~/store'

import Button from '~/components/ui/Button.vue'

interface Props {
  track?: Track | QueueTrack
  button?: boolean
  border?: boolean
}

withDefaults(defineProps<Props>(), {
  track: undefined,
  button: false,
  border: false
})

const store = useStore()
const { t } = useI18n()

const labels = computed(() => ({
  addToPlaylist: t('components.playlists.TrackPlaylistIcon.button.add')
}))
</script>

<template>
  <Button
    v-if="button"
    primary
    icon="bi-list"
    @click.stop="store.commit('playlists/chooseTrack', track)"
  >
    {{ t('components.playlists.TrackPlaylistIcon.button.add') }}
  </Button>
  <Button
    v-else
    secondary
    icon="bi-list"
    :class="['ui', 'basic', 'circular', 'icon', {'really': !border}, 'button']"
    :aria-label="labels.addToPlaylist"
    :title="labels.addToPlaylist"
    @click.stop="store.commit('playlists/chooseTrack', track)"
  />
</template>
