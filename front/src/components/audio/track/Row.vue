<script setup lang="ts">
import type { Track, ArtistCredit, Album, Playlist, Library, Channel, Actor } from '~/types'
import type { PlayOptionsProps } from '~/composables/audio/usePlayOptions'

import { computed, ref } from 'vue'

import usePlayOptions from '~/composables/audio/usePlayOptions'

import { usePlayer } from '~/composables/audio/player'
import { useQueue } from '~/composables/audio/queue'
import { useStore } from '~/store'
import TrackFavoriteIcon from '~/components/favorites/TrackFavoriteIcon.vue'
import PlayIndicator from '~/components/audio/track/PlayIndicator.vue'
import PlayButton from '~/components/audio/PlayButton.vue'

import Button from '~/components/ui/Button.vue'

const store = useStore()

interface Props extends PlayOptionsProps {
  track: Track
  index: number

  showAlbum?: boolean
  showArt?: boolean
  showArtist?: boolean
  showDuration?: boolean
  showPosition?: boolean
  displayActions?: boolean

  // TODO(wvffle): Remove after https://github.com/vuejs/core/pull/4512 is merged
  tracks: Track[]
  isPlayable?: boolean
  artistCredit?: ArtistCredit[] | null
  album?: Album | null
  playlist?: Playlist | null
  library?: Library | null
  channel?: Channel | null
  account?: Actor | null
}

const props = withDefaults(defineProps<Props>(), {
  showAlbum: true,
  showArt: true,
  showArtist: true,
  showDuration: true,
  showPosition: false,
  displayActions: true,

  artistCredit: null,
  album: null,
  playlist: null,
  library: null,
  channel: null,
  account: null
})

const { activateTrack } = usePlayOptions(props)
const { isPlaying, loading } = usePlayer()
const { currentTrack } = useQueue()

const active = computed(() => props.track.id === currentTrack.value?.id && props.track.position === currentTrack.value?.position)
const hover = ref(false)
</script>

<template>
  <div
    :class="[{ active }, 'track-row row', $style.row]"
    style="display: contents;"
    @dblclick="activateTrack(track, index)"
    @mousemove="hover = true"
    @mouseout="hover = false"
  >
    <!-- 1. column: Play button or track position -->

    <div
      class="actions one wide left floated column"
      role="button"
      @click.prevent.exact="activateTrack(track, index)"
    >
      <play-indicator
        v-if="
          !loading &&
            isPlaying &&
            active &&
            !hover
        "
      />
      <Button
        v-else-if="
          !isPlaying &&
            active &&
            !hover
        "
        ghost
        icon="bi-play-fill"
      />
      <Button
        v-else-if="
          isPlaying &&
            active &&
            hover
        "
        ghost
        icon="bi-pause-fill"
      />
      <Button
        v-else-if="hover"
        ghost
        icon="bi-play-fill"
      />
      <span
        v-else-if="showPosition"
        class="track-position"
      >
        {{ `${track.position}`.padStart(2, '0') }}
      </span>
    </div>

    <div
      class="image left floated column"
      role="button"
      @click.prevent.exact="activateTrack(track, index)"
    >
      <img
        v-if="showArt && track.cover?.urls.original"
        v-lazy="store.getters['instance/absoluteUrl'](track.cover.urls.small_square_crop)"
        :alt="track.title"
        class="track_image"
        @error="(e) => { e.target && track.cover ? (e.target as HTMLImageElement).src = store.getters['instance/absoluteUrl'](track.cover.urls.medium_square_crop) : null }"
      >
      <img
        v-else-if="showArt && track.album?.cover?.urls.original"
        v-lazy="store.getters['instance/absoluteUrl'](track.album.cover.urls.small_square_crop)"
        alt=""
        class="track_image"
        @error="(e) => { e.target && track.album.cover ? (e.target as HTMLImageElement).src = store.getters['instance/absoluteUrl'](track.album.cover.urls.medium_square_crop) : null }"
      >
      <img
        v-else-if="showArt"
        alt=""
        class="track_image"
        src="../../../assets/audio/default-cover.png"
      >
    </div>

    <div
      tabindex="0"
      class="content ellipsis column left floated column"
    >
      <a
        @click="activateTrack(track, index)"
      >
        {{ track.title }}
      </a>
    </div>

    <div
      class="content ellipsis left floated column"
    >
      <router-link
        v-if="showAlbum"
        :to="{ name: 'library.albums.detail', params: { id: track.album?.id } }"
      >
        {{ track.album?.title }}
      </router-link>
    </div>

    <div
      class="content ellipsis left floated column"
    >
      <template
        v-for="ac in (showArtist ? track.artist_credit : [])"
        :key="ac.artist.id"
      >
        <router-link
          class="artist link"
          :to="{
            name: 'library.artists.detail',
            params: { id: ac.artist?.id },
          }"
        >
          {{ ac.credit }}
        </router-link>
        <span>{{ ac.joinphrase }}</span>
      </template>
    </div>

    <div
      class="meta right floated column"
    >
      <track-favorite-icon
        v-if="store.state.auth.authenticated"
        ghost
        :track="track"
      />
    </div>

    <div
      class="meta right floated column"
    >
      <human-duration
        v-if="showDuration && track.uploads && track.uploads.length > 0 && track.uploads[0].duration"
        :duration="track.uploads[0].duration"
      />
    </div>

    <div
      v-if="displayActions"
      class="meta right floated column"
    >
      <PlayButton
        :dropdown-only="true"
        :is-playable="track.is_playable"
        :track="track"
        class="ui floating dropdown"
        ghost
      />
    </div>
  </div>
</template>

<style module>
  .row > :has(> :is(a, span)) {
    line-height: 46px;
  }
  .row > div {
    /* total height 64px, according to designs on penpot */
    margin-bottom: 8px;
    margin-right: 8px;
    height: 48px;
  }
</style>
