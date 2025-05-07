<script setup lang="ts">
import type { Playlist } from '~/types'

import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'
import { useRouter } from 'vue-router'
import axios from 'axios'

import useErrorHandler from '~/composables/useErrorHandler'
import OptionsButton from '~/components/ui/button/Options.vue'
import EmbedWizard from '~/components/audio/EmbedWizard.vue'
import Modal from '~/components/ui/Modal.vue'
import Alert from '~/components/ui/Alert.vue'
import Button from '~/components/ui/Button.vue'
import Popover from '~/components/ui/Popover.vue'
import PopoverItem from '~/components/ui/popover/PopoverItem.vue'

interface Events {
  (e: 'import'): void
  (e: 'export'): void
}

interface Props {
  playlist: Playlist
}

const emit = defineEmits<Events>()
const props = defineProps<Props>()
const store = useStore()
const currentDate = new Date()
const formattedDate = currentDate.toISOString().split('T')[0]

const { t } = useI18n()

const labels = computed(() => ({
  import: t('components.playlists.PlaylistDropdown.button.import.header'),
  export: t('components.playlists.PlaylistDropdown.button.export.header'),
  more: t('components.playlists.PlaylistDropdown.more')

}))

const exportUrl = computed(() => store.getters['instance/absoluteUrl'](`/api/v2/playlists/${props.playlist.uuid}`))
const exportPlaylist = async () => {
  const url = exportUrl.value
  const authToken = store.state.auth.oauth.accessToken

  const headers = {
    'Content-Type': 'application/octet-stream',
    Accept: 'application/octet-stream',
    Authorization: `Bearer ${authToken}`
  }

  const response = await axios.get(url, { headers })
  const blob = new Blob([response.data])
  const downloadUrl = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = downloadUrl
  a.download = `${props.playlist.name}_${formattedDate}.xspf`
  a.click()
  a.remove()
}

const fileInputRef = ref<HTMLInputElement | null>(null)

const router = useRouter()

const deletePlaylist = async () => {
  try {
    await axios.delete(`playlists/${props.playlist.uuid}/`)
    store.dispatch('playlists/fetchOwn')
    await router.push({ path: '/library' })  // <-- await instead of return
  } catch (error) {
    useErrorHandler(error as Error)
  }
}

const patchPlaylist = async () => {
  const url = exportUrl.value

  if (!fileInputRef.value || !fileInputRef.value.files || fileInputRef.value.files.length === 0) {
    return
  }

  const file = fileInputRef.value.files[0]

  const headers: Record<string, string> = {
    'Content-Type': 'application/octet-stream'
  }

  await axios.patch(url, file, { headers })
  emit('import')
}

// Function to trigger file input when clicking import
const triggerFileInput = () => {
  fileInputRef.value?.click()
}

const open = ref(false)
const showEmbedModal = ref(false)
const showDeleteModal = ref(false)
</script>
<template>
  <span>
    <Popover v-model="open">
      <template #default="{ toggleOpen }">
        <OptionsButton
          is-square-small
          @click="toggleOpen"
        />
      </template>
      <template #items>
        <PopoverItem
          v-if="playlist.privacy_level === 'everyone' && playlist.is_playable"
          icon="bi-code-slash"
          @click="showEmbedModal = !showEmbedModal"
        >
          {{ t('views.playlists.Detail.button.embed') }}
        </PopoverItem>
        <PopoverItem
          v-if="store.state.auth.profile && playlist.actor.full_username === store.state.auth.fullUsername"
          destructive
          icon="bi-trash"
          :action="deletePlaylist"
          @click="showDeleteModal = !showDeleteModal"
        >
          {{ t('views.playlists.Detail.button.delete') }}
        </PopoverItem>
        <PopoverItem
          icon="bi-download"
          @click="exportPlaylist"
        >
          {{ labels.export }}
        </PopoverItem>

        <PopoverItem
          v-if="store.state.auth.authenticated && playlist.actor.full_username === store.state.auth.fullUsername"
          icon="bi-upload"
          @click="triggerFileInput"
        >
          {{ labels.import }}
        </PopoverItem>
      </template>
    </Popover>

    <!-- Hidden file input, triggered by the button click -->
    <input
      ref="fileInputRef"
      type="file"
      style="display: none"
      @change="patchPlaylist"
    >
  </span>

  <Modal
    v-if="playlist.privacy_level === 'everyone' && playlist.is_playable"
    v-model="showEmbedModal"
    title="t('views.playlists.Detail.modal.embed.header')"
  >
    <div class="scrolling content">
      <div class="description">
        <embed-wizard
          :uuid="playlist.uuid"
          type="playlist"
        />
      </div>
    </div>
    <template #actions>
      <Button variant="outline">
        {{ t('views.playlists.Detail.button.cancel') }}
      </Button>
    </template>
  </Modal>

  <Modal
    v-model="showDeleteModal"
    destructive
    :title="t('views.playlists.Detail.modal.delete.header')"
  >
    <template #alert>
      <Alert red>
        <p>
          {{ t('views.playlists.Detail.modal.delete.content.warning') }}
        </p>
      </Alert>
    </template>
    <template #actions>
      <Button @click="showDeleteModal = false">
        {{ t('views.playlists.Detail.button.cancel') }}
      </Button>
      <Button
        destructive
        @click="deletePlaylist"
      >
        {{ t('views.playlists.Detail.button.confirm') }}
      </Button>
    </template>
  </Modal>
</template>
