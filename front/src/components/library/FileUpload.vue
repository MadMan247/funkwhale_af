<script setup lang="ts">
import type { BackendError, FileSystem, Library, PrivacyLevelEnum } from '~/types'
import type { VueUploadItem } from 'vue-upload-component'
import type { paths } from '~/generated/types'

import { computed, ref, reactive, watch, nextTick } from 'vue'
import { useEventListener, useIntervalFn } from '@vueuse/core'
import { humanSize, truncate } from '~/utils/filters'
import { useI18n } from 'vue-i18n'
import { sortBy } from 'lodash-es'
import { useStore } from '~/store'

import axios from 'axios'

import LibraryFilesTable from '~/views/content/libraries/FilesTable.vue'
import FileUploadWidget from './FileUploadWidget.vue'
import FsBrowser from './FsBrowser.vue'
import FsLogs from './FsLogs.vue'

import useWebSocketHandler from '~/composables/useWebSocketHandler'
import updateQueryString from '~/composables/updateQueryString'
import useErrorHandler from '~/composables/useErrorHandler'
import useSharedLabels from '~/composables/locale/useSharedLabels'

import Alert from '~/components/ui/Alert.vue'
import Button from '~/components/ui/Button.vue'
import Slider from '~/components/ui/Slider.vue'
import Section from '~/components/ui/Section.vue'
import Pill from '~/components/ui/Pill.vue'
import Layout from '~/components/ui/Layout.vue'
import Table from '~/components/ui/Table.vue'

interface Events {
  (e: 'uploads-finished', delta: number): void
}

interface Props {
  defaultImportReference?: string
}

const emit = defineEmits<Events>()
const props = withDefaults(defineProps<Props>(), {
  defaultImportReference: ''
})

const { t } = useI18n()
const store = useStore()

const upload = ref()
const supportedExtensions = computed(() => store.state.ui.supportedExtensions)

const labels = computed(() => ({
  tooltips: {
    denied: t('components.library.FileUpload.tooltip.denied'),
    server: t('components.library.FileUpload.tooltip.size'),
    network: t('components.library.FileUpload.tooltip.network'),
    timeout: t('components.library.FileUpload.tooltip.timeout'),
    retry: t('components.library.FileUpload.tooltip.retry'),
    extension: t(
      'components.library.FileUpload.tooltip.extension',
      { extensions: supportedExtensions.value.join(', ') }
    )
  } as Record<string, string>
}))

const uploads = reactive({
  pending: 0,
  finished: 0,
  skipped: 0,
  errored: 0,
  objects: {} as Record<string, any>
})

// Select corresponding user-library when slider changes

const sharedLabels = useSharedLabels()

const options = {
  me: sharedLabels.fields.privacy_level.choices.me,
  instance: sharedLabels.fields.privacy_level.choices.instance,
  followers: sharedLabels.fields.privacy_level.choices.followers,
  everyone: sharedLabels.fields.privacy_level.choices.everyone
} as const satisfies Record<PrivacyLevelEnum, string>

const privacyLevel = defineModel<PrivacyLevelEnum | undefined>({ required: true })

const library = ref<Library>()

// New implementation with `useClient`:

// watch(privacyLevel, (newValue) =>
//   get({
//       privacy_level: newValue,
//       scope: 'me'
//   })
//   .then((data) =>
//     library.value = data?.results.find(({name}) => name === privacyLevel.value)
//   ),
//   { immediate: true }
// )

// Old implementation:

watch(privacyLevel, async (newValue) => {
  try {
    const response = await axios.get<paths['/api/v2/libraries/']['get']['responses']['200']['content']['application/json']>('libraries/', {
      params: {
        privacy_level: newValue,
        scope: 'me'
      }
    })

    library.value = response.data.results.find(({ name }) => name === newValue)
  } catch (error) {
    useErrorHandler(error as Error)
  }
}, { immediate: true })

//
// File counts
//
const files = ref([] as VueUploadItem[])
const processedFilesCount = computed(() => uploads.skipped + uploads.errored + uploads.finished)
const uploadedFilesCount = computed(() => files.value.filter(file => file.success).length)
const retryableFiles = computed(() => files.value.filter(file => file.error))
const erroredFilesCount = computed(() => retryableFiles.value.length)
const processableFiles = computed(() => uploads.pending
  + uploads.skipped
  + uploads.errored
  + uploads.finished
  + uploadedFilesCount.value
)

//
// Uploading
//
const importReference = ref(props.defaultImportReference || new Date().toISOString())
history.replaceState(history.state, '', updateQueryString(location.href, 'import', importReference.value))
const uploadData = computed(() => ({
  library: library.value?.uuid,
  import_reference: importReference
}))

watch(() => uploads.finished, (newValue, oldValue) => {
  if (newValue > oldValue) {
    emit('uploads-finished', newValue - oldValue)
  }
})

//
// Upload status
//
const fetchStatus = async () => {
  for (const status of Object.keys(uploads)) {
    if (status === 'objects') continue

    try {
      const response = await axios.get('uploads/', {
        params: {
          import_reference: importReference.value,
          import_status: status,
          page_size: 1,
          library: library.value?.uuid
        }
      })

      uploads[status as keyof typeof uploads] = response.data.count
    } catch (error) {
      useErrorHandler(error as Error)
    }
  }
}

fetchStatus()

const needsRefresh = ref(false)
useWebSocketHandler('import.status_updated', async (event) => {
  if (event.upload.import_reference !== importReference.value) {
    return
  }

  // TODO (wvffle): Why?
  await nextTick()

  if (event.new_status === 'errored') {
    for (const file of files.value) {
      if (file.response?.uuid === event.upload.uuid) {
        file.error = event.new_status
        break
      }
    }
  }

  uploads[event.old_status] -= 1
  uploads[event.new_status] += 1
  uploads.objects[event.upload.uuid] = event.upload
  needsRefresh.value = true
})

//
// Files
//
const sortedFiles = computed(() => {
  const filesToSort = files.value

  return [
    ...sortBy(filesToSort.filter(file => file.errored), ['name']),
    ...sortBy(filesToSort.filter(file => !file.errored && !file.success), ['name']),
    ...sortBy(filesToSort.filter(file => file.success), ['name'])
  ]
})

const hasActiveUploads = computed(() => files.value.some(file => file.active))

//
// Quota status
//
const quotaStatus = ref()

const uploadedSize = computed(() => {
  let uploaded = 0

  for (const file of files.value) {
    if (!file.error) {
      uploaded += (file.size ?? 0) * +(file.progress ?? 0) / 100
    }
  }

  return uploaded
})

const remainingSpace = computed(() => Math.max(
  (quotaStatus.value?.remaining ?? 0) - uploadedSize.value / 1e6,
  0
))

watch(remainingSpace, space => {
  if (space <= 0) {
    upload.value.active = false
  }
})

const isLoadingQuota = ref(false)
const fetchQuota = async () => {
  isLoadingQuota.value = true

  try {
    const response = await axios.get('users/me/')
    quotaStatus.value = response.data.quota_status
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoadingQuota.value = false
}

fetchQuota()

//
// Filesystem
//
const fsPath = ref([])
const fsStatus = ref({
  import: {
    status: 'pending'
  }
} as FileSystem)
watch(fsPath, () => fetchFilesystem(true))

const { pause, resume } = useIntervalFn(() => {
  fetchFilesystem(false)
}, 5000, { immediate: false })

const isLoadingFs = ref(false)
const fetchFilesystem = async (updateLoading: boolean) => {
  if (updateLoading) isLoadingFs.value = true
  pause()

  try {
    const response = await axios.get('libraries/fs-import', { params: { path: fsPath.value.join('/') } })
    fsStatus.value = response.data
  } catch (error) {
    useErrorHandler(error as Error)
  }

  if (updateLoading) isLoadingFs.value = false
  if (store.state.auth.availablePermissions.library) resume()
}

if (store.state.auth.availablePermissions.library) {
  fetchFilesystem(true)
}

const fsErrors = ref([] as string[])
const importFs = async () => {
  isLoadingFs.value = true

  try {
    const response = await axios.post('libraries/fs-import', {
      path: fsPath.value.join('/'),
      library: library.value?.uuid,
      import_reference: importReference.value
    })

    fsStatus.value = response.data
  } catch (error) {
    fsErrors.value = (error as BackendError).backendErrors
  }

  isLoadingFs.value = false
}

// TODO (wvffle): Maybe use AbortController?
const cancelFsScan = async () => {
  try {
    await axios.delete('libraries/fs-import')
    fetchFilesystem(false)
  } catch (error) {
    useErrorHandler(error as Error)
  }
}

const inputFile = (newFile: VueUploadItem) => {
  if (!newFile) return

  if (remainingSpace.value < (newFile.size ?? Infinity) / 1e6) {
    newFile.error = 'denied'
  } else {
    newFile.active = true
  }
}

// NOTE: For some weird reason typescript thinks that xhr field is not compatible with the same type
const retry = (files: Omit<VueUploadItem, 'xhr'>[]) => {
  for (const file of files) {
    upload.value.update(file, { error: '', progress: '0.00' })
  }

  upload.value.active = true
}

//
// Before unload
//
useEventListener(window, 'beforeunload', (event) => {
  if (!hasActiveUploads.value) return null
  event.preventDefault()
  return (event.returnValue = t('components.library.FileUpload.message.listener'))
})

// collapse section
const isServerDisclosureOpen = ref(false)
</script>

<template>
  <div :class="{ loading: isLoadingQuota }">
    <div
      :class="['ui', { red: remainingSpace === 0 }, { warning: remainingSpace > 0 && remainingSpace <= 50 }, 'small', 'statistic']"
    >
      <div class="label">
        {{ t('components.library.FileUpload.label.remainingSpace') }}
      </div>
      <div class="value">
        {{ humanSize(remainingSpace * 1000 * 1000) }}
      </div>
    </div>
  </div>
  <Slider
    v-model="privacyLevel"
    :options="options"
    :label="t('components.manage.library.UploadsTable.label.visibility')"
  />

  <Alert blue>
    <p>
      {{ t('components.library.FileUpload.message.local.message') }}
    </p>
    <ul>
      <li v-if="library?.privacy_level != 'me'">
        {{ t('components.library.FileUpload.message.local.copyright') }}
      </li>
      <li>
        {{ t('components.library.FileUpload.message.local.tag') }}&nbsp;
        <a
          href="http://picard.musicbrainz.org/"
          target="_blank"
        >{{ t('components.library.FileUpload.link.picard')
        }}</a>
      </li>
      <li>
        {{ t('components.library.FileUpload.message.local.format') }}
      </li>
    </ul>
  </Alert>

  <file-upload-widget
    ref="upload"
    v-model="files"
    :class="$style.uploader"
    :data="uploadData"
    @input-file="inputFile"
  >
    <Button
      primary
      icon="bi bi-upload"
    >
      {{ t('components.library.FileUpload.label.uploadWidget') }}
    </Button>
    <p>
      {{ t('components.library.FileUpload.label.extensions', { extensions: supportedExtensions.join(', ') }) }}
    </p>
  </file-upload-widget>

  <!-- Show how many files are uploading and processing -->

  <Layout
    v-if="files.length > 0"
    flex
  >
    <Layout
      flex
      gap-8
    >
      <label>{{ t('components.library.FileUpload.link.uploading') }}</label>
      <Pill
        v-bind="{
          'green': erroredFilesCount === 0,
          'red': erroredFilesCount > 0,
          'yellow': files.length > uploadedFilesCount + erroredFilesCount
        }"
      >
        {{ t('components.library.FileUpload.table.upload.progressNum', {
          current: uploadedFilesCount + erroredFilesCount,
          total: files.length
        }) }}
      </Pill>
    </Layout>
    <Layout
      flex
      gap-8
    >
      <label>{{ t('components.library.FileUpload.link.processing') }}</label>
      <Pill>
        {{ t('components.library.FileUpload.table.upload.progressNum', {
          current: processedFilesCount, total:
            processableFiles
        }) }}
      </Pill>
    </Layout>
  </Layout>

  <Alert
    v-if="fsErrors.length > 0"
    red
  >
    <h3 class="header">
      {{ t('components.library.FileUpload.header.failure') }}
    </h3>
    <ul class="list">
      <li
        v-for="(error, key) in fsErrors"
        :key="key"
      >
        {{ error }}
      </li>
    </ul>
  </Alert>

  <!-- Show list of processed files -->

  <library-files-table
    :needs-refresh="needsRefresh"
    ordering-config-name="library.detail.upload"
    :filters="{ import_reference: importReference }"
    :custom-objects="Object.values(uploads.objects)"
    @fetch-start="needsRefresh = false"
  />

  <!-- Edit the metadata of uploaded files -->

  <Table
    v-if="files.length > 0"
    :class="$style.table"
    :grid-template-columns="['1fr', 'auto', 'auto', 'auto']"
  >
    <template #header>
      <b class="ten wide">
        {{ t('components.library.FileUpload.table.upload.header.filename') }}
      </b>
      <b>
        {{ t('components.library.FileUpload.table.upload.header.size') }}
      </b>
      <b>
        {{ t('components.library.FileUpload.table.upload.header.status') }}
      </b>
      <b>
        {{ t('components.library.FileUpload.table.upload.header.actions') }}
      </b>
    </template>

    <!-- Retry row -->
    <template v-if="retryableFiles.length > 1">
      <b />
      <b />
      <b />
      <b>
        <Button
          auto
          primary
          @click.prevent="retry(retryableFiles)"
        >
          {{ t('components.library.FileUpload.button.retry') }}
        </Button>
      </b>
    </template>

    <!-- Rows for each file -->
    <template
      v-for="file in sortedFiles"
      :key="file.id"
    >
      <b :title="file.name">
        {{ truncate(file.name ?? '', 60) }}
      </b>
      <b>{{ humanSize(file.size ?? 0) }}</b>
      <b>
        <span
          v-if="typeof file.error === 'string' && file.error"
          class="ui tooltip"
          :data-tooltip="labels.tooltips[file.error]"
        >
          <span class="ui danger icon label">
            <i class="bi bi-question-circle-fill" /> {{ file.error }}
          </span>
        </span>
        <span
          v-else-if="file.success"
          class="ui success label"
        >
          <span key="1">
            {{ t('components.library.FileUpload.table.upload.status.uploaded') }}
          </span>
        </span>
        <span
          v-else-if="file.active"
          class="ui warning label"
        >
          <span key="2">
            {{ t('components.library.FileUpload.table.upload.status.uploading') }}
          </span>

          {{ t('components.library.FileUpload.table.upload.progress', { percent: parseFloat(file.progress ?? '0.00') })
          }}
        </span>
        <span
          v-else
          class="ui label"
        >
          <span key="3">
            {{ t('components.library.FileUpload.table.upload.status.pending') }}
          </span>
        </span>
      </b>
      <b>
        <template v-if="file.error">
          <Button
            v-if="retryableFiles.includes(file)"
            square
            secondary
            :title="labels.tooltips.retry"
            icon="bi-arrow-clockwise"
            @click.prevent="retry([file])"
          />
        </template>
        <template v-else-if="!file.success">
          <Button
            square-small
            destructive
            icon="bi-trash-fill"
            @click.prevent="upload.remove(file)"
          />
        </template>
      </b>
    </template>
  </Table>

  <!-- Progressive disclosure: Import from server -->

  <Section
    :h2="t('components.library.FileUpload.header.server')"
    align-left
    v-bind="isServerDisclosureOpen
      ? { collapse: () => { isServerDisclosureOpen = false } }
      : { expand: () => { isServerDisclosureOpen = true } }
    "
  >
    <div style="grid-column: 1 / -1">
      <fs-browser
        v-model="fsPath"
        :loading="isLoadingFs"
        :data="fsStatus"
        @import="importFs"
      />
      <template v-if="fsStatus && fsStatus.import">
        <h3 class="ui header">
          {{ t('components.library.FileUpload.header.status') }}
        </h3>
        <p v-if="fsStatus.import.reference !== importReference">
          {{ t('components.library.FileUpload.description.previousImport') }}
        </p>
        <p v-else>
          {{ t('components.library.FileUpload.description.import') }}
        </p>

        <Button
          v-if="fsStatus.import.status === 'started' || fsStatus.import.status === 'pending'"
          secondary
          @click="cancelFsScan"
        >
          {{ t('components.library.FileUpload.button.cancel') }}
        </Button>
        <fs-logs :data="fsStatus.import" />
      </template>
    </div>
  </Section>
</template>

<style module lang="scss">
.uploader {
  padding: 32px;
  border-radius: var(--fw-border-radius);
  border: 2px dashed var(--border-color);
}

.table {
  b {
    padding: 0 6px;
  }
}
</style>
