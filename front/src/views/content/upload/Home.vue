<script setup lang="ts">
import { humanSize } from '~/utils/filters'
import { useI18n } from 'vue-i18n'
import { computed, ref, type Ref } from 'vue'
import { useStore } from '~/store'

// LIBRARIES BEGIN

import type { Library, Channel } from '~/types'

import axios from 'axios'

import LibraryCard from '../libraries/CardUpload.vue'
import ChannelCard from '../channels/CardUpload.vue'
import Upload from '~/ui/pages/upload.vue'
// import UploadModal from '~/ui/pages/upload.vue'
// const ChannelUploadModal = defineAsyncComponent(() => import('~/components/channels/UploadModal.vue'))

import useErrorHandler from '~/composables/useErrorHandler'

// TODO: Delete this file.

const { t } = useI18n()

const libraries = ref([] as Library[])
const channels = ref([] as Channel[])

const musicChannels = computed(() => channels.value.filter(channel => channel.artist?.content_category !== 'podcast'))
const podcastChannels = computed(() => channels.value.filter(channel => channel.artist?.content_category === 'podcast'))

const isLoading = ref(false)
const hiddenForm = ref(true)
const fetchLibraries = async () => {
  isLoading.value = true

  try {
    const response = await axios.get('libraries/', { params: { scope: 'me' } })
    libraries.value = response.data.results
    if (libraries.value.length === 0) {
      hiddenForm.value = false
    }
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}
const fetchChannels = async () => {
  isLoading.value = true

  try {
    const response = await axios.get('channels/', { params: { scope: 'me' } })
    channels.value = response.data.results
    if (channels.value.length === 0) {
      hiddenForm.value = false
    }
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

fetchLibraries()
fetchChannels()

// TODO: Check if this is needed:
// const libraryCreated = (library: Library) => {
//   router.push({ name: 'library.detail', params: { id: library.uuid } })
// }

// LIBRARIES END

const labels = computed(() => ({
  title: t('views.content.Home.title')
}))

const store = useStore()

const quota = computed(() => store.state.instance.settings.users.upload_quota.value)
const defaultQuota = computed(() => humanSize(quota.value * 1e6))

// Plus Icon

const plusIcon = 'data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iaXNvLTg4NTktMSI/Pg0KPCEtLSBVcGxvYWRlZCB0bzogU1ZHIFJlcG8sIHd3dy5zdmdyZXBvLmNvbSwgR2VuZXJhdG9yOiBTVkcgUmVwbyBNaXhlciBUb29scyAtLT4NCjxzdmcgZmlsbD0iIzAwMDAwMCIgaGVpZ2h0PSI4MDBweCIgd2lkdGg9IjgwMHB4IiB2ZXJzaW9uPSIxLjEiIGlkPSJDYXBhXzEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIA0KCSB2aWV3Qm94PSIwIDAgNDkwIDQ5MCIgeG1sOnNwYWNlPSJwcmVzZXJ2ZSI+DQo8Zz4NCgk8Zz4NCgkJPGc+DQoJCQk8cGF0aCBkPSJNMjI3LjgsMTc0LjF2NTMuN2gtNTMuN2MtOS41LDAtMTcuMiw3LjctMTcuMiwxNy4yczcuNywxNy4yLDE3LjIsMTcuMmg1My43djUzLjdjMCw5LjUsNy43LDE3LjIsMTcuMiwxNy4yDQoJCQkJczE3LjEtNy43LDE3LjEtMTcuMnYtNTMuN2g1My43YzkuNSwwLDE3LjItNy43LDE3LjItMTcuMnMtNy43LTE3LjItMTcuMi0xNy4yaC01My43di01My43YzAtOS41LTcuNy0xNy4yLTE3LjEtMTcuMg0KCQkJCVMyMjcuOCwxNjQuNiwyMjcuOCwxNzQuMXoiLz4NCgkJCTxwYXRoIGQ9Ik03MS43LDcxLjdDMjUuNSwxMTgsMCwxNzkuNSwwLDI0NXMyNS41LDEyNyw3MS44LDE3My4zQzExOCw0NjQuNSwxNzkuNiw0OTAsMjQ1LDQ5MHMxMjctMjUuNSwxNzMuMy03MS44DQoJCQkJQzQ2NC41LDM3Miw0OTAsMzEwLjQsNDkwLDI0NXMtMjUuNS0xMjctNzEuOC0xNzMuM0MzNzIsMjUuNSwzMTAuNSwwLDI0NSwwQzE3OS42LDAsMTE4LDI1LjUsNzEuNyw3MS43eiBNNDU1LjcsMjQ1DQoJCQkJYzAsNTYuMy0yMS45LDEwOS4yLTYxLjcsMTQ5cy05Mi43LDYxLjctMTQ5LDYxLjdTMTM1LjgsNDMzLjgsOTYsMzk0cy02MS43LTkyLjctNjEuNy0xNDlTNTYuMiwxMzUuOCw5Niw5NnM5Mi43LTYxLjcsMTQ5LTYxLjcNCgkJCQlTMzU0LjIsNTYuMiwzOTQsOTZTNDU1LjcsMTg4LjcsNDU1LjcsMjQ1eiIvPg0KCQk8L2c+DQoJPC9nPg0KCTxnPg0KCTwvZz4NCgk8Zz4NCgk8L2c+DQoJPGc+DQoJPC9nPg0KCTxnPg0KCTwvZz4NCgk8Zz4NCgk8L2c+DQoJPGc+DQoJPC9nPg0KCTxnPg0KCTwvZz4NCgk8Zz4NCgk8L2c+DQoJPGc+DQoJPC9nPg0KCTxnPg0KCTwvZz4NCgk8Zz4NCgk8L2c+DQoJPGc+DQoJPC9nPg0KCTxnPg0KCTwvZz4NCgk8Zz4NCgk8L2c+DQoJPGc+DQoJPC9nPg0KPC9nPg0KPC9zdmc+'

// Open modal

const upload = ref(false)
const object:Ref<Library | Channel | undefined> = ref()

const openModal = (object_: Library | Channel) => {
  // upload.value = true;
  object.value = object_

  // open old modal model
  store.state.channels.showUploadModal = true
  store.state.channels.uploadModalConfig = { channel: 'artist' in object.value ? (object as Ref<Channel>).value : null }
}
</script>

<template>
  <!-- TODO: Remove this module -->
  <!-- eslint-disable @intlify/vue-i18n/no-raw-text -->
  <section
    v-title="labels.title"
    class="ui vertical aligned stripe segment"
  >
    <div class="ui text container">
      <h1>{{ labels.title }}</h1>
      <p>
        <strong>{{ t('views.content.Home.help.uploadQuota', { quota: defaultQuota }) }}</strong>
      </p>
      <hr>
      <h3>Choose a library:</h3>
      <fw-card
        :image="plusIcon"
        :title="'New Library'"
      />

      <!-- TODO: Check what value `new` should be -->
      <library-card
        v-for="library in libraries"
        :key="library.uuid"
        :new="false"
        :library="library"
      />

      <h3>Choose a music channel:</h3>
      <section style="display:flex;margin:-16px;flex-wrap:wrap;">
        <channel-card
          v-for="channel in musicChannels"
          :key="channel.uuid"
          :channel="channel"
          :callback="openModal"
        />
      </section>

      <h3>Choose a podcast channel:</h3>
      <section style="display:flex;gap:16px;flex-wrap:wrap;">
        <channel-card
          v-for="channel in podcastChannels"
          :key="channel.uuid"
          class="column"
          :channel="channel"
          :callback="openModal"
        />
      </section>
    </div>
  </section>

  <fw-modal
    v-model="upload"
    :title="`Upload to ${
      object ?
        'artist' in object ?
          object.artist?.name
          : 'I am a library'
        : 'I am undefined'}`"
  >
    <upload />
  </fw-modal>
  <!-- <channel-upload-modal v-if="store.state.auth.authenticated" /> -->
  <!-- eslint-enable @intlify/vue-i18n/no-raw-text -->
</template>
