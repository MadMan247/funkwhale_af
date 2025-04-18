<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { computed } from 'vue'

import { usePlayer } from '~/composables/audio/player'
import { useQueue } from '~/composables/audio/queue'

import Button from '~/components/ui/Button.vue'

// TODO: Check if we want to use `currentTrack` from useQueue() in order to disable some icon. Or not.
const { playPrevious, hasNext, playNext } = useQueue()
const { isPlaying } = usePlayer()

const { t } = useI18n()
const labels = computed(() => ({
  previous: t('components.audio.PlayerControls.labels.previous'),
  play: t('components.audio.PlayerControls.labels.play'),
  pause: t('components.audio.PlayerControls.labels.pause'),
  next: t('components.audio.PlayerControls.labels.next')
}))
</script>

<template>
  <div class="player-controls">
    <Button
      :title="labels.previous"
      :aria-label="labels.previous"
      round
      ghost
      class="control tablet-and-up"
      icon="bi-skip-backward-fill"
      @click.prevent.stop="playPrevious()"
    />
    <Button
      :title="isPlaying ? labels.pause : labels.play"
      round
      ghost
      :aria-label="isPlaying ? labels.pause : labels.play"
      :class="['control', isPlaying ? 'pause' : 'play', 'large']"
      :icon="isPlaying ? 'bi-pause-fill' : 'bi-play-fill'"
      @click.prevent.stop="isPlaying = !isPlaying"
    />
    <Button
      :title="labels.next"
      :aria-label="labels.next"
      round
      ghost
      :disabled="!hasNext"
      class="control"
      icon="bi-skip-forward-fill"
      @click.prevent.stop="playNext()"
    />
  </div>
</template>
