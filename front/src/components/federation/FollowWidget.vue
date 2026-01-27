<script setup lang="ts">

import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { components } from '~/generated/types'
import type { BackendError } from '~/types'

import axios from 'axios'

import Layout from '~/components/ui/Layout.vue'
import Section from '~/components/ui/Section.vue'
import Loader from '~/components/ui/Loader.vue'
import Alert from '~/components/ui/Alert.vue'
import ActorCard from '~/components/federation/ActorCard.vue'
import Pagination from '~/components/ui/Pagination.vue'


interface Props {
  title?: string
	url: string
	pageSize?: number
	isOwnProfile?: boolean
}
const props = defineProps<Props>()

const { t } = useI18n()

const paginateBy = props.pageSize || 4
const page = ref(1)
const nextPage = ref()

const isLoading = ref(false)
const isFollowersEndpoint = computed(() => props.url.includes('followers'))

const result = ref()

const actors = reactive([] as components['schemas']['Actor'][])
const totalItems = ref(0)

const errors = ref([] as string[])

const handleActorRevoked = () => {
  // Refetch data to reflect the revocation
  fetchData()
}

const fetchData = async (url = props.url) => {
  isLoading.value = true

  try {
    const response = await axios.get(url, {
      params: {
        page: page.value,
        page_size: paginateBy
      }
    })
    nextPage.value = response.data.partOf
    result.value = response.data

    if (response.data.items && Array.isArray(response.data.items)) {
      actors.splice(0, actors.length, ...response.data.items)
    } else {
      // Clear actors if response structure is unexpected to prevent displaying stale data
      actors.splice(0, actors.length)
    }
  } catch (error: any) {
    const backendError = error as BackendError

    if (backendError.response?.status === 403) {
      errors.value = ['private']
    } else {
      errors.value = backendError.backendErrors ?? [error.message ?? error]
    }
  }

  isLoading.value = false
  totalItems.value = result.value?.totalItems || 0
}

onMounted(() => {
  setTimeout(fetchData, 1000)
})
watch(page, () => {
  fetchData()
})
</script>

<template>
  <Section
    align-left
    :h2="title"
  >
    <Loader
      v-if="isLoading"
      style="grid-column: 1 / -1;"
    />
    <Alert
      v-if="!isLoading && result && totalItems === 0"
      blue
      style="grid-column: 1 / -1;"
    >
      {{ isFollowersEndpoint ? t('components.federation.FollowWidget.empty.noFollowers') : t('components.federation.FollowWidget.empty.noFollowing') }}
    </Alert>
    <Alert
      v-if="!isLoading && errors.length > 0"
      blue
      style="grid-column: 1 / -1;"
    >
      <span v-if="errors.includes('private')">{{ t('components.federation.FollowWidget.empty.private') }}</span>
      <span v-else>{{ errors[0] }}</span>
    </Alert>
    <Layout
      v-if="!isLoading && totalItems > 0"
      flex
    >
      <actor-card
        v-for="actor in actors"
        :key="actor.id"
        :actor="actor"
        :follower="isFollowersEndpoint"
        :following="!isFollowersEndpoint"
        :is-own-profile="isOwnProfile"
        @revoked="handleActorRevoked"
      />
    </Layout>
    <Pagination
      v-if="page && actors && result && totalItems > paginateBy"
      v-model:page="page"
      style="grid-column: 1 / -1;"
      :pages="Math.ceil((totalItems || 0) / paginateBy)"
    />
  </Section>
</template>
