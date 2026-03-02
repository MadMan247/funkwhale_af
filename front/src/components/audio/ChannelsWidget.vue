<script setup lang="ts">
import { ref, computed } from 'vue'

import { type operations } from '~/generated/types.ts'
import { useDataStore } from '~/ui/stores/data'

import ChannelCard from '~/components/audio/ChannelCard.vue'

import Loader from '~/components/ui/Loader.vue'
import Section from '~/components/ui/Section.vue'
import Pagination from '~/components/ui/Pagination.vue'

/* TODO: Simplify Link and Button props #2500; then explicitly route `action` prop to Section
 Alt.: Re-implement action as slot (better!)
 ```ts
 import type { ComponentProps } from 'vue-component-type-helpers'
 ...
 action?: ComponentProps<typeof Section>['action']
 ```
 - Not possible right now because component props of Link and Button are too complex to represent
*/
 const { title, query } = defineProps<{
  title?: string
  query: Required<operations['get_channels']['parameters']>['query']
}>()

const page = ref(1)
const page_size_fallback = 5

const channels = computed(() => useDataStore().channels({
  page_size: page_size_fallback,
  page: page.value,
  ...query
}).value)
</script>

<template>
  <Section
    align-left
    :columns-per-item="1"
    :h2="title"
  >
    <Loader
      v-if="channels.status === 'loading'"
      style="grid-column: 1 / -1;"
    />
    <empty-state
      v-else-if="channels.data?.count === 0"
      :refresh="true"
      style="grid-column: 1 / -1;"
      @refresh="channels.refetch"
    />
    <template v-if="channels.data">
      <Pagination
        v-if="channels.data.count > (query.page_size ?? page_size_fallback)"
        v-model:page="page"
        :pages="Math.ceil((channels.data.count || 0) / (query.page_size ?? page_size_fallback))"
        style="grid-column: 1 / -1;"
      />
      <channel-card
        v-for="channel in channels.data.results"
        :key="channel.uuid"
        :object="channel"
      />
      <Pagination
        v-if="channels.data.count > (query.page_size ?? page_size_fallback)"
        v-model:page="page"
        :pages="Math.ceil((channels.data.count || 0) / (query.page_size ?? page_size_fallback))"
        style="grid-column: 1 / -1;"
      />
    </template>
  </Section>
</template>
