<script setup lang="ts">
import type { BackendError, Playlist, APIErrorResponse } from '~/types'

import { filter, sortBy, flow } from 'lodash-es'
import axios from 'axios'
import { useI18n } from 'vue-i18n'
import Modal from '~/components/ui/Modal.vue'
import PlaylistForm from '~/components/playlists/Form.vue'
import useLogger from '~/composables/useLogger'
import { useStore } from '~/store'
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { generateTrackCreditString } from '~/utils/utils'

import Button from '~/components/ui/Button.vue'
import Link from '~/components/ui/Link.vue'
import Alert from '~/components/ui/Alert.vue'
import Spacer from '~/components/ui/Spacer.vue'

const logger = useLogger()
const store = useStore()

const showDuplicateTrackAddConfirmation = ref(false)

const router = useRouter()
router.beforeEach(() => {
  store.commit('playlists/showModal', false)
  showDuplicateTrackAddConfirmation.value = false
})

const playlists = computed(() => store.state.playlists.playlists)
const track = computed(() => store.state.playlists.modalTrack)
const trackCreditString = computed(() => generateTrackCreditString(track.value))

const { t } = useI18n()
const labels = computed(() => ({
  addToPlaylist: t('components.playlists.PlaylistModal.button.addToPlaylist'),
  filterPlaylistField: t('components.playlists.PlaylistModal.placeholder.filterPlaylist')
}))

const playlistNameFilter = ref('')

const sortedPlaylists = computed(() => flow(
  filter((playlist: Playlist) => playlist.name.match(new RegExp(playlistNameFilter.value, 'i')) !== null),
  sortBy((playlist: Playlist) => { return playlist.modification_date })
)(playlists.value).reverse())

const formKey = ref(new Date().toString())
watch(() => store.state.playlists.showModal, () => {
  formKey.value = new Date().toString()
  showDuplicateTrackAddConfirmation.value = false
})

const lastSelectedPlaylist = ref(-1)
const errors = ref([] as string[])
const duplicateTrackAddInfo = ref({} as { playlist_name?: string })

const addToPlaylist = async (playlistId: number, allowDuplicates: boolean) => {
  lastSelectedPlaylist.value = playlistId

  try {
    await axios.post(`playlists/${playlistId}/add/`, {
      tracks: [track.value?.id].filter(i => i),
      allow_duplicates: allowDuplicates
    })

    logger.info('Successfully added track to playlist')
    store.state.playlists.showModal = false
    store.dispatch('playlists/fetchOwn')
  } catch (error) {
    if (error as BackendError) {
      const { backendErrors, rawPayload = {} } = error as BackendError

      if (backendErrors.length === 1 && backendErrors[0] === 'Tracks Already Exist In Playlist') {
        duplicateTrackAddInfo.value = ((rawPayload.playlist as APIErrorResponse).non_field_errors as APIErrorResponse)[0] as object
        showDuplicateTrackAddConfirmation.value = true
      } else {
        errors.value = backendErrors
        showDuplicateTrackAddConfirmation.value = false
      }
    }
  }
}

store.dispatch('playlists/fetchOwn')
</script>

<template>
  <Modal
    v-model="store.state.playlists.showModal"
    :title="t('components.playlists.PlaylistModal.header.addToPlaylist')"
    :cancel="t('components.playlists.PlaylistModal.button.cancel')"
    :priority="8"
  >
    <template v-if="track">
      <h3 class="ui header">
        {{ t('components.playlists.PlaylistModal.header.addToPlaylist') }}
        <div class="ui sub header">
          {{ t('components.playlists.PlaylistModal.header.track', { artist: trackCreditString, title: track.title }) }}
        </div>
      </h3>
    </template>
    <div v-if="playlists.length > 0">
      <Alert
        v-if="showDuplicateTrackAddConfirmation"
        yellow
      >
        <p>
          <i18n-t keypath="components.playlists.PlaylistModal.warning.duplicate">
            <strong>{{ track?.title }}</strong>
            <strong>{{ duplicateTrackAddInfo.playlist_name }}</strong>
          </i18n-t>
        </p>
        <Button
          primary
          @click="addToPlaylist(lastSelectedPlaylist, true)"
        >
          {{ t('components.playlists.PlaylistModal.button.addDuplicate') }}
        </Button>
      </Alert>
      <Alert
        v-if="errors.length > 0"
        role="alert"
        red
      >
        <h4 class="header">
          {{ t('components.playlists.PlaylistModal.header.addFailure') }}
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

      <h4 class="ui header">
        {{ t('components.playlists.PlaylistModal.header.available') }}
      </h4>
      <!-- TODO: Add Playlist filter -->
      <!-- <Input
        id="playlist-name-filter"
        v-model="playlistNameFilter"
        :placeholder="labels.filterPlaylistField"
        :label="t('components.playlists.PlaylistModal.label.filter')"
      /> -->
      <table
        v-if="sortedPlaylists.length > 0"
        class="ui unstackable very basic table"
      >
        <thead>
          <tr>
            <th>
              <span class="visually-hidden">{{ t('components.playlists.PlaylistModal.table.edit.header.edit')
              }}</span>
            </th>
            <th>
              {{ t('components.playlists.PlaylistModal.table.edit.header.name') }}
            </th>
            <th class="sorted descending">
              {{ t('components.playlists.PlaylistModal.table.edit.header.lastModification') }}
            </th>
            <th>
              {{ t('components.playlists.PlaylistModal.table.edit.header.tracks') }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(playlist, key) in sortedPlaylists"
            :key="key"
          >
            <td>
              <Link
                solid
                secondary
                square-small
                :to="{ name: 'library.playlists.detail', params: { id: playlist.uuid }, query: { mode: 'edit' } }"
                icon="bi-pencil-fill"
              >
                <span class="visually-hidden">{{ t('components.playlists.PlaylistModal.button.edit') }}</span>
              </Link>
            </td>
            <td>
              <router-link
                :to="{ name: 'library.playlists.detail', params: { id: playlist.uuid } }"
                @click="store.state.playlists.showModal = false"
              >
                {{ playlist.name }}
              </router-link>
            </td>
            <td><human-date :date="playlist.modification_date" /></td>
            <td>{{ playlist.tracks_count }}</td>
            <td>
              <Button
                v-if="track"
                low-height
                primary
                :title="labels.addToPlaylist"
                icon="bi-plus"
                @click.prevent="addToPlaylist(playlist.uuid, false)"
              >
                {{ t('components.playlists.PlaylistModal.button.addTrack') }}
              </Button>
            </td>
          </tr>
        </tbody>
      </table>
      <template v-else>
        <Spacer />
        <Alert blue>
          <span>
            {{ t('components.playlists.PlaylistModal.header.noResults') }}
          </span>
        </Alert>
      </template>
    </div>
    <div
      v-else
      class="ui placeholder segment"
    >
      <div class="ui icon header">
        <i class="bi bi-list" />
        {{ t('components.playlists.PlaylistModal.empty.noPlaylists') }}
      </div>
    </div>

    <Spacer />

    <playlist-form
      :key="formKey"
      :create="true"
    />
  </Modal>
</template>
