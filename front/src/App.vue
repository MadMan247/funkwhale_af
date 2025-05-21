<script setup lang="ts">
import { watchEffect, computed, onMounted, nextTick } from 'vue'

import { type QueueTrack, useQueue } from '~/composables/audio/queue'
import { useStore } from '~/store'
import useLogger from '~/composables/useLogger'
import { useStyleTag, useIntervalFn } from '@vueuse/core'
import { color } from '~/composables/color'

import { generateTrackCreditStringFromQueue } from '~/utils/utils'

import PlaylistModal from '~/components/playlists/PlaylistModal.vue'
import FilterModal from '~/components/moderation/FilterModal.vue'
import ReportModal from '~/components/moderation/ReportModal.vue'
import ServiceMessages from '~/components/ServiceMessages.vue'
import AudioPlayer from '~/components/audio/Player.vue'
import Queue from '~/components/Queue.vue'
import Sidebar from '~/ui/components/Sidebar.vue'
import ShortcutsModal from '~/ui/modals/Shortcuts.vue'
import LanguagesModal from '~/ui/modals/Language.vue'
import SearchModal from '~/ui/modals/Search.vue'
import UploadModal from '~/ui/modals/Upload.vue'
import Loader from '~/components/ui/Loader.vue'

// Fake content
onMounted(async () => {
  await nextTick()
  document.getElementById('fake-app')?.remove()
})

const logger = useLogger()
logger.debug('App setup()')

const store = useStore()

// Tracks
const { currentTrack } = useQueue()
const getTrackInformationText = (track: QueueTrack | undefined) => {
  if (!track) {
    return null
  }

  return `♫ ${track.title} – ${generateTrackCreditStringFromQueue(track)} ♫`
}

// Update title
const initialTitle = document.title
watchEffect(() => {
  const parts = [
    getTrackInformationText(currentTrack.value),
    store.state.ui.pageTitle,
    initialTitle || 'Funkwhale'
  ]

  document.title = parts.filter(i => i).join(' – ')
})

// Styles
useStyleTag(computed(() => store.state.instance.settings.ui.custom_css.value))

// Fake content
onMounted(async () => {
  await nextTick()
  document.getElementById('fake-content')?.classList.add('loaded')
})

// Time ago
useIntervalFn(() => {
  // used to redraw ago dates every minute
  store.commit('ui/computeLastDate')
}, 1000 * 60)

// Fetch user data on startup
// NOTE: We're not checking if we're authenticated in the store,
//       because we want to learn if we are authenticated at all
store.dispatch('auth/fetchUser')

</script>

<template>
  <div class="funkwhale responsive">
    <Sidebar />
    <RouterView
      v-slot="{ Component }"
      v-bind="color({}, ['default', 'solid'])()"
      :class="$style.layout"
    >
      <Transition
        v-if="Component"
        name="main"
        mode="out-in"
      >
        <KeepAlive :max="10">
          <Suspense>
            <component :is="Component" />
            <template #fallback>
              <Loader />
            </template>
          </Suspense>
        </KeepAlive>
      </Transition>
      <transition name="queue">
        <Queue v-show="store.state.ui.queueFocused" />
      </transition>
    </RouterView>
  </div>
  <AudioPlayer
    class="funkwhale"
    v-bind="color({}, ['default', 'solid'])()"
  />
  <ServiceMessages />
  <LanguagesModal />
  <ShortcutsModal />
  <PlaylistModal v-if="store.state.auth.authenticated" />
  <FilterModal v-if="store.state.auth.authenticated" />
  <ReportModal />
  <UploadModal v-if="store.state.auth.authenticated" />
  <SearchModal />
</template>

<style scoped lang="scss">
.responsive {
  display: grid !important;
  grid-template-rows: min-content;
  min-height: 100vh;

  @media screen and (min-width: 1024px) {
    grid-template-columns: 300px 1fr;
    grid-template-rows: 100% 0 0;
  }
}
</style>
<style>
  /* Make inert pages (behind modals) unscrollable */
  body:has(#app[inert="true"]) {
    overflow:hidden;
  }
</style>
<style module>
  .layout {
    padding: 32px;
  }
</style>
