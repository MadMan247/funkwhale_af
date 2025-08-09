<script setup lang="ts">
import type { Playlist } from '~/types'

import PlayButton from '~/components/audio/PlayButton.vue'
import defaultCover from '~/assets/audio/default-cover.png'
import { momentFormat } from '~/utils/filters'
import { ref, computed } from 'vue'
import { useStore } from '~/store'
import { useI18n } from 'vue-i18n'

import moment from 'moment'

import Card from '~/components/ui/Card.vue'
import Spacer from '~/components/ui/Spacer.vue'
import ActorLink from '~/components/common/ActorLink.vue'

interface Props {
  playlist: Playlist
}

const props = defineProps<Props>()
const store = useStore()
const { t } = useI18n()

const images = computed(() => {
  const urls = props.playlist.album_covers.slice(0, 4).map(url => store.getters['instance/absoluteUrl'](url))

  while (urls.length < 4) {
    urls.push(defaultCover)
  }

  return urls
})

const bgcolors = ref([
  '#f2efef',
  '#eee9e9',
  '#ddd9d9',
  '#cfcaca',
  '#b3afaf',
  '#908888',
  '#605656',
  '#4d4547',
  '#292525',
  '#403a3b',
  '#322f2f'
])

function shuffleArray (array: string[]): string[] {
  return [...array].sort(() => Math.random() - 0.5)
}

const randomizedColors = computed(() => shuffleArray(bgcolors.value))

// TODO: Chseck if the following function has a use
// const goToPlaylist = () => {
//   router.push({ name: 'library.playlists.detail', params: { id: props.playlist.id } })
// }

const updatedTitle = computed(() => {
  const date = momentFormat(new Date(props.playlist.modification_date ?? '1970-01-01'))
  return t('views.playlists.Card.title', { date })
})
const updatedAgo = computed(() => moment(props.playlist.modification_date).fromNow())

</script>

<template>
  <Card
    :title="playlist.name"
    :to="{ name: 'library.playlists.detail', params: { id: playlist.uuid } }"
    small
  >
    <template #topright>
      <!-- TODO: playlist.is_playable is always false -->
      <PlayButton
        icon-only
        :is-playable="true"
        :playlist="playlist"
      />
    </template>

    <template #image>
      <div class="playlist-grid">
        <img
          v-for="(url, idx) in images"
          :key="idx"
          v-lazy="url"
          :alt="playlist.name"
          :style="{ backgroundColor: randomizedColors[idx % randomizedColors.length] }"
        >
      </div>
    </template>

    <template #default>
      <div class="playlist-meta">
        <span>{{ t('vui.by-user') }}</span>
        <Spacer :size="8" />
        <ActorLink
          :actor="playlist.actor"
          :avatar="true"
          discrete
        />
      </div>
    </template>

    <template #footer>
      <time
        :datetime="playlist.modification_date"
        :title="updatedTitle"
      >
        {{ updatedAgo }}
      </time>
      <i class="bi bi-dot" />
      <span>{{ t('components.playlists.Card.meta.tracks', playlist.tracks_count) }}</span>
      <!-- TODO: playlist.is_playable is always false -->
      <PlayButton
        dropdown-only
        :is-playable="true"
        :playlist="playlist"
      />
    </template>
  </Card>
</template>

<style lang="scss" scoped>
.playlist-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: 2px;

  > img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.play-button {
  top: 16px;
  right: 16px;
}

.playlist-meta {
  display: flex;
}

.playlist-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 0 8px;
}
</style>
