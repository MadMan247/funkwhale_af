<script setup lang="ts">
import { computed, ref } from 'vue'

import type { operations } from '~/generated/types'
import { useStore } from '~/store'
import { useDataStore } from '~/ui/stores/data'

import AlbumCard from '~/components/album/Card.vue'
import InlineSearchBar from '~/components/common/InlineSearchBar.vue'

import Loader from '~/components/ui/Loader.vue'
import Pagination from '~/components/ui/Pagination.vue'
import Section from '~/components/ui/Section.vue'
import Spacer from '~/components/ui/Spacer.vue'

/* TODO: Simplify Link and Button props #2500; then explicitly route `action` prop to Section
 Alt.: Re-implement action as slot (better!)
 ```ts
 import type { ComponentProps } from 'vue-component-type-helpers'
 ...
 action?: ComponentProps<typeof Section>['action']
 ```
 - Not possible right now because component props of Link and Button are too complex to represent
*/
const { title, hasSearch, query } = defineProps<{
  title?: string
  hasSearch?: boolean
  query: Required<operations['get_albums']['parameters']>['query']
}>()

const store = useStore()

const page = ref(1)
const q = ref('')
const page_size_fallback = 12

const albums = computed(() => useDataStore().albums({
  page: page.value,
  page_size: page_size_fallback,
  q: q.value,
  ...query
}, {
  refetchSignal: store.state.moderation.lastUpdate
}).value)
</script>

<template>
  <Section
    align-left
    :h2="title"
    :columns-per-item="1"
  >
    <InlineSearchBar
      v-if="hasSearch"
      v-model="q"
      style="grid-column: 1 / -1;"
      @search="albums.refetch"
    />
    <Loader
      v-if="albums.status === 'loading'"
      style="grid-column: 1 / -1;"
    />
    <template v-if="albums.data">
      <album-card
        v-for="album in albums.data.results"
        :key="album.id"
        :album
      />
      <slot
        v-if="albums.status !== 'loading' && albums.data.count === 0"
        name="empty-state"
      >
        <empty-state
          :refresh="true"
          style="grid-column: 1 / -1;"
          @refresh="albums.refetch"
        />
      </slot>
      <Spacer grow />
      <Pagination
        v-if="albums.data.count > (query.page_size ?? page_size_fallback)"
        v-model:page="page"
        :pages="Math.ceil(albums.data.count / (query.page_size ?? page_size_fallback))"
        style="grid-column: 1 / -1;"
      />
    </template>
  </Section>
</template>
