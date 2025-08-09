<script setup lang="ts">
import type { Artist } from '~/types'

import { reactive, ref, watch, onMounted } from 'vue'
import { useStore } from '~/store'

import axios from 'axios'

import useErrorHandler from '~/composables/useErrorHandler'

import ArtistCard from '~/components/artist/Card.vue'
import Section from '~/components/ui/Section.vue'
import Pagination from '~/components/ui/Pagination.vue'
import Loader from '~/components/ui/Loader.vue'

interface Props {
  filters: Record<string, string | boolean>
  search?: boolean
  header?: boolean
  limit?: number
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  search: false,
  header: true,
  limit: 12,
  title: undefined
})

const store = useStore()

const query = ref('')
const artists = reactive([] as Artist[])
const count = ref(0)
const page = ref(1)
const nextPage = ref()

const isLoading = ref(false)
const fetchData = async (url = 'artists/') => {
  isLoading.value = true

  try {
    const params = {
      q: query.value,
      ...props.filters,
      page: page.value,
      page_size: props.limit
    }

    const response = await axios.get(url, { params })
    nextPage.value = response.data.next
    count.value = response.data.count
    artists.splice(0, artists.length, ...response.data.results)
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

onMounted(() => {
  setTimeout(fetchData, 1000)
})

const performSearch = () => {
  artists.length = 0
  fetchData()
}

watch(
  [() => store.state.moderation.lastUpdate, page],
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
    <slot
      v-if="!isLoading && artists.length === 0"
      name="empty-state"
    >
      <empty-state
        style="grid-column: 1 / -1;"
        :refresh="true"
        @refresh="fetchData"
      />
    </slot>
    <inline-search-bar
      v-if="!isLoading && search"
      v-model="query"
      style="grid-column: 1 / -1;"
      @search="performSearch"
    />
    <artist-card
      v-for="artist in artists"
      :key="artist.id"
      :artist="artist"
    />
    <Pagination
      v-if="page && artists && count > limit"
      v-model:page="page"
      style="grid-column: 1 / -1;"
      :pages="Math.ceil((count || 0) / limit)"
    />
  </Section>
</template>
