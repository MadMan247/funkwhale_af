<script setup lang="ts">
import type { Track, Artist, Album, Playlist, Library, Channel, Actor } from '~/types'
import type { PlayOptionsProps } from '~/composables/audio/usePlayOptions'
import usePlayOptions from '~/composables/audio/usePlayOptions'
import useReport from '~/composables/moderation/useReport'

import { useStore } from '~/store'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { computed } from 'vue'
import { useVModel } from '@vueuse/core'
import { generateTrackCreditString, getArtistCoverUrl } from '~/utils/utils'

import Modal from '~/components/ui/Modal.vue'
import Button from '~/components/ui/Button.vue'
import Layout from '~/components/ui/Layout.vue'

interface Events {
  (e: 'update:show', value: boolean): void
}

interface Props extends PlayOptionsProps {
  track: Track
  index: number
  show: boolean

  isArtist?: boolean
  isAlbum?: boolean

  // TODO(wvffle): Remove after https://github.com/vuejs/core/pull/4512 is merged
  isPlayable?: boolean
  tracks?: Track[]
  artist?: Artist | null
  album?: Album | null
  playlist?: Playlist | null
  library?: Library | null
  channel?: Channel | null
  account?: Actor | null
}

const emit = defineEmits<Events>()
const props = withDefaults(defineProps<Props>(), {
  isArtist: false,
  isAlbum: false,

  tracks: () => [],
  artist: null,
  album: null,
  playlist: null,
  library: null,
  channel: null,
  account: null
})


const show = useVModel(props, 'show', emit)

const { report, getReportableObjects } = useReport()
const { enqueue, enqueueNext } = usePlayOptions(props)
const store = useStore()

const isFavorite = computed(() => store.getters['favorites/isFavorite'](props.track.id))

const { t } = useI18n()
const router = useRouter()

const favoriteButton = computed(() => isFavorite.value
  ? t('components.audio.track.Modal.button.removeFromFavorites')
  : t('components.audio.track.Modal.button.addToFavorites')
)

const trackDetailsButton = computed(() => props.track.artist_credit?.[0].artist.content_category === 'podcast'
  ? t('components.audio.track.Modal.button.episodeDetails')
  : t('components.audio.track.Modal.button.trackDetails')
)

const albumDetailsButton = computed(() => props.track.artist_credit?.[0].artist?.content_category === 'podcast'
  ? t('components.audio.track.Modal.button.seriesDetails')
  : t('components.audio.track.Modal.button.albumDetails')
)

const artistDetailsButton = computed(() => props.track.artist_credit?.[0].artist?.content_category === 'podcast'
  ? t('components.audio.track.Modal.button.channelDetails')
  : t('components.audio.track.Modal.button.artistDetails')
)

const labels = computed(() => ({
  startRadio: t('components.audio.track.Modal.button.startRadio'),
  playNow: t('components.audio.track.Modal.button.playNow'),
  addToQueue: t('components.audio.track.Modal.button.addToQueue'),
  playNext: t('components.audio.track.Modal.button.playNext'),
  addToPlaylist: t('components.audio.track.Modal.button.addToPlaylist')
}))
</script>

<template>
  <!-- TODO: Delete this file after this modal is replaced with playbutton dropdown-only popover -->
  <Modal
    v-model="show"
    :title="track.title"
    class="small"
  >
    <div class="header">
      <div class="ui large centered rounded image">
        <img
          v-if="track.album?.cover?.urls.original"
          v-lazy="store.getters['instance/absoluteUrl'](track.album.cover.urls.medium_square_crop)"
          alt=""
          class="ui centered image"
        >
        <img
          v-else-if="track.cover"
          v-lazy="store.getters['instance/absoluteUrl'](track.cover.urls.medium_square_crop)"
          alt=""
          class="ui centered image"
        >
        <img
          v-else-if="!!track.artist_credit.length && track.artist_credit[0].artist.cover"
          v-lazy="getArtistCoverUrl(track.artist_credit)"
          alt=""
          class="ui centered image"
        >
        <img
          v-else
          alt=""
          class="ui centered image"
          src="../../../assets/audio/default-cover.png"
        >
      </div>
      <h4 class="track-modal-subtitle">
        {{ generateTrackCreditString(track) }}
      </h4>
    </div>
    <div class="content">
      <Layout
        stack
        no-gap
      >
        <Button
          v-if="store.state.auth.authenticated && track.artist_credit?.[0].artist.content_category !== 'podcast'"
          full
          ghost
          :aria-label="favoriteButton"
          :icon="isFavorite ? 'bi-heart-fill' : 'bi-heart'"
          :is-active="isFavorite"
          @click.stop="store.dispatch('favorites/toggle', track.id)"
        >
          {{ favoriteButton }}
        </Button>
        <Button
          full
          ghost
          :aria-label="labels.addToQueue"
          icon="bi-plus"
          @click.stop.prevent="enqueue(); show = false"
        >
          {{ labels.addToQueue }}
        </Button>
        <Button
          full
          ghost
          :aria-label="labels.playNext"
          icon="bi-skip-end"
          @click.stop.prevent="enqueueNext(true); show = false"
        >
          {{ labels.playNext }}
        </Button>
        <Button
          full
          ghost
          :aria-label="labels.startRadio"
          icon="bi-rss"
          @click.stop.prevent="store.dispatch('radios/start', { type: 'similar', objectId: track.id }); show = false"
        >
          {{ labels.startRadio }}
        </Button>
        <Button
          full
          ghost
          :aria-label="labels.addToPlaylist"
          icon="bi-list"
          @click.stop="store.commit('playlists/chooseTrack', track)"
        >
          {{ labels.addToPlaylist }}
        </Button>
        <hr>
        <Button
          v-if="!isAlbum && track.album"
          full
          ghost
          :aria-label="albumDetailsButton"
          icon="bi-disc"
          @click.prevent.exact="router.push({ name: 'library.albums.detail', params: { id: track.album?.id } })"
        >
          {{ albumDetailsButton }}
        </Button>
        <template
          v-if="!isArtist"
        >
          <Button
            v-for="ac in track.artist_credit"
            :key="ac.artist.id"
            full
            ghost
            :aria-label="artistDetailsButton"
            icon="bi-person-fill"
            @click.prevent.exact="router.push({ name: 'library.artists.detail', params: { id: ac.artist.id } })"
          >
            {{ ac.credit }}<span v-if="ac.joinphrase">{{ ac.joinphrase }}</span>
          </Button>
        </template>
        <Button
          full
          ghost
          :aria-label="trackDetailsButton"
          icon="bi-info-circle"
          @click.prevent.exact="router.push({ name: 'library.tracks.detail', params: { id: track.id } })"
        >
          {{ trackDetailsButton }}
        </Button>
        <hr>
        <Button
          v-for="obj in getReportableObjects({ track, album: track.album, artistCredit: track.artist_credit })"
          :key="obj.target.type + obj.target.id"
          full
          ghost
          icon="bi-share"
          @click.stop.prevent="report(obj)"
        >
          {{ obj.label }}
        </Button>
      </Layout>
    </div>
  </Modal>
</template>
