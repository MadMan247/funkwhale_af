<script setup lang="ts">
import type { Playlist } from '~/types'

import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'
import axios from 'axios'

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

const exportUrl = computed(() => store.getters['instance/absoluteUrl'](`/api/v2/playlists/${props.playlist.id}`))
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

</script>
<template>
  <span>
    <button
      v-dropdown="{direction: 'downward'}"
      class="ui floating dropdown circular icon basic button"
      :title="labels.more"
    >
      <i class="ellipsis vertical icon" />
      <div class="menu">
        <div
          role="button"
          class="basic item"
          :title="t('components.playlists.PlaylistDropdown.button.export.description')"
          @click="exportPlaylist"
        >
          <i class="upload icon" />
          {{ labels.export }}
        </div>
        <div
          v-if="$store.state.auth.profile && playlist.user.id === $store.state.auth.profile.id"
          role="button"
          class="basic item"
          :title="t('components.playlists.PlaylistDropdown.button.import.description')"
          @click="triggerFileInput"
        >
          <i class="download icon" />
          {{ labels.import }}
        </div>
      </div>
    </button>

    <!-- Hidden file input, triggered by the button click -->
    <input
      ref="fileInputRef"
      type="file"
      style="display: none"
      @change="patchPlaylist"
    >
  </span>
</template>
