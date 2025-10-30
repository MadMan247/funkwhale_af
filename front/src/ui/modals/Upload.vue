<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'
import { useModal } from '~/ui/composables/useModal.ts'

import Modal from '~/components/ui/Modal.vue'
import Button from '~/components/ui/Button.vue'
import Layout from '~/components/ui/Layout.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Card from '~/components/ui/Card.vue'

import type { Channel, PrivacyLevelEnum } from '~/types'
import ChannelUpload from '~/components/channels/UploadForm.vue'
import LibraryUpload from '~/components/library/FileUpload.vue'

const { t } = useI18n()
const store = useStore()

const { isOpen } = useModal('upload')

type UploadDestination =
  | { type: 'channel', channel?: Channel | null, filter?: 'podcast' | 'music' }
  | { type: 'library' }

type State =
  { uploadDestination?: UploadDestination, page: typeof pages[number], files?: string[] }

// initial state
const init = () => (
  store.state.channels.uploadModalConfig.channel
    ? {
      page: 'uploadFiles',
      uploadDestination: { type: 'channel', channel: store.state.channels.uploadModalConfig.channel }
    } as const
    : { page: 'selectDestination' } as const
)
const state = ref<State>(init())

const pages = ['selectDestination', 'uploadFiles', 'uploadsInProgress'] as const

const goBack = computed(() =>
  state.value.page === 'selectDestination'
    ? undefined
    : () => { state.value.page = pages[pages.indexOf(state.value.page) - 1]! }
)

// Step 1
const destinationSelected = (destination: UploadDestination) =>
  state.value = { ...state.value, uploadDestination: destination, page: 'uploadFiles' }

const direction = ref<'forward' | 'backward'>('forward')

watch(state, ({ page }, oldValue) => {
  direction.value
    = pages.indexOf(page) > pages.indexOf(oldValue.page)
      ? 'forward'
      : 'backward'

  // TODO: Tidy up this dirty dirty hack
  // Also, it only works for the first page
  document.querySelector('#app')?.setAttribute('inert', 'true')
}, { deep: true })

// Step 1.1

// Load the library for the chosen privacy level
const privacyLevel = ref<PrivacyLevelEnum>('me')

const modalTitle = computed(() =>
({ selectDestination: 'Upload', uploadFiles: 'Select files for upload', uploadsInProgress: 'Uploading...' }
[state.value.page])
)

const channelUpload = ref()
</script>

<template>
  <Modal
    v-model="isOpen"
    :title="modalTitle"
  >
    <template
      v-if="goBack"
      #topleft
    >
      <Button
        icon="bi-chevron-compact-left"
        :title="t('components.channels.UploadModal.button.previous')"
        @click="goBack"
      />
      <Spacer grow />
    </template>

    <Transition
      mode="out-in"
      :class="direction"
    >
      <!-- Page content -->
      <!-- Page 1 -->

      <Layout
        v-if="state.page === 'selectDestination'"
        flex
        style="place-content:center"
      >
        <Card
          small
          solid
          title="Music"
          icon="bi-upload"
          @click="destinationSelected({ type: 'library' })"
        >
          <template #image>
            <i
              class="bi bi-headphones solid secondary raised"
              :class="$style.icon"
            />
          </template>
          {{ t('modals.upload.library') }}
        </Card>
        <Card
          small
          solid
          title="Music"
          icon="bi-upload primary solid"
          @click="destinationSelected({ type: 'channel', filter: 'music' })"
        >
          <template #image>
            <i
              class="bi bi-music-note-beamed solid primary"
              :class="$style.icon"
            />
          </template>
          {{ t('modals.upload.musicChannel') }}
        </Card>
        <Card
          small
          solid
          title="Podcast"
          icon="bi-upload primary solid"
          @click="destinationSelected({ type: 'channel', filter: 'podcast' })"
        >
          <template #image>
            <i
              class="bi bi-mic-fill solid primary"
              :class="$style.icon"
            />
          </template>
          {{ t('modals.upload.podcastChannel') }}
        </Card>
      </Layout>

      <!-- Page 2 -->

      <Layout
        v-else-if="state.page === 'uploadFiles'"
        stack
      >
        <ChannelUpload
          v-if="state.uploadDestination?.type === 'channel'"
          ref="channelUpload"
          :filter="state.uploadDestination.filter"
          :channel="state.uploadDestination?.channel || null"
        />

        <LibraryUpload
          v-if="state.uploadDestination?.type === 'library'"
          v-model="privacyLevel"
        />
        {{ state.files }}
      </Layout>
    </Transition>

    <template #actions>
      <Spacer
        h
        grow
      />
      <Button
        v-if="state.page === 'uploadFiles' && !channelUpload"
        primary
        @click="() => { isOpen = false }"
      >
        {{ t('components.channels.UploadModal.button.finishLater') }}
      </Button>
      <Button
        v-if="channelUpload"
        primary
        @click="() => { channelUpload.publish(); isOpen = false }"
      >
        {{ t('components.channels.UploadModal.button.publish') }}
      </Button>
    </template>
  </Modal>
</template>

<style module>
.icon {
  font-size: 100px;
  padding: 28px;
  inset: 0;
  display: block;
  text-align: center;
}
</style>
<style>
.v-enter-active,
.v-leave-active {
  transition: all 0.5s ease;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;

  &.forward {
    transform: translateX(100%);
  }

  &.backward {
    transform: translateX(-100%);
  }
}

.v-leave-to {
  &.forward {
    transform: translateX(100%);
  }

  &.backward {
    transform: translateX(-100%);
  }
}
</style>
