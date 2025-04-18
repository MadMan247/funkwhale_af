<script setup lang="ts">
import type { QueueItemSource } from '~/types'

import time from '~/utils/time'
import { generateTrackCreditStringFromQueue } from '~/utils/utils'
import { useStore } from '~/store'

import Button from '~/components/ui/Button.vue'

const store = useStore()

interface Events {
  (e: 'play', index: number): void
  (e: 'remove', index: number): void
}

interface Props {
  source: QueueItemSource
  index: number
}

defineEmits<Events>()
defineProps<Props>()
</script>

<template>
  <div
    class="queue-item"
    tabindex="0"
  >
    <div class="handle">
      <i class="bi bi-list" />
    </div>
    <div
      class="image-cell"
      @click="$emit('play', index)"
    >
      <img
        class="ui mini image"
        alt=""
        :src="source.coverUrl"
      >
    </div>
    <div @click="$emit('play', index)">
      <div
        class="title reset ellipsis"
        :title="source.title"
        :aria-label="source.labels.selectTrack"
      >
        <strong>{{ source.title }}</strong><br>
        <span>
          {{ generateTrackCreditStringFromQueue(source) }}
        </span>
      </div>
    </div>
    <div class="duration-cell">
      <template v-if="source.sources.length > 0">
        {{ time.parse(Math.round(source.sources[0].duration ?? 0)) }}
      </template>
    </div>
    <div class="controls">
      <Button
        v-if="store.state.auth.authenticated"
        :aria-label="source.labels.favorite"
        :title="source.labels.favorite"
        :icon="store.getters['favorites/isFavorite'](source.id) ? 'bi-heart-fill' : 'bi-heart'"
        round
        ghost
        square-small
        style="align-self: center;"
        :class="store.getters['favorites/isFavorite'](source.id) ? 'pink' : ''"
        @click.stop="store.dispatch('favorites/toggle', source.id)"
      />
      <Button
        :aria-label="source.labels.remove"
        :title="source.labels.remove"
        icon="bi-x"
        round
        ghost
        square-small
        style="align-self: center;"
        @click.stop="$emit('remove', index)"
      />
    </div>
  </div>
</template>
