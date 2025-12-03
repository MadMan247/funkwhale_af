<script setup lang="ts">
import type { Channel, Upload } from '~/types'

import { computed, ref, reactive, watch } from 'vue'
import { whenever } from '@vueuse/core'
import { useStore } from '~/store'
import { useI18n } from 'vue-i18n'
import { useModal } from '~/ui/composables/useModal.ts'

import axios from 'axios'

import ChannelEntries from '~/components/audio/ChannelEntries.vue'
import ChannelSeries from '~/components/audio/ChannelSeries.vue'
import AlbumModal from '~/components/channels/AlbumModal.vue'

import Loader from '~/components/ui/Loader.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Alert from '~/components/ui/Alert.vue'
import Button from '~/components/ui/Button.vue'
import Link from '~/components/ui/Link.vue'

import useWebSocketHandler from '~/composables/useWebSocketHandler'

interface Props {
  object: Channel
}

const { t } = useI18n()

const props = defineProps<Props>()

const store = useStore()

const isPodcast = computed(() => props.object.artist?.content_category === 'podcast')
const isOwner = computed(() => store.state.auth.authenticated && props.object.attributed_to.full_username === store.state.auth.fullUsername)

const seriesFilters = computed(() => ({
  artist: props.object.artist?.id,
  ordering: '-creation_date',
  playable: isOwner.value
    ? undefined
    : true
}))

const pendingUploads = reactive([] as Upload[])
const processedUploads = computed(() => pendingUploads.filter(upload => upload.import_status !== 'pending'))
const finishedUploads = computed(() => pendingUploads.filter(upload => upload.import_status === 'finished'))
const erroredUploads = computed(() => pendingUploads.filter(upload => upload.import_status === 'errored'))
const skippedUploads = computed(() => pendingUploads.filter(upload => upload.import_status === 'skipped'))

const pendingUploadsById = computed(() => pendingUploads.reduce((acc, upload) => {
  acc[upload.uuid] = upload
  return acc
}, {} as Record<string, Upload>))

const isOver = computed(() => pendingUploads.length === processedUploads.value.length)
const isSuccessfull = computed(() => pendingUploads.length === finishedUploads.value.length)

watch(() => store.state.channels.latestPublication, (value) => {
  if (value?.channel.uuid === props.object.uuid && value?.uploads && value?.uploads.length > 0) {
    pendingUploads.push(...value.uploads)
  }
})

const episodesKey = ref(new Date())
const seriesKey = ref(new Date())
whenever(isOver, () => {
  episodesKey.value = new Date()
  seriesKey.value = new Date()
})

const fetchPendingUploads = async () => {
  try {
    const response = await axios.get('uploads/', {
      params: { channel: props.object.uuid, import_status: ['pending', 'skipped', 'errored'], include_channels: 'true' },
      paramsSerializer: {
        indexes: null
      }
    })

    pendingUploads.length = 0
    pendingUploads.push(...response.data.results)
  } catch (error) {

  }
}

if (isOwner.value) {
  fetchPendingUploads()
    .then(() => {
      useWebSocketHandler('import.status_updated', (event) => {
        const pendingUpload = pendingUploadsById.value[event.upload.uuid]
        if (pendingUpload == null) return
        Object.assign(pendingUpload, event.upload)
      })
    })
}

const { to, isOpen } = useModal('album')
</script>

<template>
  <section>
    <Alert
      v-if="pendingUploads.length > 0"
      yellow
    >
      <template v-if="isSuccessfull">
        <Button
          icon="bi-x"
          round
          ghost
          square-small
          style="float: right;"
          @click="pendingUploads.length = 0"
        />
        <h3 class="ui header">
          {{ t('views.channels.DetailOverview.header.uploadsSuccess') }}
        </h3>
        <p>
          {{ t('views.channels.DetailOverview.meta.progress', {finished: processedUploads.length, total: pendingUploads.length}) }}
        </p>
      </template>
      <template v-else-if="isOver">
        <h3 class="ui header">
          {{ t('views.channels.DetailOverview.header.uploadsFailure') }}
        </h3>
        <Link
          v-if="skippedUploads.length > 0"
          secondary
          solid
          :to="{name: 'content.libraries.files', query: {q: 'status:skipped'}}"
        >
          {{ t('views.channels.DetailOverview.link.skippedUploads') }}
        </Link>
        <Link
          v-if="erroredUploads.length > 0"
          secondary
          solid
          :to="{name: 'content.libraries.files', query: {q: 'status:errored'}}"
        >
          {{ t('views.channels.DetailOverview.link.erroredUploads') }}
        </Link>
      </template>
      <template v-else>
        <Loader :container="false" />
        <h3 class="ui header">
          {{ t('views.channels.DetailOverview.header.uploadsProcessing') }}
        </h3>
        <p>
          {{ t('views.channels.DetailOverview.message.processing') }}
        </p>
        <p>
          {{ t('views.channels.DetailOverview.meta.progress', {finished: processedUploads.length, total: pendingUploads.length}) }}
        </p>
      </template>
    </Alert>
    <channel-entries
      :key="String(episodesKey) + 'entries'"
      :is-podcast="isPodcast"
      :default-cover="object.artist?.cover || null"
      :filters="{channel: object.uuid, ordering: '-creation_date'}"
    >
      <h2 class="ui header">
        <span
          v-if="isPodcast"
        >
          {{ t('views.channels.DetailOverview.header.latestEpisodes') }}
        </span>
        <span
          v-else
        >
          {{ t('views.channels.DetailOverview.header.latestTracks') }}
        </span>
      </h2>
    </channel-entries>
    <Spacer />
    <channel-series
      :key="String(seriesKey) + 'series'"
      :filters="seriesFilters"
      :is-podcast="isPodcast"
    >
      <h2 class="ui with-actions header">
        <span
          v-if="isPodcast"
        >
          {{ t('views.channels.DetailOverview.header.series') }}
        </span>
        <span
          v-else
        >
          {{ t('views.channels.DetailOverview.header.albums') }}
        </span>
        <div
          v-if="isOwner"
          class="actions"
        >
          <Link
            :to="to"
          >
            <i class="bi bi-plus" />
            {{ t('views.channels.DetailOverview.link.addAlbum') }}
          </Link>
        </div>
      </h2>
    </channel-series>
    <album-modal
      v-if="isOwner"
      :model-value="object"
      :channel="object"
      @created="isOpen = false; seriesKey = new Date()"
    />
  </section>
</template>
