<script setup lang="ts">
import type { Playlist } from '~/types'

import { ref, reactive, watch } from 'vue'
import { useStore } from '~/store'
import { useI18n } from 'vue-i18n'

import axios from 'axios'

import useErrorHandler from '~/composables/useErrorHandler'

import PlaylistCard from '~/components/playlists/Card.vue'
import Button from '~/components/ui/Button.vue'
import Section from '~/components/ui/Section.vue'
import Alert from '~/components/ui/Alert.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Loader from '~/components/ui/Loader.vue'
import Pagination from '~/components/ui/Pagination.vue'

interface Props {
  filters: Record<string, unknown>
  url: string
  title?: string
}

const { t } = useI18n()

const props = defineProps<Props>()

const store = useStore()

const objects = reactive([] as Playlist[])
const page = ref(1)
const nextPage = ref('')
const count = ref(0)

const isLoading = ref(false)

const fetchData = async (url = props.url) => {
  isLoading.value = true

  try {
    const params = {
      ...props.filters,
      page: page.value,
      page_size: props.filters.limit ?? 4
    }

    const response = await axios.get(url, { params })
    nextPage.value = response.data.next
    count.value = response.data.count
    objects.splice(0, objects.length, ...response.data.results)
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

fetchData()

watch(
  () => [store.state.moderation.lastUpdate, page.value],
  () => fetchData(),
  { immediate: true }
)
</script>

<template>
  <Section
    align-left
    :columns-per-item="3"
    :h2="title"
  >
    <Loader
      v-if="isLoading"
      style="grid-column: 1 / -1;"
    />
    <Alert
      v-if="!isLoading && objects.length === 0"
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
    <PlaylistCard
      v-for="playlist in objects"
      :key="playlist.uuid"
      :playlist="playlist"
    />
  </Section>
  <Pagination
    v-if="page && objects && count > (props.filters.limit as number)"
    v-model:page="page"
    :pages="Math.ceil((count || 0) / (props.filters.limit as number))"
  />
</template>
