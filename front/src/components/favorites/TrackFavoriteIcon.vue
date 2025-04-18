<script setup lang="ts">
import type { QueueTrack } from '~/composables/audio/queue'
import type { Track } from '~/types'

import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'
import { computed } from 'vue'

import Button from '~/components/ui/Button.vue'

interface Props {
  track?: QueueTrack | Track
  button?: boolean
  border?: boolean
  ghost?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  track: () => ({} as Track),
  button: false,
  border: false,
  ghost: false
})

const { t } = useI18n()
const store = useStore()

const isFavorite = computed(() => store.getters['favorites/isFavorite'](props.track.id))
const title = computed(() => isFavorite.value
  ? t('components.favorites.TrackFavoriteIcon.button.remove')
  : t('components.favorites.TrackFavoriteIcon.button.add')
)
</script>

<template>
  <Button
    v-if="button"
    :icon="isFavorite ? 'bi-heart-fill' : 'bi-heart'"
    :class="['ui', 'pink', {'inverted': isFavorite}, {'favorited': isFavorite}, 'icon', 'labeled', 'button']"
    @click.stop="store.dispatch('favorites/toggle', track.id)"
  >
    <span v-if="isFavorite">
      {{ t('components.favorites.TrackFavoriteIcon.label.inFavorites') }}
    </span>
    <span v-else>
      {{ t('components.favorites.TrackFavoriteIcon.button.add') }}
    </span>
  </Button>
  <Button
    v-else
    :ghost="ghost"
    :secondary="!ghost"
    :icon="isFavorite ? 'bi-heart-fill' : 'bi-heart'"
    :class="['ui', 'favorite-icon', {'pink': isFavorite}, {'favorited': isFavorite}, 'basic', 'circular', 'icon', {'really': !border}, 'button']"
    :aria-label="title"
    :title="title"
    @click.stop="store.dispatch('favorites/toggle', track.id)"
  />
</template>
