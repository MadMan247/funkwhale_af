<script setup lang="ts">
import { ref,computed } from 'vue'
import { useStore } from '~/store'

import ArtistCard from '~/components/artist/Card.vue'
import Section from '~/components/ui/Section.vue'
import Pagination from '~/components/ui/Pagination.vue'
import Loader from '~/components/ui/Loader.vue'
import type { operations } from '~/generated/types'
import { useDataStore } from '~/ui/stores/data'

const store = useStore()

 const { title, hasSearch, query } = defineProps<{
  title?: string
  hasSearch?: boolean
  query: Required<operations['get_artists']['parameters']>['query']
}>()

const page = ref(1)
const q = ref('')
const page_size_fallback = 12

const artists = computed(() => useDataStore().artists({
  page_size: page_size_fallback,
  page: page.value,
    q: q.value,
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
      v-if="artists.status === 'loading'"
      style="grid-column: 1 / -1;"
    />
    <slot
      v-else-if="artists.data?.count === 0"
      name="empty-state"
    >
      <empty-state
        style="grid-column: 1 / -1;"
        :refresh="true"
        @refresh="artists.refetch"
      />
    </slot>
    <inline-search-bar
      v-if="artists.status !== 'loading' && hasSearch"
      v-model="q"
      style="grid-column: 1 / -1;"
      @search="artists.refetch"
    />
    <template v-if="artists.data">
      <artist-card
        v-for="artist in artists.data.results"
        :key="artist.id"
        :artist
      />
      <Pagination
        v-if="artists.data.count > (query.page_size ?? page_size_fallback)"
        v-model:page="page"
        style="grid-column: 1 / -1;"
        :pages="Math.ceil(artists.data.count / (query.page_size ?? page_size_fallback))"
      />
    </template>
  </Section>
</template>
