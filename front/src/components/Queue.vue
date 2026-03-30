<script setup lang="ts">
import type { QueueItemSource } from '~/types'

import { isWebAudioRequested, getAudioContext } from '~/composables/audio/audio-api'
import { whenever, watchDebounced, useCurrentElement, useScrollLock, useFullscreen, useIdle, refAutoReset, useStorage } from '@vueuse/core'
import { nextTick, ref, computed, watchEffect, defineAsyncComponent, onUnmounted } from 'vue'
import { useFocusTrap } from '@vueuse/integrations/useFocusTrap'
import { useRouter } from 'vue-router'
import { useStore } from '~/store'

import { usePlayer } from '~/composables/audio/player'
import { useTracks } from '~/composables/audio/tracks'
import { useQueue } from '~/composables/audio/queue'
import useErrorHandler from '~/composables/useErrorHandler'
import { resetHandlers, refreshMetadata } from '~/init/mediaSession'

import time from '~/utils/time'

import { useI18n } from 'vue-i18n'

import TrackFavoriteIcon from '~/components/favorites/TrackFavoriteIcon.vue'
import TrackPlaylistIcon from '~/components/playlists/TrackPlaylistIcon.vue'

import VirtualList from '~/components/vui/list/VirtualList.vue'
import QueueItem from '~/components/QueueItem.vue'

import Layout from '~/components/ui/Layout.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Link from '~/components/ui/Link.vue'
import Button from '~/components/ui/Button.vue'
import ArtistCreditLabel from '~/components/audio/ArtistCreditLabel.vue'

const MilkDrop = defineAsyncComponent(() => import('~/components/audio/visualizer/MilkDrop.vue'))

const {
  isPlaying,
  currentTime,
  duration,
  bufferProgress,
  seekTo,
  loading: isLoadingAudio,
  errored
} = usePlayer()

const {
  hasNext,
  currentTrack,
  currentIndex,
  queue,
  dequeue,
  playTrack,
  reorder,
  endsIn,
  clear
} = useQueue()

const { currentSound } = useTracks()

const queueModal = ref()
const { activate, deactivate } = useFocusTrap(queueModal, { allowOutsideClick: true, preventScroll: true })

const { t } = useI18n()
const scrollLock = useScrollLock(document.body)
const store = useStore()

const labels = computed(() => ({
  queue: t('components.Queue.label.queue'),
  populating: t('components.Queue.label.populatingRadio'),
  duration: t('components.Queue.label.duration'),
  addArtistContentFilter: t('components.Queue.label.addArtistContentFilter'),
  restart: t('components.Queue.label.restart'),
  previous: t('components.Queue.label.previous'),
  next: t('components.Queue.label.next'),
  pause: t('components.Queue.label.pause'),
  play: t('components.Queue.label.play'),
  fullscreen: t('components.Queue.label.enterFullscreen'),
  exitFullscreen: t('components.Queue.label.exitFullscreen'),
  showCoverArt: t('components.Queue.label.showCoverArt'),
  showVisualizer: t('components.Queue.label.showVisualizer')
}))

watchEffect(async () => {
  scrollLock.value = !!store.state.ui.queueFocused
  if (store.state.ui.queueFocused) {
    await nextTick()
    activate()
  } else {
    deactivate()
  }
})

const list = ref()
const el = useCurrentElement()
const scrollToCurrent = (behavior: ScrollBehavior = 'smooth') => {
  if (el.value != null && 'querySelector' in el.value) {
    const item = el.value.querySelector('.queue-item.active')
    item?.scrollIntoView({
      behavior,
      block: 'center'
    })
  }
}

watchDebounced(currentTrack, () => scrollToCurrent(), { debounce: 100 })

whenever(
  () => queue.value.length === 0,
  () => store.commit('ui/queueFocused', null),
  { immediate: true }
)

const router = useRouter()
router.beforeEach(() => store.commit('ui/queueFocused', null))

const isDragging = ref(false)
const dragPosition = ref(0)
const progressBar = ref<HTMLElement | null>(null)

const handleProgressUpdate = (event: MouseEvent | TouchEvent) => {
  if (!progressBar.value) return

  let clientX: number

  // 1. Properly differentiate between Touch and Mouse
  if ('targetTouches' in event) {
    // TouchEvent: Get the clientX from the first touch point
    const touch = event.targetTouches[0]
    if (!touch) return
    clientX = touch.clientX
  } else {
    // MouseEvent
    clientX = event.clientX
  }

  const rect = progressBar.value.getBoundingClientRect()

  // 2. Standardize the math
  const percentage = Math.max(0, Math.min((clientX - rect.left) / rect.width, 1))

  dragPosition.value = percentage * 100
  seekTo(percentage * (duration.value || 0))
}

const onMouseDown = (event: MouseEvent) => {
  event.stopPropagation()
  isDragging.value = true
  handleProgressUpdate(event)
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp)
}

const onMouseMove = (event: MouseEvent) => { if (isDragging.value) handleProgressUpdate(event) }

const onMouseUp = () => {
  isDragging.value = false
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseup', onMouseUp)
}

const onTouchStart = (event: TouchEvent) => { event.stopPropagation(); isDragging.value = true; handleProgressUpdate(event) }
const onTouchMove = (event: TouchEvent) => { event.stopPropagation(); isDragging.value = true; handleProgressUpdate(event) }
const onTouchEnd = (event: TouchEvent) => { isDragging.value = false; handleProgressUpdate(event) }

onUnmounted(() => {
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseup', onMouseUp)
})

const play = async (index: number) => {
  try {
    isPlaying.value = true
    await playTrack(index)
  } catch (error: any) {
    isPlaying.value = false
    await useErrorHandler(error)
  }
}

const queueItems = computed(() => queue.value.map((track, index) => ({
  ...track,
  key: `${index}-${track.id}`,
  labels: {
    remove: t('components.Queue.label.remove'),
    selectTrack: t('components.Queue.label.selectTrack'),
    favorite: t('components.Queue.label.favorite')
  }
}) as QueueItemSource))

const reorderTracks = async (from: number, to: number) => {
  reorder(from, to)

  await nextTick()
  if (to === currentIndex.value) {
    scrollToCurrent()
  }
}
const hideArtist = () => {
  const { value } = currentTrack
  if (value != null && value.artistId !== -1 && value.artistCredit) {
    return store.dispatch('moderation/hide', {
      type: 'artist',
      target: {
        id: value.artistCredit[0]?.artist.id,
        name: value.artistCredit[0]?.artist.name
      }
    })
  }
}

const cover = ref()
const { isFullscreen: fullscreen, enter, exit } = useFullscreen(cover)
const { idle } = useIdle(2000)

const showTrackInfo = refAutoReset(false, 5000)
whenever(currentTrack, () => (showTrackInfo.value = true))

const trackLinkIsOverflowing = ref(false)
const trackLinkRef = ref<HTMLElement>()

const checkTrackLinkOverflow = () => {
  let linkElement = (trackLinkRef.value as any)?.$el || trackLinkRef.value

  if (linkElement?.tagName !== 'A') {
    linkElement = linkElement?.querySelector('a')
  }

  if (linkElement?.parentElement) {
    trackLinkIsOverflowing.value = linkElement.scrollWidth > linkElement.parentElement.clientWidth
  }
}

watchEffect(() => {
  if (currentTrack.value) {
    nextTick(() => checkTrackLinkOverflow())
  }
})

const resizeObserver = new ResizeObserver(() => checkTrackLinkOverflow())
watchEffect(() => {
  const playerDiv = document.getElementById('player')
  if (playerDiv) {
    resizeObserver.observe(playerDiv)
    return () => resizeObserver.disconnect()
  }
})

const milkdrop = ref()
const loadRandomPreset = () => {
  milkdrop.value?.loadRandomPreset()
}

enum CoverType {
  COVER_ART,
  MILK_DROP
}

let isWebGLSupported = false
try {
  const canvas = document.createElement('canvas')
  isWebGLSupported = !!canvas.getContext('webgl2')
} catch (error) {}

const coverType = useStorage('queue:cover-type', CoverType.COVER_ART)
if (!isWebGLSupported) {
  coverType.value = CoverType.COVER_ART
}

const setCoverType = async (type: CoverType) => {
  const isMilkDrop = type === CoverType.MILK_DROP
  coverType.value = type

  if (isMilkDrop) {
    if (getAudioContext().state === 'suspended') {
      await getAudioContext().resume()
    }
    isWebAudioRequested.value = true
  } else {
    const { currentTime } = usePlayer()
    const { createTrack, clearCache } = useTracks()
    const { currentIndex } = useQueue()
    const wasPlaying = isPlaying.value
    const savedTime = currentTime.value

    // 1. Pause
    isPlaying.value = false

    // 2. Switch mode before recreating so new HTMLSound skips createMediaElementSource
    isWebAudioRequested.value = false
    // reset MediaSession so iOS establishes a new session
    resetHandlers()
    // 3. Dispose current sound and clear cache so createTrack creates a fresh HTMLSound
    await currentSound.value?.dispose()
    clearCache()

    // 4. Recreate, seek, resume
    await createTrack(currentIndex.value)
    await nextTick() // wait for Vue to update currentSound reactive ref
    await currentSound.value?.seekTo(savedTime)
    if (wasPlaying) isPlaying.value = true

    // Restore metadata since resetHandlers cleared it and track didn't change
    refreshMetadata()
  }
}
</script>

<template>
  <section
    class="main opaque component-queue default solid"
    :aria-label="labels.queue"
  >
    <div
      id="queue-grid"
      :class="store.state.ui.queueFocused && `show-${store.state.ui.queueFocused}`"
    >
      <div
        id="player"
        class="ui basic segment"
      >
        <template v-if="currentTrack">
          <div
            ref="cover"
            :class="['cover-container', { idle, fullscreen }]"
          >
            <div class="cover">
              <template v-if="coverType === CoverType.COVER_ART">
                <img
                  v-if="fullscreen"
                  class="cover-shadow"
                  :src="store.getters['instance/absoluteUrl'](currentTrack.coverUrl)"
                >
                <img
                  ref="cover"
                  alt=""
                  :src="store.getters['instance/absoluteUrl'](currentTrack.coverUrl)"
                >
              </template>
              <milk-drop
                v-else-if="coverType === CoverType.MILK_DROP"
                ref="milkdrop"
              />

              <Transition name="queue">
                <div
                  v-if="!fullscreen || !idle"
                  class="cover-buttons"
                >
                  <tooltip :content="!isWebGLSupported && t('components.Queue.message.webglUnsupported')">
                    <Button
                      v-if="coverType === CoverType.COVER_ART"
                      :aria-label="labels.showVisualizer"
                      :title="labels.showVisualizer"
                      :disabled="!isWebGLSupported"
                      icon="bi-display"
                      @click="setCoverType(CoverType.MILK_DROP)"
                    />
                    <Button
                      v-else-if="coverType === CoverType.MILK_DROP"
                      :aria-label="labels.showCoverArt"
                      :title="labels.showCoverArt"
                      :disabled="!isWebGLSupported"
                      icon="bi-image-fill"
                      @click="setCoverType(CoverType.COVER_ART)"
                    />
                  </tooltip>

                  <Button
                    v-if="!fullscreen"
                    :aria-label="labels.fullscreen"
                    :title="labels.fullscreen"
                    icon="bi-arrows-fullscreen"
                    @click="enter"
                  />
                  <Button
                    v-else
                    secondary
                    :aria-label="labels.exitFullscreen"
                    :title="labels.exitFullscreen"
                    icon="bi-fullscreen-exit"
                    @click="exit"
                  />
                </div>
              </Transition>
              <Transition name="queue">
                <div
                  v-if="fullscreen && (!idle || showTrackInfo)"
                  class="track-info"
                  @click="loadRandomPreset()"
                >
                  <h1>{{ currentTrack.title }}</h1>
                  <h2>
                    <div
                      v-for="ac in currentTrack.artistCredit"
                      :key="ac.artist.id"
                    >
                      {{ ac.credit ?? t('components.Queue.meta.unknownArtist') }}
                      <span>{{ ac.joinphrase }}</span>
                    </div>
                    <span class="symbol hyphen middle" />
                    {{ currentTrack.albumTitle ?? t('components.Queue.meta.unknownAlbum') }}
                  </h2>
                </div>
              </Transition>
            </div>
          </div>
          <h1 class="ui header">
            <Link
              ref="trackLinkRef"
              class="track"
              :class="{ scrolling: trackLinkIsOverflowing }"
              :to="{name: 'library.tracks.detail', params: {id: currentTrack.id }}"
            >
              {{ currentTrack.title }}
            </Link>
          </h1>
          <h2 class="ui header">
            <template v-if="currentTrack.albumId !== -1">
              <Link
                class="album"
                :to="{name: 'library.albums.detail', params: {id: currentTrack.albumId }}"
              >
                {{ currentTrack.albumTitle ?? t('components.Queue.meta.unknownAlbum') }}
              </Link>
            </template>
          </h2>
          <span>
            <ArtistCreditLabel
              v-if="currentTrack.artistCredit"
              :artist-credit="currentTrack.artistCredit"
            />
          </span>
          <div
            v-if="currentTrack && errored"
            class="ui small warning message"
          >
            <h3 class="header">
              {{ t('components.Queue.header.failure') }}
            </h3>
            <p v-if="hasNext && isPlaying">
              {{ t('components.Queue.message.automaticPlay') }}
              <i class="loading spinner icon" />
            </p>
            <p>
              {{ t('components.Queue.warning.connectivity') }}
            </p>
          </div>
          <div
            v-else-if="currentSound && !currentSound.playable"
            class="ui small warning message"
          >
            <h3 class="header">
              {{ t('components.Queue.header.noSources') }}
            </h3>
            <p v-if="hasNext && isPlaying">
              {{ t('components.Queue.message.automaticPlay') }}
              <i class="loading spinner icon" />
            </p>
          </div>
          <Spacer
            :size="16"
            class="desktop-and-below"
          />
          <Layout
            flex
            class="additional-controls desktop-and-below"
          >
            <track-favorite-icon
              v-if="store.state.auth.authenticated"
              :track="currentTrack"
              ghost
            />
            <track-playlist-icon
              v-if="store.state.auth.authenticated"
              :track="currentTrack"
              ghost
            />
            <Button
              v-if="store.state.auth.authenticated"
              ghost
              icon="bi-eye-slash"
              :aria-label="labels.addArtistContentFilter"
              :title="labels.addArtistContentFilter"
              @click="hideArtist"
            />
          </Layout>
          <div class="progress-wrapper">
            <div class="progress-area">
              <div
                ref="progressBar"
                :class="['ui', 'small', 'vibrant', {'indicating': isLoadingAudio && !errored}, 'progress']"
                :style="{
                  '--fw-track-progress': isDragging
                    ? `${dragPosition}%`
                    : `${(currentTime / duration) * 100}%`
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
              </div>

              <Teleport to="body">
                <div
                  v-if="isDragging"
                  style="position:fixed;inset:0;z-index:99999;cursor:grabbing"
                  @mousemove="onMouseMove"
                  @mouseup="onMouseUp"
                />
              </Teleport>
            </div>
            <div class="progress">
              <template v-if="!isLoadingAudio">
                <a
                  href=""
                  :aria-label="labels.restart"
                  class="left floated timer discrete start"
                  @click.prevent="currentTime = 0"
                >
                  {{ time.parse(Math.round(currentTime)) }}
                </a>
                <span class="right floated timer total">{{ time.parse(Math.round(duration)) }}</span>
              </template>
              <template v-else>
                <span class="left floated timer">{{ t('components.Queue.meta.startTime') }}</span>
                <span class="right floated timer">{{ t('components.Queue.meta.startTime') }}</span>
              </template>
            </div>
          </div>
        </template>
      </div>
      <div id="queue">
        <div class="ui basic clearing segment">
          <h2
            class="ui header"
            :style="store.state.ui.queueFocused === 'queue' ? 'padding-left: 16px;' : ''"
          >
            <div class="content">
              <Button
                ghost
                icon="bi-chevron-down"
                style="float: right;"
                @click="store.commit('ui/queueFocused', null)"
              />
              <Button
                destructive
                outline
                icon="bi-trash-fill"
                style="float: right; margin-right: 16px;"
                @click="clear"
              >
                {{ t('components.Queue.button.clear') }}
              </Button>
              {{ labels.queue }}
              <div class="sub header">
                <div>
                  <i18n-t keypath="components.Queue.meta.queuePosition">
                    <template #index>
                      {{ currentIndex + 1 }}
                    </template>
                    <template #length>
                      {{ queue.length }}
                    </template>
                  </i18n-t>
                  <span class="middle pipe symbol" />
                  <span
                    style="margin-right: 8px;"
                  >
                    {{ t('components.Queue.meta.end') }}
                  </span>
                  <span :title="labels.duration">
                    {{ endsIn }}
                  </span>
                </div>
              </div>
            </div>
          </h2>
        </div>
        <virtual-list
          v-if="queueItems.length !== 0"
          ref="list"
          :list="queueItems"
          :component="QueueItem"
          :size="60"
          @reorder="reorderTracks"
          @visible="list.scrollToIndex(currentIndex, 'center')"
        >
          <template #default="{ index, item, classlist }">
            <queue-item
              v-if="index !== undefined"
              :data-index="index"
              :index="index"
              :source="item"
              :class="[...classlist, currentIndex === index && 'active']"
              @play="play"
              @remove="dequeue"
            />
          </template>
          <template #footer>
            <div
              v-if="store.state.radios.populating"
              class="radio-populating"
            >
              <i class="loading spinner icon" />
              {{ labels.populating }}
            </div>
            <div
              v-if="store.state.radios.running"
              class="ui info message radio-message"
            >
              <div class="content">
                <h3 class="header">
                  <i class="bi bi-boombox-fill" />
                  {{ t('components.Queue.header.radio') }}
                </h3>
                <p>
                  {{ t('components.Queue.message.radio') }}
                </p>
                <Button
                  primary
                  icon="bi-stop-fill"
                  @click="store.dispatch('radios/stop')"
                >
                  {{ t('components.Queue.button.stopRadio') }}
                </Button>
              </div>
            </div>
          </template>
        </virtual-list>
      </div>
    </div>
  </section>
</template>
