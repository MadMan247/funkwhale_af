<script setup lang="ts">
import type { BackendError, PaginatedChannelList } from '~/types'
import { type operations } from '~/generated/types.ts'

import { ref, onMounted, watch } from 'vue'
import { clone } from 'lodash-es'

import axios from 'axios'

import ChannelCard from '~/components/audio/ChannelCard.vue'
import Loader from '~/components/ui/Loader.vue'
import Section from '~/components/ui/Section.vue'
import Pagination from '~/components/ui/Pagination.vue'

interface Events {
  (e: 'fetched', channels: PaginatedChannelList): void
}

interface Props {
  filters: Record<string, string | boolean>
  limit?: number
  title?: string
}

const emit = defineEmits<Events>()
const props = withDefaults(defineProps<Props>(), {
  limit: 5,
  title: undefined
})

const result = ref<PaginatedChannelList>()
const errors = ref([] as string[])
const nextPage = ref()
const page = ref(1)
const count = ref(0)

const isLoading = ref(false)

const fetchData = async (url = 'channels/') => {
  isLoading.value = true

  const params: operations['get_channels']['parameters']['query'] = {
    ...clone(props.filters),
    page: page.value,
    page_size: props.limit
  }

  try {
    const response = await axios.get<PaginatedChannelList>(url, { params })
    nextPage.value = response.data.next
    count.value = response.data.count
    result.value = response.data
    emit('fetched', response.data)
  } catch (error) {
    errors.value = (error as BackendError).backendErrors
  }

  isLoading.value = false
}

onMounted(() => {
  fetchData()
})

watch([() => props.filters, page],
  () => fetchData(),
  { deep: true }
)
</script>

<template>
  <Section
    align-left
    :columns-per-item="1"
    :h2="title || undefined"
  >
    <Loader
      v-if="isLoading"
      style="grid-column: 1 / -1;"
    />
    <template
      v-if="!isLoading && result?.count === 0"
    >
      <empty-state
        :refresh="true"
        style="grid-column: 1 / -1;"
        @refresh="fetchData('channels/')"
      />
    </template>
    <Pagination
      v-if="page && result && count > limit && limit > 16"
      v-model:page="page"
      :pages="Math.ceil((count || 0) / limit)"
      style="grid-column: 1 / -1;"
    />
    <channel-card
      v-for="channel in result?.results"
      :key="channel.uuid"
      :object="channel"
    />
    <Pagination
      v-if="page && result && count > limit"
      v-model:page="page"
      :pages="Math.ceil((count || 0) / limit)"
      style="grid-column: 1 / -1;"
    />
  </Section>
</template>
