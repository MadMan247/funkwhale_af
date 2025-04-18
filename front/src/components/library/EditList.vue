<script setup lang="ts">
import type { BackendError, ReviewState, Review } from '~/types'
import { ref, watchEffect } from 'vue'

import axios from 'axios'

import EditCard from '~/components/library/EditCard.vue'
import Layout from '~/components/ui/Layout.vue'
import Button from '~/components/ui/Button.vue'
import Loader from '~/components/ui/Loader.vue'

interface Props {
  url: string
  filters?: object
  currentState?: ReviewState
}

const props = withDefaults(defineProps<Props>(), {
  filters: () => ({}),
  currentState: () => ({})
})

const errors = ref([] as string[])
const previousPage = ref()
const nextPage = ref()
const objects = ref([] as Review[])
const isLoading = ref(false)
const fetchData = async (url = props.url) => {
  isLoading.value = true
  const params = {
    ...props.filters,
    page_size: 5
  }

  try {
    const response = await axios.get(url, { params })
    previousPage.value = response.data.previous
    nextPage.value = response.data.next
    objects.value = response.data.results
  } catch (error) {
    errors.value = (error as BackendError).backendErrors
  }

  isLoading.value = false
}

watchEffect(() => fetchData())
</script>

<template>
  <h3>
    <slot />
  </h3>
  <slot
    v-if="!isLoading && objects.length === 0"
    name="empty-state"
  />
  <Layout grid>
    <Button
      v-if="nextPage || previousPage"
      :disabled="!previousPage"
      primary
      round
      align-self="center"
      icon="bi-chevron-left"
      @click="fetchData(previousPage)"
    />
    <Loader v-if="isLoading" />
    <edit-card
      v-for="obj in objects"
      :key="obj.uuid"
      :obj="obj"
      :current-state="currentState"
      @updated="fetchData(url)"
      @deleted="fetchData(url)"
    />
    <Button
      v-if="nextPage || previousPage"
      :disabled="!nextPage"
      align-self="center"
      primary
      round
      icon="bi-chevron-right"
      @click="fetchData(nextPage)"
    />
  </Layout>
</template>
