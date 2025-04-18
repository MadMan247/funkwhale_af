<script setup lang="ts">
import type { Album } from '~/types'

import { reactive, ref, watch } from 'vue'
import { useStore } from '~/store'

import axios from 'axios'

import usePage from '~/composables/navigation/usePage'
import useErrorHandler from '~/composables/useErrorHandler'

import AlbumCard from '~/components/album/Card.vue'
import Section from '~/components/ui/Section.vue'
import Loader from '~/components/ui/Loader.vue'
import Pagination from '~/components/ui/Pagination.vue'

interface Props {
  filters: Record<string, string | boolean>
  showCount?: boolean
  search?: boolean
  limit?: number
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  showCount: false,
  search: false,
  limit: 12,
  title: undefined
})

const store = useStore()

const query = ref('')
const albums = reactive([] as Album[])
const count = ref(0)
const page = usePage()
const nextPage = ref()

const isLoading = ref(false)
const fetchData = async (url = 'albums/') => {
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
    albums.splice(0, albums.length, ...response.data.results)
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

setTimeout(fetchData, 1000)

const performSearch = () => {
  albums.length = 0
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
    :h2="title"
    :columns-per-item="1"
  >
    <inline-search-bar
      v-if="search"
      v-model="query"
      style="grid-column: 1 / -1;"
      @search="performSearch"
    />
    <Loader
      v-if="isLoading"
      style="grid-column: 1 / -1;"
    />
    <template v-if="!isLoading && albums.length > 0">
      <album-card
        v-for="album in albums"
        :key="album.id"
        :album="album"
      />
    </template>
    <slot
      v-if="!isLoading && albums.length === 0"
      name="empty-state"
    >
      <empty-state
        :refresh="true"
        style="grid-column: 1 / -1;"
        @refresh="fetchData"
      />
    </slot>
    <Pagination
      v-if="page && albums && count > props.limit"
      v-model:page="page"
      :pages="Math.ceil((count || 0) / props.limit)"
      style="grid-column: 1 / -1;"
    />
  </Section>
</template>
