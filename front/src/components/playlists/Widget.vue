<script setup lang="ts">
import { ref, computed } from 'vue'
import { useStore } from '~/store'
import { useI18n } from 'vue-i18n'

import type { operations } from '~/generated/types'

import PlaylistCard from '~/components/playlists/Card.vue'
import Button from '~/components/ui/Button.vue'
import Section from '~/components/ui/Section.vue'
import Alert from '~/components/ui/Alert.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Loader from '~/components/ui/Loader.vue'
import Pagination from '~/components/ui/Pagination.vue'
import { useDataStore } from '~/ui/stores/data'

const { t } = useI18n()
const store = useStore()

const { title, query } = defineProps<{
  title?: string
  query: Required<operations['get_playlists']['parameters']>['query']
}>()

const page = ref(1)
const page_size_fallback = 4

const playlists = computed(() => useDataStore().playlists({
  page_size: page_size_fallback,
  page: page.value,
  ...query
}, {
  refetchSignal: store.state.moderation.lastUpdate
}).value)
</script>

<template>
  <Section
    align-left
    :columns-per-item="3"
    :h2="title"
  >
    <Loader
      v-if="playlists.status === 'loading'"
      style="grid-column: 1 / -1;"
    />
    <Alert
      v-else-if="playlists.data?.count === 0"
      style="grid-column: 1 / -1;"
      blue
      align-items="center"
    >
      <h4>
        <i class="bi bi-search" />
        {{ t('components.playlists.Widget.placeholder.noPlaylists') }}
      </h4>
      <Spacer />
      <Button
        v-if="store.state.auth.authenticated"
        icon="bi-music-note-list"
        primary
        align-self="center"
        @click="store.commit('playlists/chooseTrack', null)"
      >
        {{ t('components.playlists.Widget.button.create') }}
      </Button>
    </Alert>
    <template v-if="playlists.data">
      <PlaylistCard
        v-for="playlist in playlists.data.results"
        :key="playlist.uuid"
        :playlist
      />
      <Pagination
        v-if="playlists.data.count > (query.page_size ?? page_size_fallback)"
        v-model:page="page"
        :pages="Math.ceil((playlists.data.count || 0) / (query.page_size ?? page_size_fallback))"
      />
    </template>
  </Section>
</template>
