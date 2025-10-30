<script setup lang="ts">
import { usePlayer } from '~/composables/audio/player'
import { useQueue } from '~/composables/audio/queue'

import { useMouse, useWindowSize } from '@vueuse/core'
import { computed, ref } from 'vue'
import { useStore } from '~/store'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

import onKeyboardShortcut from '~/composables/onKeyboardShortcut'
import time from '~/utils/time'

import TrackFavoriteIcon from '~/components/favorites/TrackFavoriteIcon.vue'
import TrackPlaylistIcon from '~/components/playlists/TrackPlaylistIcon.vue'
import PlayerControls from './PlayerControls.vue'
import VolumeControl from './VolumeControl.vue'
import Layout from '~/components/ui/Layout.vue'
import Button from '~/components/ui/Button.vue'

const {
  LoopingMode,
  initializeFirstTrack,
  isPlaying,
  mute,
  volume,
  toggleLooping,
  looping,
  seekBy,
  seekTo,
  currentTime,
  duration,
  bufferProgress,
  loading: isLoadingAudio
} = usePlayer()

const {
  playPrevious,
  playNext,
  queue,
  currentIndex,
  currentTrack,
  isShuffled,
  shuffle,
  clear
} = useQueue()

const store = useStore()
const router = useRouter()
const { t } = useI18n()

/** Toggle between null and player */
const togglePlayer = () => {
  store.commit('ui/queueFocused',
    store.state.ui.queueFocused === 'queue'
      ? null
      : store.state.ui.queueFocused === 'player'
        ? null
        : 'player'
  )
}

const switchTab = () => {
  store.commit('ui/queueFocused', store.state.ui.queueFocused === 'player' ? 'queue' : 'player')
}

// Key binds
onKeyboardShortcut('e', togglePlayer)
onKeyboardShortcut('p', () => { isPlaying.value = !isPlaying.value })
onKeyboardShortcut('s', shuffle)
onKeyboardShortcut('q', clear)
onKeyboardShortcut('m', mute)
onKeyboardShortcut('l', toggleLooping)
onKeyboardShortcut('f', () => store.dispatch('favorites/toggle', currentTrack.value?.id))
onKeyboardShortcut('escape', () => store.commit('ui/queueFocused', null))

onKeyboardShortcut(['shift', 'up'], () => (volume.value += 0.1), true)
onKeyboardShortcut(['shift', 'down'], () => (volume.value -= 0.1), true)

onKeyboardShortcut('right', () => seekBy(5), true)
onKeyboardShortcut(['shift', 'right'], () => seekBy(30), true)
onKeyboardShortcut('left', () => seekBy(-5), true)
onKeyboardShortcut(['shift', 'left'], () => seekBy(-30), true)

onKeyboardShortcut(['ctrl', 'shift', 'left'], playPrevious, true)
onKeyboardShortcut(['ctrl', 'shift', 'right'], playNext, true)

const labels = computed(() => ({
  audioPlayer: t('components.audio.Player.label.audioPlayer'),
  previous: t('components.audio.Player.label.previousTrack'),
  play: t('components.audio.Player.label.play'),
  pause: t('components.audio.Player.label.pause'),
  next: t('components.audio.Player.label.nextTrack'),
  unmute: t('components.audio.Player.label.unmute'),
  mute: t('components.audio.Player.label.mute'),
  expandQueue: t('components.audio.Player.label.expandQueue'),
  shuffle: t('components.audio.Player.label.shuffleQueue'),
  clear: t('components.audio.Player.label.clearQueue'),
  addArtistContentFilter: t('components.audio.Player.label.addArtistContentFilter')
}))

const progressBar = ref()
const touchProgress = (event: MouseEvent) => {
  const time = ((event.clientX - ((event.target as Element).closest('.progress')?.getBoundingClientRect().left ?? 0)) / progressBar.value.offsetWidth) * duration.value
  seekTo(time)
}

const { x } = useMouse({ type: 'client' })
const { width: screenWidth } = useWindowSize({ includeScrollbar: false })

initializeFirstTrack()

const loopingTitle = computed(() => {
  const mode = looping.value
  return mode === LoopingMode.None
    ? t('components.audio.Player.label.loopingDisabled')
    : mode === LoopingMode.LoopTrack
      ? t('components.audio.Player.label.loopingSingle')
      : t('components.audio.Player.label.loopingWholeQueue')
})

// TODO: check if still useful for filtering
// const hideArtist = () => {
//   if (currentTrack.value.artistId !== -1 && currentTrack.value.artistCredit) {
//     return store.dispatch('moderation/hide', {
//       type: 'artist',
//       target: {
//         id: currentTrack.value.artistCredit[0].artist.id,
//         name: currentTrack.value.artistCredit[0].artist.name
//       }
//     })
//   }
// }
</script>

<template>
  <section
    v-if="currentTrack"
    role="complementary"
    class="player-wrapper ui bottom-player component-player"
    aria-labelledby="player-label"
  >
    <h1
      id="player-label"
      t="'components.audio.Player.header.player'"
      class="visually-hidden"
    />
    <div
      class="ui inverted segment fixed-controls"
      @click.prevent.stop="togglePlayer"
    >
      <div
        ref="progressBar"
        :class="['ui', 'top attached', 'small', 'inverted', {'indicating': isLoadingAudio}, 'progress']"
        @click.prevent.stop="touchProgress"
      >
        <div
          class="buffer bar"
          :style="{ 'transform': `translateX(${bufferProgress - 100}%)` }"
        />
        <div class="position bar" />
        <div
          class="seek bar"
          :style="{ 'transform': `translateX(${x / screenWidth * 100 - 100}%)` }"
        />
      </div>
      <div class="controls-row">
        <div class="controls track-controls queue-not-focused desktop-and-up">
          <div
            class="ui tiny image"
            @click.stop.prevent="router.push({name: 'library.tracks.detail', params: {id: currentTrack.id }})"
          >
            <!-- TODO: Use smaller covers -->
            <img
              ref="cover"
              v-lazy="store.getters['instance/absoluteUrl'](currentTrack.coverUrl)"
              alt=""
            >
          </div>
          <div
            class="middle aligned content ellipsis"
            @click.stop.prevent=""
          >
            <strong>
              <router-link
                class="header discrete link track"
                :to="{name: 'library.tracks.detail', params: {id: currentTrack.id }}"
                @click.stop.prevent=""
              >
                {{ currentTrack.title }}
              </router-link>
            </strong>
            <div class="meta">
              <span>
                <template
                  v-for="ac in currentTrack.artistCredit"
                  :key="ac.artist.id"
                >
                  <router-link
                    class="small discrete link"
                    :to="{name: 'library.artists.detail', params: {id: ac.artist.id }}"
                    @click.stop.prevent=""
                  >
                    {{ ac.credit ?? t('components.audio.Player.meta.unknownArtist') }}
                  </router-link>
                  <span>{{ ac.joinphrase }}</span>
                </template>
              </span>
              <template v-if="currentTrack.albumId !== -1">
                <span class="middle slash symbol" />
                <router-link
                  class="small discrete link"
                  :to="{name: 'library.albums.detail', params: {id: currentTrack.albumId }}"
                  @click.stop.prevent=""
                >
                  {{ currentTrack.albumTitle ?? t('components.audio.Player.meta.unknownAlbum') }}
                </router-link>
              </template>
            </div>
          </div>
        </div>
        <div class="controls track-controls queue-not-focused desktop-and-below">
          <div class="ui tiny image">
            <!-- TODO: Use smaller covers -->
            <img
              ref="cover"
              v-lazy="store.getters['instance/absoluteUrl'](currentTrack.coverUrl)"
              alt=""
            >
          </div>
          <div class="middle aligned content ellipsis">
            <strong>
              {{ currentTrack.title }}
            </strong>
            <Layout
              flex
              no-gap
              class="meta"
            >
              <div
                v-for="ac in currentTrack.artistCredit"
                :key="ac.artist.id"
              >
                {{ ac.credit ?? t('components.audio.Player.meta.unknownArtist') }}
                <span>{{ ac.joinphrase }}</span>
              </div>
              <template v-if="currentTrack.albumId !== -1">
                <span class="middle slash symbol" />
                {{ currentTrack.albumTitle ?? t('components.audio.Player.meta.unknownAlbum') }}
              </template>
            </Layout>
          </div>
        </div>
        <div
          v-if="store.state.auth.authenticated"
          class="controls desktop-and-up fluid align-right"
        >
          <track-favorite-icon
            ghost
            :track="currentTrack"
          />
          <track-playlist-icon
            ghost
            :track="currentTrack"
          />
          <!-- <Button
            round
            ghost
            icon="bi-eye-slash"
            :aria-label="labels.addArtistContentFilter"
            :title="labels.addArtistContentFilter"
            @click="hideArtist"
          >
          </Button> -->
        </div>
        <player-controls class="controls queue-not-focused" />
        <div class="controls progress-controls queue-not-focused tablet-and-up small align-left">
          <div class="timer">
            <template v-if="!isLoadingAudio">
              <span
                class="start"
                @click.stop.prevent="seekTo(0)"
              >
                {{ time.parse(Math.round(currentTime)) }}
              </span>
              <span class="middle pipe symbol" />
              <span class="total">{{ time.parse(Math.round(duration)) }}</span>
            </template>
          </div>
        </div>
        <div class="controls queue-controls when-queue-focused align-right">
          <div class="group">
            <volume-control class="expandable" />
            <Button
              :class="{ looping: looping !== LoopingMode.None }"
              :title="loopingTitle"
              ghost
              round
              :aria-label="loopingTitle"
              :disabled="!currentTrack"
              :icon="looping === LoopingMode.LoopTrack ? 'bi-repeat-1' : 'bi-repeat'"
              @click.prevent.stop="toggleLooping"
            />

            <Button
              round
              ghost
              :class="{ shuffling: isShuffled }"
              :disabled="queue.length === 0"
              :title="labels.shuffle"
              :aria-label="labels.shuffle"
              icon="bi-shuffle"
              @click.prevent.stop="shuffle()"
            />
          </div>

          <!-- TODO: Remove fake responsive elements -->
          <div class="group">
            <div class="fake-dropdown">
              <Button
                aria-expanded="true"
                ghost
                round
                icon="bi-music-note-list"
                @click.stop="togglePlayer"
              >
                <i18n-t keypath="components.audio.Player.meta.position">
                  <template #index>
                    {{ currentIndex + 1 }}
                  </template>
                  <template #length>
                    {{ queue.length }}
                  </template>
                </i18n-t>
              </Button>
              <Button
                class="position circular control button desktop-and-below"
                icon="bi-music-note-list"
              >
                <i18n-t keypath="components.audio.Player.meta.position">
                  <template #index>
                    {{ currentIndex + 1 }}
                  </template>
                  <template #length>
                    {{ queue.length }}
                  </template>
                </i18n-t>
              </Button>

              <Button
                ghost
                :class="['desktop-and-up', { 'close-control': store.state.ui.queueFocused }]"
                :icon="store.state.ui.queueFocused ? 'bi-chevron-down' : 'bi-chevron-up'"
                :aria-pressed="store.state.ui.queueFocused ? true : undefined"
                @click.stop="togglePlayer"
              />
              <Button
                ghost
                :class="['desktop-and-below', { 'close-control': store.state.ui.queueFocused === 'player' }]"
                :icon="store.state.ui.queueFocused === 'queue' ? 'bi-chevron-down' : 'bi-chevron-up'"
                :aria-pressed="store.state.ui.queueFocused ? true : undefined"
                @click.stop="switchTab"
              />
            </div>
            <Button
              class="close-control desktop-and-below"
              icon="bi-x"
              @click.stop="store.commit('ui/queueFocused', null)"
            />
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style lang="scss" scoped>

</style>
