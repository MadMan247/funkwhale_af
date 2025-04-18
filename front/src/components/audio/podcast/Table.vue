<script setup lang="ts">
import type { Track } from '~/types'

import PodcastRow from '~/components/audio/podcast/Row.vue'
import TrackMobileRow from '~/components/audio/track/MobileRow.vue'
import Pagination from '~/components/ui/Pagination.vue'

interface Props {
  tracks: Track[]
  showPosition?: boolean
  showArt?: boolean
  showDuration?: boolean
  displayActions?: boolean
  isArtist?: boolean
  isAlbum?: boolean
  isPodcast?: boolean
  paginateResults?: boolean
  paginateBy?: number
  total?: number
}

withDefaults(defineProps<Props>(), {
  showPosition: false,
  showArt: true,
  showDuration: true,
  displayActions: true,
  isArtist: false,
  isAlbum: false,
  isPodcast: true,
  paginateResults: true,
  paginateBy: 25,
  total: 0
})

const { page } = defineModels<{ page: number, }>()
</script>

<template>
  <div>
    <div class="ui hidden divider" />

    <!-- Add a header if needed -->

    <slot name="header" />

    <div>
      <div :class="['track-table', 'ui', 'unstackable', 'grid', 'tablet-and-up']">
        <!-- For each item, build a row -->
        <podcast-row
          v-for="(track, index) in tracks"
          :key="track.id"
          :track="track"
          :index="index"
          :tracks="tracks"
          :display-actions="displayActions"
          :show-duration="showDuration"
          :is-podcast="isPodcast"
        />
      </div>
      <div
        v-if="paginateResults"
        class="ui center aligned basic segment desktop-and-up"
      >
        <Pagination
          v-model:page="page"
          :pages="Math.ceil((total || 0)/paginateBy)"
        />
      </div>
    </div>

    <div :class="['track-table', 'ui', 'unstackable', 'grid', 'tablet-and-below']">
      <!-- For each item, build a row -->

      <track-mobile-row
        v-for="(track, index) in tracks"
        :key="track.id"
        :track="track"
        :index="index"
        :tracks="tracks"
        :show-position="showPosition"
        :show-art="showArt"
        :show-duration="showDuration"
        :is-artist="isArtist"
        :is-album="isAlbum"
        :is-podcast="isPodcast"
      />
      <div
        v-if="paginateResults"
        class="ui center aligned basic segment tablet-and-below"
      >
        <Pagination
          v-if="paginateResults"
          v-model:page="page"
          :pages="Math.ceil((total || 0)/paginateBy)"
        />
      </div>
    </div>
  </div>
</template>
