<script setup lang="ts">
import type { Track } from '~/types'

import { useI18n } from 'vue-i18n'
import { clone, uniqBy } from 'lodash-es'
import { ref, computed } from 'vue'

import axios from 'axios'

import TrackMobileRow from '~/components/audio/track/MobileRow.vue'
import Pagination from '~/components/ui/Pagination.vue'
import TrackRow from '~/components/audio/track/Row.vue'
import Input from '~/components/ui/Input.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Loader from '~/components/ui/Loader.vue'
import Table from '~/components/ui/Table.vue'

import useErrorHandler from '~/composables/useErrorHandler'

interface Events {
  (e: 'fetched'): void
  (e: 'page-changed', page: number): void
}

interface Props {
  tracks?: undefined | Track[]

  showAlbum?: boolean
  showArtist?: boolean
  showPosition?: boolean
  showArt?: boolean
  showDuration?: boolean
  search?: boolean
  displayActions?: boolean
  isArtist?: boolean
  isAlbum?: boolean
  isPodcast?: boolean

  filters?: object

  nextUrl?: string | null

  paginateResults?: boolean
  total?: number
  page?: number
  paginateBy?: number,

  unique?: boolean
}

const emit = defineEmits<Events>()
const props = withDefaults(defineProps<Props>(), {
  tracks: undefined,

  showAlbum: true,
  showArtist: true,
  showPosition: false,
  showArt: true,
  showDuration: true,
  search: false,
  displayActions: true,
  isArtist: false,
  isAlbum: false,
  isPodcast: false,

  filters: () => ({}),
  nextUrl: null,

  paginateResults: false,
  total: 0,
  page: 1,
  paginateBy: 25,

  unique: true
})

const currentPage = ref(props.page)
const totalTracks = ref(props.total)
const fetchDataUrl = ref(props.nextUrl)
const additionalTracks = ref([] as Track[])
const query = ref('')

const allTracks = computed(() => {
  const tracks = [...(props.tracks ?? []), ...additionalTracks.value]
  return props.unique
    ? uniqBy(tracks, 'id')
    : tracks
})

const paginateResults = computed(() => props.paginateResults && allTracks.value.length < props.paginateBy)

const { t } = useI18n()

const labels = computed(() => ({
  title: t('components.audio.track.Table.table.header.title'),
  album: t('components.audio.track.Table.table.header.album'),
  artist: t('components.audio.track.Table.table.header.artist'),
  searchPlaceholder: t('views.Search.header.search')
}))

const isLoading = ref(false)
const fetchData = async () => {
  isLoading.value = true

  const params = {
    ...clone(props.filters),
    page_size: props.paginateBy,
    page: currentPage.value,
    include_channels: true,
    q: query.value
  }

  try {
    const response = await axios.get('tracks/', { params })

    // TODO (wvffle): Fetch continuously?
    fetchDataUrl.value = response.data.next
    additionalTracks.value = response.data.results
    totalTracks.value = response.data.count
    emit('fetched')
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

const performSearch = () => {
  currentPage.value = 1
  additionalTracks.value = []
  fetchData()
}

if (props.tracks === undefined) {
  fetchData()
}

const updatePage = (page: number) => {
  if (props.tracks === undefined) {
    currentPage.value = page
    fetchData()
  } else {
    emit('page-changed', page)
  }
}
</script>

<template>
  <div>
    <!-- Show the search bar if search is true -->

    <Input
      v-if="search"
      v-model="query"
      search
      autofocus
      :placeholder="labels.searchPlaceholder"
      @search="performSearch"
    />
    <Spacer v-if="search" />

    <!-- Add a header if needed -->

    <slot name="header" />

    <!-- Show a message if no tracks are available -->

    <slot
      v-if="!isLoading && allTracks.length === 0"
      name="empty-state"
    >
      <empty-state
        :refresh="true"
        @refresh="fetchData()"
      />
    </slot>

    <!-- Table on screens > 768px wide -->
    <!-- TODO: Make responsive to parent container instead of screen -->

    <div
      v-else
      :class="['track-table', 'ui', 'unstackable', 'grid', 'tablet-and-up']"
    >
      <Loader v-if="isLoading" />

      <Table
        :grid-template-columns="['48px', '56px', 'auto', 'auto', 'auto', '56px', '64px', '48px']"
        :header-props="{ 'table-header': true }"
      >
        <template #header>
          <label />
          <label />
          <label>
            <span>{{ labels.title }}</span>
          </label>
          <label>
            <span v-if="showAlbum">{{ labels.album }}</span>
          </label>
          <label>
            <span v-if="showArtist">{{ labels.artist }}</span>
          </label>
          <label />
          <label>
            <i
              v-if="showDuration"
              class="bi bi-clock"
            />
          </label>
          <label />
        </template>

        <track-row
          v-for="(track, index) in allTracks"
          :key="`${track.id} ${track.position}`"
          :track="track"
          :index="index"
          :tracks="allTracks"
          :show-album="showAlbum"
          :show-artist="showArtist"
          :show-position="showPosition"
          :show-art="showArt"
          :display-actions="displayActions"
          :show-duration="showDuration"
          :is-podcast="isPodcast"
        />
      </Table>

      <!-- Pagination -->

      <Pagination
        v-if="paginateResults"
        :pages="paginateBy"
        :page="page"
        @update:current="updatePage"
      />
    </div>

    <!-- Under 768px screen width -->
    <!-- TODO: Make responsive to parent container instead of screen -->

    <div
      :class="['track-table', 'ui', 'unstackable', 'grid', 'tablet-and-below']"
    >
      <Loader v-if="isLoading" />

      <!-- For each item, build a row -->

      <track-mobile-row
        v-for="(track, index) in allTracks"
        :key="track.id"
        :track="track"
        :index="index"
        :tracks="allTracks"
        :show-position="showPosition"
        :show-art="showArt"
        :show-duration="showDuration"
        :is-artist="isArtist"
        :is-album="isAlbum"
        :is-podcast="isPodcast"
      />
      <Pagination
        v-if="paginateResults"
        :pages="paginateBy"
        :page="page"
        @update:current="updatePage"
      />
    </div>
  </div>
</template>

<style scoped>
  [table-header] > label {
    padding-left: 4px;
    align-self: center !important;
  }
</style>
