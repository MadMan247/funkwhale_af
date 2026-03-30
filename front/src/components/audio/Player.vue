<script setup lang="ts">
import { usePlayer } from '~/composables/audio/player'
import { useQueue } from '~/composables/audio/queue'

import { computed, ref, onUnmounted } from 'vue'
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

const progressBar = ref<HTMLElement | null>(null)
const seekPosition = ref(0)
const isDragging = ref(false)

/** * Central logic for calculating seek percentage.
 * Works for both Mouse and Touch events.
 */
const touchProgress = (event: MouseEvent | TouchEvent) => {
  if (!event || !progressBar.value) return

  let clientX: number
  if ('targetTouches' in event) {
    const touch = event.targetTouches[0] || event.changedTouches?.[0]
    if (!touch) return
    clientX = touch.clientX
  } else {
    clientX = (event as MouseEvent).clientX
  }

  const rect = progressBar.value.getBoundingClientRect()
  const percentage = Math.max(0, Math.min((clientX - rect.left) / rect.width, 1))

  seekPosition.value = percentage * 100
  seekTo(percentage * (duration.value || 0))
}

// --- Desktop Mouse Handlers ---

const onMouseDown = (event: MouseEvent) => {
  event.stopPropagation() // Prevent immediate togglePlayer
  isDragging.value = true

  touchProgress(event)

  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp)
}

const onMouseMove = (event: MouseEvent) => {
  if (isDragging.value) {
    touchProgress(event)
  }
}

const onMouseUp = () => {
  isDragging.value = false
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseup', onMouseUp)
}

// --- Mobile Touch Handlers ---

const onTouchStart = (event: TouchEvent) => {
  event.stopPropagation()
  isDragging.value = true
  touchProgress(event)
}

const onTouchMove = (event: TouchEvent) => {
  if (event.cancelable) event.preventDefault()
  event.stopPropagation()
  touchProgress(event)
}

const onTouchEnd = (event: TouchEvent) => {
  // Final update to set the seek position at the exact release point
  touchProgress(event)
  isDragging.value = false
}

onUnmounted(() => {
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseup', onMouseUp)
})

initializeFirstTrack()

const loopingTitle = computed(() => {
  const mode = looping.value
  return mode === LoopingMode.None
    ? t('components.audio.Player.label.loopingDisabled')
    : mode === LoopingMode.LoopTrack
      ? t('components.audio.Player.label.loopingSingle')
      : t('components.audio.Player.label.loopingWholeQueue')
})

const hideArtist = () => {
  if (currentTrack.value && currentTrack.value.artistId !== -1 && currentTrack.value.artistCredit) {
    return store.dispatch('moderation/hide', {
      type: 'artist',
      target: {
        id: currentTrack.value.artistCredit[0]?.artist.id,
        name: currentTrack.value.artistCredit[0]?.artist.name
      }
    })
  }
}
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
      class="visually-hidden"
    >
      {{ t('components.audio.Player.header.player') }}
    </h1>
    <div
      class="ui inverted segment fixed-controls"
      @click.prevent.stop="togglePlayer"
    >
      <div
        ref="progressBar"
        :class="['ui', 'top attached', 'small', 'inverted', {'indicating': isLoadingAudio}, 'progress']"
        :style="{
          '--fw-track-progress': isDragging
            ? `${seekPosition}%`
            : `${(currentTime / (duration || 1)) * 100}%`
        }"
        @mousedown="onMouseDown"
        @touchstart.passive="onTouchStart"
        @touchmove.prevent="onTouchMove"
        @touchend.prevent="onTouchEnd"
        @click.stop
      >
        <div
          class="buffer bar"
          :style="{ 'transform': `translate3d(${bufferProgress - 100}%, 0, 0)` }"
        />
        <div
          class="position bar"
        />
        <div
          class="seek bar"
          :style="{ 'transform': `translate3d(${seekPosition - 100}%, 0, 0)` }"
        />
      </div>

      <Teleport to="body">
        <div
          v-if="isDragging"
          style="position: fixed; inset: 0; z-index: 99999; cursor: grabbing;"
          @mousemove="onMouseMove"
          @mouseup="onMouseUp"
        />
      </Teleport>
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
        <div
          v-if="store.state.ui.queueFocused !== 'player' && store.state.ui.queueFocused !== 'queue'"
          class="controls track-controls queue-not-focused desktop-and-below"
        >
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
          <Button
            round
            ghost
            icon="bi-eye-slash"
            :aria-label="labels.addArtistContentFilter"
            :title="labels.addArtistContentFilter"
            @click="hideArtist"
          />
        </div>

        <div
          v-if="store.state.ui.queueFocused"
          class="controls desktop-and-below"
        >
          <Button
            :class="{ looping: looping !== LoopingMode.None }"
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
            :aria-label="labels.shuffle"
            icon="bi-shuffle"
            @click.prevent.stop="shuffle()"
          />
        </div>

        <player-controls class="controls" />

        <div
          v-if="store.state.ui.queueFocused === 'player' || store.state.ui.queueFocused === 'queue'"
          class="controls desktop-and-below queue-not-focused"
        >
          <Button
            icon="bi-music-note-list"
            ghost
            tiny
            :class="['desktop-and-below', { 'close-control': store.state.ui.queueFocused === 'queue' }]"
            :is-active="store.state.ui.queueFocused === 'queue'"
            @click.stop="switchTab"
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
            v-if="store.state.ui.queueFocused === 'player' || store.state.ui.queueFocused === 'queue'"
            ghost
            class="close-control"
            icon="bi bi-chevron-down"
            @click.stop="store.commit('ui/queueFocused', null)"
          />
        </div>

        <div class="controls progress-controls queue-not-focused tablet-and-up small align-right">
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
                icon="bi-music-note-list"
                class="desktop-and-up"
                :aria-label="labels.expandQueue"
                :is-active="store.state.ui.queueFocused === 'player'"
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
                icon="bi-music-note-list"
                ghost
                tiny
                :class="['desktop-and-below', { 'close-control': store.state.ui.queueFocused }]"
                :is-active="store.state.ui.queueFocused === 'queue'"
                @click.stop="switchTab"
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
                v-if="store.state.ui.queueFocused === 'player' || store.state.ui.queueFocused === 'queue'"
                ghost
                class="close-control"
                icon="bi bi-chevron-down"
                @click.stop="store.commit('ui/queueFocused', null)"
              />
              <Button
                v-else
                ghost
                class="desktop-and-up"
                icon="bi bi-chevron-up"
                @click.stop="togglePlayer"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style lang="scss" scoped>
.ui.progress {
  position: relative;
  cursor: pointer;
  overflow: visible !important; /* Ensure the hit area isn't clipped */
}

/* Create a generous 24px invisible hit area for lumpy fingers on small mobile screens */
.ui.progress::after {
  content: '';
  position: absolute;
  top: -5px;    /* Slight overlap above */
  bottom: -15px; /* Large area below for easier thumb access */
  left: 0;
  right: 0;
  z-index: 20;
}

.progress-area {
  cursor: pointer;
  // Ensure the container is easy to hit
  padding: 10px 0;
}

.fake-dropdown {
  border: 1px solid gray;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-width: 8em;
  z-index: 2;
  > .control.button {
    padding: 0.5em;

  }
  .position.control {
    flex-grow: 1;
  }
  .angle.icon {
    margin-right: 0;
  }
}
</style>
