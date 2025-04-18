<script setup lang="ts">
import { computed, ref, reactive } from 'vue'
import { useUploadsStore } from '~/ui/stores/upload'
import { bytesToHumanSize } from '~/ui/composables/bytes'
import { useRouter } from 'vue-router'
import { useStore } from '~/store'
import { useI18n } from 'vue-i18n'
import UploadList from '~/ui/components/UploadList.vue'
import Alert from '~/components/ui/Alert.vue'
import Button from '~/components/ui/Button.vue'
import Modal from '~/components/ui/Modal.vue'
import Input from '~/components/ui/Input.vue'

// TODO: Delete this file once all upload functionality is moved to the new UI.

const { t } = useI18n()

const uploads = useUploadsStore()

const libraryOpen = computed({
  get: () => !!uploads.currentUploadGroup,
  set: (value) => {
    if (!value) {
      uploads.currentUploadGroup = undefined
    }
  }
})

// Server import
const serverPath = ref('/srv/funkwhale/data/music')

// Upload
const queue = computed(() => {
  return uploads.currentUploadGroup?.queue ?? []
})

const combinedFileSize = computed(() => bytesToHumanSize(
  queue.value.reduce((acc, { file }) => acc + file.size, 0)
))

// Actions

// TODO: Is this needed?
// const processFiles = (fileList: FileList) => {
//   if (!uploads.currentUploadGroup) return

//   for (const file of fileList) {
//     uploads.currentUploadGroup.queueUpload(file)
//   }
// }

const router = useRouter()
const cancel = () => {
  libraryOpen.value = false
  uploads.currentUploadGroup?.cancel()
  uploads.currentUploadGroup = undefined

  if (uploads.queue.length > 0) {
    router.push('/upload/running')
  }
}

const continueInBackground = () => {
  libraryOpen.value = false
  uploads.currentUploadGroup = undefined
  router.push('/upload/running')
}

// TODO (whole file): Delete this file, please.

// Sorting
const sortItems = reactive([
  { label: 'Upload time', value: 'upload-time' },
  { label: 'Upload time 2', value: 'upload-time-2' },
  { label: 'Upload time 3', value: 'upload-time-3' }
])
const currentSort = ref(sortItems[0])

const store = useStore()

// Filtering
const filterItems = reactive([
  { label: 'All', value: 'all' }
])
const currentFilter = ref(filterItems[0])

const modalName = 'upload'

const isOpen = computed({
  get () {
    return store.state.ui.modalsOpen.has(modalName)
  },
  set (value) {
    store.commit('ui/setModal', [modalName, value])
  }
})
</script>

<template>
  <!-- eslint-disable @intlify/vue-i18n/no-raw-text -->
  <Modal
    v-model="isOpen"
    title="Upload..."
  >
    <template #alert>
      <Alert yellow>
        {{ `${t('components.library.FileUpload.message.local.tag')}
        ${t('components.library.FileUpload.link.picard')}` }}
      </Alert>
    </template>

    <!-- TODO: Use a file input. We haven't implemented this yet.
    We could say v-model can be of type `string | number | File | File[]`
    and then implement this functionality. -->
    <!-- v-model="processFiles" -->
    <!-- @vue-ignore -->
    <Input
      type="file"
      :accept="['.flac', '.ogg', '.opus', '.mp3', '.aac', '.aif', '.aiff', '.m4a'].join(', ')"
      multiple
      auto-reset
    />

    <!-- Upload path -->
    <div v-if="queue.length > 0">
      <div class="list-header">
        <div class="file-count">
          {{ queue.length }} files, {{ combinedFileSize }}
        </div>

        <FwSelect
          v-model="currentFilter"
          icon="bi:filter"
          :items="filterItems"
        />
        <FwSelect
          v-model="currentSort"
          icon="bi:sort-down"
          :items="sortItems"
        />
      </div>

      <UploadList :uploads="queue" />
    </div>

    <!-- Import path -->
    <template v-else>
      <label>Import from server directory</label>
      <div class="flex items-center">
        <FwInput
          v-model="serverPath"
          class="w-full mr-4"
        />
        <Button color="secondary">
          Import
        </Button>
      </div>
    </template>

    <template #actions>
      <Button
        color="secondary"
        @click="cancel"
      >
        Cancel
      </Button>
      <Button @click="continueInBackground">
        {{ uploads.queue.length ? 'Continue in background' : 'Save and close' }}
        //TODO: Translations
      </Button>
    </template>
  </Modal>
  <!-- eslint-enable @intlify/vue-i18n/no-raw-text -->
</template>

<style scoped lang="scss">
.list-header {
  display: flex;
  align-items: center;
  margin: 2rem 0 1rem;

  > .file-count {
    margin-right: auto;
    color: var(--fw-gray-600);
    font-weight: 900;
    font-size: 0.875rem;
  }
}

.flex:not(.flex-col) {
  .funkwhale.button {
    &:first-child {
      margin-left: 0;
    }

    &:last-child {
      margin-right: 0;
    }
  }
}
</style>
