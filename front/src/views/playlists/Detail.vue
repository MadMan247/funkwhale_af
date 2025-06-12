<script setup lang="ts">
import type { PlaylistTrack, Playlist, Track } from '~/types'

import { useI18n } from 'vue-i18n'
import { ref, computed } from 'vue'
import { useStore } from '~/store'

import axios from 'axios'

import defaultCover from '~/assets/audio/default-cover.png'
import PlaylistEditor from '~/components/playlists/Editor.vue'
import EmbedWizard from '~/components/audio/EmbedWizard.vue'
import HumanDate from '~/components/common/HumanDate.vue'
import TrackTable from '~/components/audio/track/Table.vue'
import PlayButton from '~/components/audio/PlayButton.vue'
import Layout from '~/components/ui/Layout.vue'
import Header from '~/components/ui/Header.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Loader from '~/components/ui/Loader.vue'
import Button from '~/components/ui/Button.vue'
import Modal from '~/components/ui/Modal.vue'
import Alert from '~/components/ui/Alert.vue'

import PlaylistDropdown from '~/components/playlists/PlaylistDropdown.vue'

import useErrorHandler from '~/composables/useErrorHandler'
import useWebSocketHandler from '~/composables/useWebSocketHandler'

// TODO: Is this event ever caught somewhere?
// interface Events {
//   (e: 'libraries-loaded', libraries: Library[]): void
// }

interface Props {
  id: string
  defaultEdit?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  defaultEdit: false
})

const store = useStore()
const isLoadingMoreTracks = ref(false)
const edit = ref(props.defaultEdit)
const playlist = ref<Playlist | null>(null)
const playlistTracks = ref<PlaylistTrack[]>([])
const showEmbedModal = ref(false)

type FullPlaylistTrack = Omit<PlaylistTrack, 'track'> & { track: Track }
const fullPlaylistTracks = ref<FullPlaylistTrack[]>([])

const tracks = computed(() => fullPlaylistTracks.value.map(({ track }, index) => ({ ...track as Track, position: index + 1 })))

const updateTrack = (updatedTrack: Track) => {
    fullPlaylistTracks.value = fullPlaylistTracks.value.map((item) =>
      item.track.id === updatedTrack.id ? { ...item, track: updatedTrack } : item
    );
};
useWebSocketHandler('playlist.track_updated', async (event) => {
    updateTrack(event.track);
});

const { t } = useI18n()
const labels = computed(() => ({
  playlist: t('views.playlists.Detail.title')
}))

const isLoading = ref(false)
const nextPage = ref<string | null>(null) // Tracks the next page URL
const previousPage = ref<string | null>(null) // Tracks the previous page URL
const totalTracks = ref<number>(0) // Total number of tracks

const fetchData = async () => {
  isLoading.value = true

  try {
    const [playlistResponse, tracksResponse] = await Promise.all([
      axios.get(`playlists/${props.id}/`),
      axios.get(`playlists/${props.id}/tracks?page=1`)
    ])

    playlist.value = playlistResponse.data
    fullPlaylistTracks.value = tracksResponse.data.results
    nextPage.value = tracksResponse.data.next
    previousPage.value = tracksResponse.data.previous
    totalTracks.value = tracksResponse.data.count
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

const loadMoreTracks = async () => {
  if (nextPage.value) {
    isLoadingMoreTracks.value = true; // Set loading state for the button
    try {
      const response = await axios.get(nextPage.value)

      // Append new tracks to the existing list
      fullPlaylistTracks.value = [...fullPlaylistTracks.value, ...response.data.results]
      // Update pagination metadata
      nextPage.value = response.data.next
    } catch (error) {
      useErrorHandler(error as Error)
    } finally {
      isLoadingMoreTracks.value = false; // Reset loading state
    }
  }
}

fetchData()

const images = computed(() => {
  const urls = playlist.value?.album_covers.slice(0, 4).map(url => store.getters['instance/absoluteUrl'](url)) || []

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

// TODO: Check if this ref is still needed
// const updatedTitle = computed(() => {
//   const date = momentFormat(new Date(playlist.value?.modification_date ?? '1970-01-01'))
//   return t('components.audio.ChannelCard.title', { date })
// })

// TODO: Implement shuffle
const shuffle = () => {}
</script>

<template>
  <Loader
    v-if="isLoading"
    v-title="labels.playlist"
  />
  <Header
    v-if="!isLoading && playlist"
    :h1="playlist.name"
    page-heading
  >
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
    <Layout
      gap-4
      class="meta"
    >
      <Layout
        flex
        gap-4
      >
        {{ playlist.tracks_count }}
        {{ t('views.playlists.Detail.header.tracks') }}
        <i class="bi bi-dot" />
        <Duration :seconds="playlist.duration" />
      </Layout>
      <Layout
        flex
        gap-4
      >
        {{ t('views.playlists.Detail.meta.attribution') }}
        {{ playlist.actor.full_username }}
        <i class="bi bi-dot" />
        {{ t('views.playlists.Detail.meta.updated') }}
        <HumanDate
          :date="playlist.modification_date"
        />
      </Layout>
    </Layout>
    <RenderedDescription
      :content="{ html: playlist.description }"
      :truncate-length="100"
    />
    <Layout
      flex
      class="header-buttons"
    >
      <PlayButton
        split
        low-height
        :is-playable="true"
        :tracks="tracks"
        :playlist="playlist"
      >
        {{ t('views.playlists.Detail.button.playAll') }}
      </PlayButton>
      <Button
        v-if="playlist.tracks_count > 1"
        primary
        icon="bi-shuffle"
        low-height
        :aria-label="t('components.audio.Player.label.shuffleQueue')"
        @click.prevent.stop="shuffle()"
      >
        {{ t('components.audio.Player.label.shuffleQueue') }}
      </Button>
      <Button
        v-if="store.state.auth.profile && playlist.actor.full_username === store.state.auth.fullUsername"
        secondary
        low-height
        icon="bi-pencil"
        @click="edit = !edit"
      >
        <template v-if="edit">
          {{ t('views.playlists.Detail.button.stopEdit') }}
        </template>
        <template v-else>
          {{ t('views.playlists.Detail.button.edit') }}
        </template>
      </Button>
      <Spacer
        h
        grow
      />
      <playlist-dropdown
        :playlist="playlist"
        @import="fetchData"
      />
    </Layout>
  </Header>

  <Layout stack>
    <template v-if="edit">
      <playlist-editor
        v-model:playlist="playlist"
        v-model:playlist-tracks="playlistTracks"
      />
    </template>
    <template v-else-if="tracks.length > 0">
      <track-table
        :show-position="true"
        :tracks="tracks"
        :unique="false"
      />
      <Button
        v-if="nextPage"
        primary
        :is-loading="isLoadingMoreTracks"
        @click="loadMoreTracks"
      >
        {{ t('views.playlists.Detail.button.loadMoreTracks') }}
      </Button>
    </template>
    <Alert
      v-else-if="!isLoading"
      blue
      align-items="center"
    >
      <Layout
        flex
        :gap="8"
      >
        <i class="bi bi-music-note-list" />
        {{ t('views.playlists.Detail.empty.noTracks') }}
      </Layout>
      <Spacer size-16 />
      <Button
        primary
        icon="bi-pencil"
        align-self="center"
        @click="edit = !edit"
      >
        {{ t('views.playlists.Detail.button.edit') }}
      </Button>
    </Alert>
  </Layout>

  <Modal
    v-if="playlist?.privacy_level === 'everyone' && playlist?.is_playable"
    v-model="showEmbedModal"
    title="t('views.playlists.Detail.modal.embed.header')"
  >
    <div class="scrolling content">
      <div class="description">
        <embed-wizard
          :uuid="playlist.uuid"
          type="playlist"
        />
      </div>
    </div>
    <template #actions>
      <Button variant="outline">
        {{ t('views.playlists.Detail.button.cancel') }}
      </Button>
    </template>
  </Modal>
</template>

<style lang="scss" scoped>

.playlist-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: 2px;
  width: 200px;
  height: 200px;
}

.playlist-grid img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.meta {
  font-size: 15px;
  @include light-theme {
    color: var(--fw-gray-700);
  }
  @include dark-theme {
    color: var(--fw-gray-500);
  }
}

.playlist-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 0 8px;
}
</style>
