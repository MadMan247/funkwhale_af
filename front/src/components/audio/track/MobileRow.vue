<script setup lang="ts">
import type { Track, Artist, Album, Playlist, Library, Channel, Actor } from '~/types'
import type { PlayOptionsProps } from '~/composables/audio/usePlayOptions'

import { usePlayer } from '~/composables/audio/player'
import { useQueue } from '~/composables/audio/queue'
import { useStore } from '~/store'
import { generateTrackCreditString } from '~/utils/utils'
import { useFallbackImage } from '~/composables/useFallbackImage'

import usePlayOptions from '~/composables/audio/usePlayOptions'

import TrackFavoriteIcon from '~/components/favorites/TrackFavoriteIcon.vue'

import PlayButton from '~/components/audio/PlayButton.vue'

interface Props extends PlayOptionsProps {
  track: Track
  index: number

  showArt?: boolean
  isArtist?: boolean
  isAlbum?: boolean

  // TODO(wvffle): Remove after https://github.com/vuejs/core/pull/4512 is merged
  isPlayable?: boolean
  artist?: Artist | null
  album?: Album | null
  playlist?: Playlist | null
  library?: Library | null
  channel?: Channel | null
  account?: Actor | null
}

const props = withDefaults(defineProps<Props>(), {
  showArt: true,
  isArtist: false,
  isAlbum: false,

  artist: null,
  album: null,
  playlist: null,
  library: null,
  channel: null,
  account: null
})

const { currentTrack } = useQueue()
const { isPlaying } = usePlayer()
const { activateTrack } = usePlayOptions(props)

const store = useStore()

const { onCoverError } = useFallbackImage()
</script>

<template>
  <div
    :class="[
      { active: currentTrack && track.id === currentTrack.id },
      'track-row row mobile',
    ]"
  >
    <div
      v-if="showArt"
      class="image left floated column"
      @click.prevent.exact="activateTrack(track, index)"
    >
      <img
        v-if="track.cover"
        v-lazy="store.getters['instance/absoluteUrl'](track.cover.urls.small_square_crop)"
        :alt="track.title"
        class="ui artist-track mini image"
        @error="(e) => onCoverError(e, track)"
      >
      <img
        v-else-if="track.album?.cover?.urls.original"
        v-lazy="store.getters['instance/absoluteUrl'](track.album.cover.urls.small_square_crop)"
        :alt="track.title"
        class="ui artist-track mini image"
        @error="(e) => onCoverError(e, track.album)"
      >
      <img
        v-else
        :alt="track.title"
        class="ui artist-track mini image"
        src="../../../assets/audio/default-cover.png"
      >
    </div>
    <div
      tabindex="0"
      role="button"
      class="content ellipsis left floated column"
      @click="activateTrack(track, index)"
    >
      <p
        :class="[
          'track-title',
          'mobile',
          { 'play-indicator': isPlaying && track.id === currentTrack?.id },
        ]"
      >
        {{ track.title }}
      </p>
      <p class="track-meta mobile">
        {{ generateTrackCreditString(track) }}
        <span class="middle middledot symbol" />
        <human-duration
          v-if="track.uploads?.[0]?.duration"
          :duration="track.uploads[0]?.duration"
        />
      </p>
    </div>
    <track-favorite-icon
      v-if="store.state.auth.authenticated"
      tiny
      :class="[
        'meta',
        'right',
        'floated',
        'column',
        'mobile',
        { 'with-art': showArt },
      ]"
      :track="track"
    />
    <!-- TODO: Replace with <PlayButton :dropdown-only="true"> after its display is fixed for mobile -->
    <play-button
      :dropdown-only="true"
      :is-playable="track.is_playable"
      :track="track"
    />
  </div>
</template>
