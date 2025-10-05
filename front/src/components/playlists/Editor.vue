<script setup lang="ts">
import { generateTrackCreditString } from '~/utils/utils'

import type { Playlist, PlaylistTrack, BackendError, APIErrorResponse } from '~/types'

import { useI18n } from 'vue-i18n'
import { useVModels } from '@vueuse/core'
import { computed, ref, onMounted } from 'vue'

import { useQueue } from '~/composables/audio/queue'
import { useStore } from '~/store'

import draggable from 'vuedraggable'
import axios from 'axios'

import DangerousButton from '~/components/common/DangerousButton.vue'
import PlaylistForm from '~/components/playlists/Form.vue'

import Layout from '~/components/ui/Layout.vue'
import Button from '~/components/ui/Button.vue'
import Alert from '~/components/ui/Alert.vue'

interface Events {
  (e: 'update:playlistTracks', value: PlaylistTrack[]): void
  (e: 'update:playlist', value: Playlist): void
}

interface Props {
  playlist: Playlist | null
  playlistTracks: PlaylistTrack[]
}

const emit = defineEmits<Events>()
const props = defineProps<Props>()

const { playlistTracks, playlist } = useVModels(props, emit)

const errors = ref([] as string[])
const duplicateTrackAddInfo = ref<{ tracks: string[] }>()
const showDuplicateTrackAddConfirmation = ref(false)

const { tracks: queueTracks } = useQueue()

interface ModifiedPlaylistTrack extends PlaylistTrack {
  _id?: string
}

const tracks = computed({
  get: () => playlistTracks.value.map((playlistTrack, index) => ({ ...playlistTrack, _id: `${ index }-${ playlistTrack.track }` } as ModifiedPlaylistTrack)),
  set: (playlist) => {
    playlistTracks.value = playlist.map((modifiedPlaylistTrack, index) => {
      const res = { ...modifiedPlaylistTrack, index } as ModifiedPlaylistTrack
      delete res._id
      return res as PlaylistTrack
    })
  }
})

const { t } = useI18n()
const labels = computed(() => ({
  copyTitle: t('components.playlists.Editor.button.copy')
}))

const isLoading = ref(false)
const status = computed(() => isLoading.value
  ? 'loading'
  : showDuplicateTrackAddConfirmation.value
    ? 'confirmDuplicateAdd'
    : errors.value.length > 0
      ? 'errored'
      : 'saved'
)

const responseHandlers = {
  success () {
    errors.value = []
    showDuplicateTrackAddConfirmation.value = false
  },
  errored (error: BackendError): void {
    showDuplicateTrackAddConfirmation.value = false

    const { backendErrors, rawPayload = {} } = error
    if (backendErrors.length === 1 && backendErrors[0] === 'Tracks Already Exist In Playlist') {
      duplicateTrackAddInfo.value = ((rawPayload.playlist as APIErrorResponse).non_field_errors as APIErrorResponse)[0] as { tracks: string[] }
      showDuplicateTrackAddConfirmation.value = true
      return
    }

    errors.value = backendErrors
  }
}

const fetchTracks = async () => {
  // NOTE: This is handled by other functions and never used directly
  const response = await axios.get(`playlists/${playlist.value?.uuid}/tracks/`)
  playlistTracks.value = response.data.results
}

const store = useStore()
const reorder = async ({ oldIndex: from, newIndex: to }: { oldIndex: number, newIndex: number }) => {
  isLoading.value = true

  try {
    await axios.post(`playlists/${playlist.value?.uuid}/move/`, { from, to })
    await store.dispatch('playlists/fetchOwn')
    responseHandlers.success()
  } catch (error) {
    responseHandlers.errored(error as BackendError)
  }

  isLoading.value = false
}

const removePlaylistTrack = async (index: number) => {
  isLoading.value = true

  try {
    tracks.value.splice(index, 1)
    await axios.post(`playlists/${playlist.value?.uuid}/remove/`, { index })
    await Promise.all([
      store.dispatch('playlists/fetchOwn'),
      fetchTracks()
    ])
    responseHandlers.success()
  } catch (error) {
    responseHandlers.errored(error as BackendError)
  }

  isLoading.value = false
}

const clearPlaylist = async () => {
  isLoading.value = true

  try {
    tracks.value = []
    await axios.delete(`playlists/${playlist.value?.uuid}/clear/`)
    await store.dispatch('playlists/fetchOwn')
    responseHandlers.success()
  } catch (error) {
    responseHandlers.errored(error as BackendError)
  }

  isLoading.value = false
}

const insertMany = async (insertedTracks: number[], allowDuplicates: boolean) => {
  isLoading.value = true

  try {
    const response = await axios.post(`playlists/${playlist.value?.uuid}/add/`, {
      allow_duplicates: allowDuplicates,
      tracks: insertedTracks
    })

    tracks.value.push(...response.data.results)
    await Promise.all([
      store.dispatch('playlists/fetchOwn'),
      fetchTracks()
    ])
    responseHandlers.success()
  } catch (error) {
    responseHandlers.errored(error as BackendError)
  }

  isLoading.value = false
}
onMounted(() => {
  fetchTracks()
})
</script>

<template>
  <Layout stack>
    <h3 class="ui top attached header">
      {{ t('components.playlists.Editor.header.editor') }}
    </h3>
    <playlist-form
      v-model:playlist="playlist"
      :title="false"
    />
    <template v-if="status === 'loading'">
      <div class="ui active tiny inline loader" />
      {{ t('components.playlists.Editor.loading.sync') }}
    </template>
    <template v-else-if="status === 'errored'">
      <i class="dangerclose icon" />
      {{ t('components.playlists.Editor.error.sync') }}
      <Alert
        v-if="errors.length > 0"
        red
        role="alert"
      >
        <ul class="list">
          <li
            v-for="error in errors"
            :key="error"
          >
            {{ error }}
          </li>
        </ul>
      </Alert>
    </template>
    <Alert
      v-else-if="status === 'confirmDuplicateAdd'"
      red
      role="alert"
    >
      <p>
        {{ t('components.playlists.Editor.warning.duplicate') }}
      </p>
      <ul class="ui relaxed divided list duplicate-tracks-list">
        <li
          v-for="track in duplicateTrackAddInfo?.tracks ?? []"
          :key="track"
          class="ui item"
        >
          {{ track }}
        </li>
      </ul>
      <Button
        destructive
        @click="insertMany(queueTracks, true)"
      >
        {{ t('components.playlists.Editor.button.addDuplicate') }}
      </Button>
    </Alert>
    <Alert
      v-else-if="status === 'saved'"
      green
      align-content="center"
    >
      <span>
        <i class="bi bi-check" />
        {{ t('components.playlists.Editor.message.sync') }}
      </span>
    </Alert>
    <Layout flex>
      <Button
        :disabled="queueTracks.length === 0"
        primary
        :class="['ui', {disabled: queueTracks.length === 0}, 'labeled', 'icon', 'button']"
        :title="labels.copyTitle"
        icon="bi-plus"
        @click="insertMany(queueTracks, false)"
      >
        {{ t('components.playlists.Editor.button.insertFromQueue', queueTracks.length) }}
      </Button>

      <dangerous-button
        :disabled="tracks.length === 0"
        icon="bi-eraser-fill"
        style="float: right;"
        :action="clearPlaylist"
        :title="t('components.playlists.Editor.modal.clearPlaylist.header', { playlist: playlist?.name })"
      >
        {{ t('components.playlists.Editor.button.clear') }}
        <template #content>
          {{ t('components.playlists.Editor.modal.clearPlaylist.content.warning') }}
        </template>
        <template #confirm>
          {{ t('components.playlists.Editor.button.clear') }}
        </template>
      </dangerous-button>
    </Layout>
    <template v-if="tracks.length > 0">
      <p>
        {{ t('components.playlists.Editor.help.reorder') }}
      </p>
      <div class="table-wrapper">
        <!-- TODO: Use activity.vue -->
        <table class="ui compact very basic unstackable table">
          <draggable
            v-model="tracks"
            tag="tbody"
            item-key="_id"
            @update="reorder"
          >
            <template #item="{ element: plt, index }">
              <tr>
                <td class="left aligned">
                  {{ plt.index + 1 }}
                </td>
                <td class="center aligned">
                  <img
                    v-if="plt.track.album && plt.track.album.cover && plt.track.album.cover.urls.original"
                    v-lazy="store.getters['instance/absoluteUrl'](plt.track.album.cover.urls.medium_square_crop)"
                    alt=""
                    style="width: 40px;"
                  >
                  <img
                    v-else
                    alt=""
                    style="width: 40px;"
                    src="../../assets/audio/default-cover.png"
                  >
                </td>
                <td colspan="4">
                  <strong>{{ plt.track.title }}</strong><br>
                  {{ generateTrackCreditString(plt.track) }}
                </td>
                <td class="right aligned">
                  <Button
                    square-small
                    round
                    destructive
                    @click.stop="removePlaylistTrack(index)"
                  >
                    <i
                      class="bi bi-trash"
                    />
                  </Button>
                </td>
              </tr>
            </template>
          </draggable>
        </table>
      </div>
    </template>
  </Layout>
</template>
