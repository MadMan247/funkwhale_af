<script setup lang="ts">
import type { BackendError, Channel, Upload, Track } from '~/types'
import type { VueUploadItem } from 'vue-upload-component'

import { computed, ref, reactive, watchEffect, watch } from 'vue'
import { whenever } from '@vueuse/core'
import { humanSize } from '~/utils/filters'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'

import axios from 'axios'
import { type paths, type operations, type components } from '~/generated/types.ts'

import UploadMetadataForm from '~/components/channels/UploadMetadataForm.vue'
import FileUploadWidget from '~/components/library/FileUploadWidget.vue'
import LicenseSelect from '~/components/channels/LicenseSelect.vue'
import AlbumSelect from '~/components/channels/AlbumSelect.vue'

import useErrorHandler from '~/composables/useErrorHandler'

import Layout from '~/components/ui/Layout.vue'
import Alert from '~/components/ui/Alert.vue'
import Button from '~/components/ui/Button.vue'
import Loader from '~/components/ui/Loader.vue'
import Spacer from '~/components/ui/Spacer.vue'

interface Events {
  (e: 'status', status: UploadStatus): void
}

interface Props {
  channel?: Channel | null,
  filter: 'podcast' | 'music' | undefined,
}

interface QuotaStatus {
  remaining: number
}

interface UploadStatus {
  totalSize: number
  totalFiles: number
  progress: number
  speed: number
  quotaStatus: QuotaStatus
  uploadedSize: number
  canSubmit: boolean
}

interface UploadedFile extends VueUploadItem {
  _fileObj?: VueUploadItem
  removed: boolean
  metadata: Metadata
}

const emit = defineEmits<Events>()
const props = withDefaults(defineProps<Props>(), {
  channel: null
})

const { t } = useI18n()
const store = useStore()

const errors = ref([] as string[])

const values = reactive<{
  channelUuid: string | null; // Channel UUID
  license: string | null;
  album: string | null;
}>({
  channelUuid: props.channel?.uuid ?? null,
  license: null,
  album: null
})

const files = ref([] as VueUploadItem[])

//
// Channels
//
const availableChannels = ref<Channel[] | null>(null)

/*
          availableChannels>1?  :=1     :=0
          |                               |       |
          v                               v       v
props   select a channel           |       create empty channel
|         |                                     null
v         v                                       |
          channelDropdownId                 v
          |
          v
selectedChannel
|
v
as a model to Album
|
v
albums

*/

// In the channel dropdown, we can select a value
//

const channelDropdownId = ref<Channel['artist']['id'] | null>(null)
const isLoading = ref(false)

const selectedChannel = computed(() => {
  if (props.channel != null) {
    // Deeplink / Preset channel
    return props.channel
  }
  const value = availableChannels.value
  if (value == null) {
    return null
  }
  if (value.length === 0) {
    createEmptyChannel()
    return null
  }
  // Multiple available channels
  return value.length === 1
      ? value[0]
      : value.find(({ artist }) => artist.id === channelDropdownId.value) ?? null
})

const emptyChannelCreateRequest:components['schemas']['ChannelCreateRequest'] = {
  name: store.state.auth.fullUsername,
  username: store.state.auth.username +  "_" + props.filter + "_channel",
  description: null,
  tags: [],
  content_category: props.filter ?? 'music'
}

const createEmptyChannel = async () => {
  try {
    await axios.post(
      'channels/',
      (emptyChannelCreateRequest satisfies operations['create_channel']['requestBody']['content']['application/json'])
    )
  } catch (error) {
    errors.value = (error as BackendError).backendErrors
  }
}

const fetchChannels = async () => {
  isLoading.value = true
  try {
    const response = await axios.get<paths['/api/v2/channels/']['get']['responses']['200']['content']['application/json']>(
      'channels/',
      { params: { scope: 'me' } }
    )

    availableChannels.value = response.data.results.filter(channel =>
      props.filter === undefined
        ? true
        : channel.artist?.content_category === props.filter
    )

  } catch (error) {
    errors.value = (error as BackendError).backendErrors
  }

  isLoading.value = false
}

// Quota and space
//
const quotaStatus = ref()
const fetchQuota = async () => {
  try {
    const response = await axios.get('users/me/')
    quotaStatus.value = response.data.quota_status as QuotaStatus
  } catch (error) {
    errors.value = (error as BackendError).backendErrors
  }
}

const uploadedSize = computed(() => {
  let uploaded = 0

  for (const file of uploadedFiles.value) {
    if (file._fileObj && !file.error) {
      uploaded += (file.size ?? 0) * +(file.progress ?? 0) / 100
    }
  }

  return uploaded
})

const remainingSpace = computed(() => Math.max(
  (quotaStatus.value?.remaining ?? 0) - uploadedSize.value / 1e6,
  0
))

//
// Draft uploads
//
const includeDraftUploads = ref()
const draftUploads = ref([] as Upload[])
whenever(() => values.channelUuid !== null, async () => {
  files.value = []
  draftUploads.value = []

  try {
    const response = await axios.get('uploads', {
      params: { import_status: 'draft', channel: values.channelUuid }
    })

    draftUploads.value = response.data.results as Upload[]
    for (const upload of response.data.results as Upload[]) {
      // @ts-expect-error TODO (wvffle): Resolve type errors when API client is done
      uploadImportData[upload.uuid] = upload.import_metadata ?? {}
    }
  } catch (error) {
    errors.value = (error as BackendError).backendErrors
  }
}, { immediate: true })

//
// Uploading files
//
const upload = ref()
const beforeFileUpload = (newFile: VueUploadItem) => {
  if (!newFile) return
  if (remainingSpace.value < (newFile.size ?? Infinity) / 1e6) {
    newFile.error = 'denied'
  } else {
    newFile.active = true
  }
}

//
// Uploaded files
//
const removed = reactive(new Set<string>())
const uploadedFiles = computed(() => {
  const uploadedFiles = files.value.map(file => {
    const data = {
      ...file,
      _fileObj: file,
      removed: false,
      metadata: {}
    } as UploadedFile

    if (file.response?.uuid) {
      const uuid = file.response.uuid as string
      data.metadata = uploadImportData[uuid] ?? uploadData[uuid]?.import_metadata ?? {} as Metadata
      data.removed = removed.has(uuid)
    }

    return data
  })

  if (includeDraftUploads.value) {
    // We have two different objects: draft uploads (so already uploaded in a previous)
    // session, and files uploaded in the current session
    // so we ensure we have a similar structure for both.
    uploadedFiles.unshift(...draftUploads.value.map(upload => ({
      id: upload.uuid,
      response: upload,
      __filename: null,
      size: upload.size,
      progress: '100.00',
      name: upload.source?.replace('upload://', '') ?? '',
      active: false,
      removed: removed.has(upload.uuid),
      metadata: uploadImportData[upload.uuid] ?? audioMetadata[upload.uuid] ?? upload.import_metadata ?? {}
    } as UploadedFile)))
  }

  return uploadedFiles.filter(file => !file.removed) as UploadedFile[]
})

const uploadedFilesById = computed(() => uploadedFiles.value.reduce((acc: Record<string, VueUploadItem>, file) => {
  acc[file.response?.uuid] = file
  return acc
}, {}))

//
// Metadata
//

const baseImportMetadata = computed(() => ({
  channel: selectedChannel.value?.uuid ?? null,
  import_status: 'draft',
  import_metadata: { license: values.license, album: values.album }
}))

type Metadata = Pick<Track, 'title' | 'position' | 'tags'> & { cover: string | null, description: string }
const uploadImportData = reactive({} as Record<string, Metadata>)
const audioMetadata = reactive({} as Record<string, Record<string, string>>)
const uploadData = reactive({} as Record<string, { import_metadata: Metadata }>)
const patchUpload = async (id: string, data: Record<string, Metadata>) => {
  try {
    const response = await axios.patch(`uploads/${id}/`, data)
    uploadData[id] = response.data
    uploadImportData[id] = response.data.import_metadata
  } catch (error) {
    useErrorHandler(error as Error)
  }
}

const fetchAudioMetadata = async (uuid: string) => {
  const uploadImportDatum = uploadImportData[uuid]

  if (uploadImportDatum == null) {
    return
  }

  delete audioMetadata[uuid]

  const response = await axios.get(`uploads/${uuid}/audio-file-metadata/`)
  audioMetadata[uuid] = response.data

  const uploadedFile = uploadedFilesById.value[uuid]
  if (uploadedFile?.response?.import_metadata.title === uploadedFile?._fileObj?.name.replace(/\.[^/.]+$/, '') && response.data.title) {
    // Replace existing title deduced from file by the one in audio file metadata, if any
    uploadImportDatum.title = response.data.title
  }

  for (const key of ['title', 'position', 'tags'] as const) {
    if (uploadImportDatum[key] === undefined) {
      // uploadImportData[uuid][key] = response.data[key] as never
    }
  }

  if (uploadImportDatum.description === undefined) {
    uploadImportDatum.description = (response.data.description ?? {}).text
  }

  await patchUpload(uuid, { import_metadata: uploadImportDatum })
}

watchEffect(async () => {
  for (const file of files.value) {
    if (file.response?.uuid && audioMetadata[file.response.uuid] === undefined) {
      uploadData[file.response.uuid] = file.response as { import_metadata: Metadata }
      uploadImportData[file.response.uuid] = file.response.import_metadata
      fetchAudioMetadata(file.response.uuid)
    }
  }
})

//
// Select upload
//
const selectedUploadId = ref()
const selectedUpload = computed(() => {
  if (!selectedUploadId.value) return null

  const selected = uploadedFiles.value.find(file => file.response?.uuid === selectedUploadId.value)
  if (!selected) return null

  return {
    ...(selected.response ?? {}),
    _fileObj: selected._fileObj
  } as Upload & { _fileObj?: VueUploadItem }
})

//
// Actions
//
const remove = async (file: VueUploadItem) => {
  if (file.response?.uuid) {
    removed.add(file.response.uuid)
    try {
      await axios.delete(`uploads/${file.response.uuid}/`)
    } catch (error) {
      useErrorHandler(error as Error)
    }
  } else {
    upload.value.remove(file)
  }
}

const retry = async (file: VueUploadItem) => {
  upload.value.update(file, { error: '', progress: '0.00' })
  upload.value.active = true
}

//
// Init
//
fetchChannels()
fetchQuota()

watch(selectedUploadId, async (_, from) => {
  const uploadImportDatum = uploadImportData[from]
  if (from != null && uploadImportDatum != null) {
    await patchUpload(from, { import_metadata: uploadImportDatum })
  }
})

//
// Status
//

watchEffect(() => {
  const uploaded = uploadedFiles.value
  const totalSize = uploaded.reduce(
    (acc, uploadedFile) => !uploadedFile.error
      ? acc + (uploadedFile.size ?? 0)
      : acc,
    0
  )

  const activeFile = files.value.find(file => file.active)

  emit('status', {
    totalSize,
    totalFiles: uploaded.length,
    progress: Math.floor(uploadedSize.value / totalSize * 100),
    speed: activeFile?.speed ?? 0,
    quotaStatus: quotaStatus.value,
    uploadedSize: uploadedSize.value,
    canSubmit: activeFile !== undefined && uploadedFiles.value.length > 0
  })
})

const labels = computed(() => ({
  editTitle: t('components.channels.UploadForm.button.edit')
}))

const publish = async () => {
  isLoading.value = true

  errors.value = []
  try {
    // Post list of uuids of uploadedFiles to axios action:publish

    /* { import_status: components["schemas"]["ImportStatusEnum"];
    audio_file: string;} */

    await axios.post<paths['/api/v2/uploads/action/']['post']['responses']['200']['content']['application/json']>('uploads/action/', {
      action: 'publish',
      objects: uploadedFiles.value.map((file) => file.response?.uuid)
    })

    // Tell the store that the uploaded files are pending import
    store.commit('channels/publish', {
      uploads: uploadedFiles.value.map((file) => ({ ...file.response, import_status: 'pending' })),
      channel: selectedChannel.value
    })
  } catch (error) {
    // TODO: Use inferred error type instead of typecasting
    errors.value = (error as BackendError).backendErrors
  }

  isLoading.value = false
}

defineExpose({
  publish
})
</script>

<template>
  <Layout
    form
    gap-8
    :class="['ui', { loading: isLoading }, 'form component-file-upload']"
    @submit.stop.prevent
  >
    <!-- Error message -->
    <Alert
      v-if="errors.length > 0"
      red
    >
      <h4 class="header">
        {{ t('components.channels.UploadForm.header.error') }}
      </h4>
      <ul class="list">
        <li
          v-for="(error, key) in errors"
          :key="key"
        >
          {{ error }}
        </li>
      </ul>
    </Alert>

    <!-- Select Album and License -->

    <div :class="['ui', 'required', 'field']">
      <label
        v-if="availableChannels !== null && availableChannels.length === 1"
      >
        {{ `${t('components.channels.UploadForm.label.channel')}: ${selectedChannel?.artist.name}` }}
      </label>
      <label
        v-else
        for="channel-dropdown"
      >
        {{ t('components.channels.UploadForm.label.channel') }}
      </label>
      <select
        v-if="availableChannels !== null && availableChannels.length > 1"
        id="channel-dropdown"
        v-model="channelDropdownId"
        class="dropdown"
      >
        <option
          v-for="availableChannel in availableChannels"
          :key="availableChannel.artist.id"
          :value="availableChannel.artist.id"
        >
          {{ availableChannel.artist.name }}
        </option>
      </select>
    </div>
    <album-select
      v-if="selectedChannel !== null"
      v-model.number="values.album"
      :channel="selectedChannel"
    />
    <div>
      <license-select
        v-if="values.license !== null"
        v-model="values.license"
        :class="['ui', 'field']"
      />
      <div class="content">
        <p>
          <i class="copyright icon" />
          {{ t('components.channels.UploadForm.help.license') }}
        </p>
      </div>
    </div>

    <!-- Files to upload -->
    <template v-if="remainingSpace === 0">
      <Alert
        red
      >
        <i class="bi bi-exclamation-triangle" />
        {{ t('components.channels.UploadForm.warning.quota') }}
      </Alert>
    </template>
    <template v-else>
      <Alert
        v-if="draftUploads?.length > 0 && includeDraftUploads === undefined"
        blue
      >
        <p>
          <i class="bi bi-circle-clockwise" />
          {{ t('components.channels.UploadForm.message.pending') }}
        </p>
        <Button
          @click.stop.prevent="includeDraftUploads = false"
        >
          {{ t('components.channels.UploadForm.button.ignore') }}
        </Button>
        <Button
          @click.stop.prevent="includeDraftUploads = true"
        >
          {{ t('components.channels.UploadForm.button.resume') }}
        </Button>
      </Alert>
      <Alert
        v-if="uploadedFiles.length > 0"
        v-bind="{[ uploadedFiles.some(file=>file.error) ? 'red' : 'green' ]:true}"
      >
        <div
          v-for="file in uploadedFiles"
          :key="file.id"
          class="channel-file"
        >
          <div class="content">
            <Button
              v-if="file.response?.uuid"
              icon="bi-pencil-fill"
              class="ui basic icon button"
              :title="labels.editTitle"
              @click.stop.prevent="selectedUploadId = file.response?.uuid"
            />
            <div
              v-if="file.error"
              class="ui basic danger icon label"
              :title="file.error.toString()"
              @click.stop.prevent="selectedUploadId = file.response?.uuid"
            >
              <i class="bi bi-exclamation-triangle-fill" />
            </div>
            <Loader v-else-if="file.active && !file.response" />
          </div>
          <Layout
            stack
            gap-8
          >
            <span v-if="file.error">
              {{ file.error?.toString() }}
            </span>
            <h4 class="ui header">
              <template v-if="file.metadata.title">
                {{ file.metadata.title }}
              </template>
              <template v-else>
                {{ file.name }}
              </template>
              <div class="sub header">
                <template v-if="file.response?.uuid">
                  {{ humanSize(file.size ?? 0) }}
                  <template v-if="file.response.duration">
                    <span class="middle middledot symbol" />
                    <human-duration :duration="file.response.duration" />
                  </template>
                </template>
                <template v-else>
                  <span v-if="file.active">
                    {{ t('components.channels.UploadForm.status.uploading') }}
                  </span>
                  <span v-else-if="file.error">
                    {{ t('components.channels.UploadForm.status.errored') }}
                  </span>
                  <span v-else>
                    {{ t('components.channels.UploadForm.status.pending') }}
                  </span>
                  <span class="middle middledot symbol" />
                  {{ humanSize(file.size ?? 0) }}
                  <span class="middle middledot symbol" />
                  {{ parseFloat(file.progress ?? '0') }}
                  <span class="percent symbol" />
                </template>
                <span class="middle middledot symbol" />
                <a @click.stop.prevent="remove(file)">
                  {{ t('components.channels.UploadForm.button.remove') }}
                </a>
                <template v-if="file.error">
                  <span class="middle middledot symbol" />
                  <a @click.stop.prevent="retry(file)">
                    {{ t('components.channels.UploadForm.button.retry') }}
                  </a>
                </template>
              </div>
            </h4>
          </Layout>
        </div>
      </Alert>
    </template>
    <upload-metadata-form
      v-if="selectedUpload"
      v-model:values="uploadImportData[selectedUploadId]"
      :upload="selectedUpload"
    />
    <Alert
      blue
      class="ui message"
    >
      <Layout
        flex
        gap-8
      >
        <i class="bi bi-info-circle-fill" />
        {{ t('components.channels.UploadForm.description.extensions', {extensions: store.state.ui.supportedExtensions.join(', ')}) }}
      </Layout>
    </Alert>
    <FileUploadWidget
      v-if="selectedChannel && selectedChannel.uuid"
      ref="upload"
      v-model="files"
      :class="['ui', 'button', 'channels']"
      :channel="selectedChannel.uuid"
      :data="baseImportMetadata"
      @input-file="beforeFileUpload"
    >
      <div>
        <i class="bi bi-upload" />&nbsp;
        {{ t('components.channels.UploadForm.message.dragAndDrop') }}
      </div>
      <div class="ui very small divider" />
      <Button
        primary
        icon="bi-folder2-open"
      >
        {{ t('components.channels.UploadForm.label.openBrowser') }}
      </Button>
      <Spacer
        class="divider"
        :size="32"
      />
    </FileUploadWidget>
  </Layout>
</template>
