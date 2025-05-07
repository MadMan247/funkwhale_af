<script setup lang="ts">
import type { OrderingProps } from '~/composables/navigation/useOrdering'
import type { Playlist, BackendResponse } from '~/types'
import type { RouteRecordName } from 'vue-router'
import type { OrderingField } from '~/store/ui'

import { computed, ref, watch } from 'vue'
import { useRouteQuery } from '@vueuse/router'
import { useI18n } from 'vue-i18n'
import { syncRef } from '@vueuse/core'
import { sortedUniq } from 'lodash-es'
import { useStore } from '~/store'

import axios from 'axios'

import PlaylistsCard from '~/components/playlists/Card.vue'
import Pagination from '~/components/ui/Pagination.vue'
import Layout from '~/components/ui/Layout.vue'
import Button from '~/components/ui/Button.vue'
import Input from '~/components/ui/Input.vue'
import Alert from '~/components/ui/Alert.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Header from '~/components/ui/Header.vue'
import Section from '~/components/ui/Section.vue'
import Loader from '~/components/ui/Loader.vue'

import useSharedLabels from '~/composables/locale/useSharedLabels'
import useOrdering from '~/composables/navigation/useOrdering'
import useErrorHandler from '~/composables/useErrorHandler'
import usePage from '~/composables/navigation/usePage'
import useLogger from '~/composables/useLogger'

interface Props extends OrderingProps {
  scope?: 'me' | 'all'

  // TODO(wvffle): Remove after https://github.com/vuejs/core/pull/4512 is merged
  orderingConfigName?: RouteRecordName
}

const store = useStore()

const props = withDefaults(defineProps<Props>(), {
  scope: 'all',
  orderingConfigName: undefined
})

const page = usePage()

const q = useRouteQuery('query', '')
const query = ref(q.value)
syncRef(q, query, { direction: 'ltr' })

const result = ref<BackendResponse<Playlist>>()

const orderingOptions: [OrderingField, keyof typeof sharedLabels.filters][] = [
  ['creation_date', 'creation_date'],
  ['modification_date', 'modification_date'],
  ['name', 'name']
]

const logger = useLogger()
const sharedLabels = useSharedLabels()

const { onOrderingUpdate, orderingString, paginateBy, ordering, orderingDirection } = useOrdering(props)

const isLoading = ref(false)
const fetchData = async () => {
  isLoading.value = true
  const params = {
    scope: props.scope,
    page: page.value,
    page_size: paginateBy.value,
    q: query.value,
    ordering: orderingString.value,
    playable: true
  }

  const measureLoading = logger.time('Fetching albums')
  try {
    const response = await axios.get('playlists/', {
      params
    })

    result.value = response.data
  } catch (error) {
    useErrorHandler(error as Error)
    result.value = undefined
  } finally {
    measureLoading()
    isLoading.value = false
  }
}
watch([page, q, ordering, orderingDirection, () => props.scope], fetchData)
fetchData()

const search = () => {
  page.value = 1
  q.value = query.value
}

onOrderingUpdate(() => {
  page.value = 1
  fetchData()
})

const { t } = useI18n()
const labels = computed(() => ({
  playlists: t('views.playlists.List.header.playlists'),
  searchPlaceholder: t('views.playlists.List.placeholder.search')
}))

const paginateOptions = computed(() => sortedUniq([12, 30, 50, paginateBy.value].sort((a, b) => a - b)))
</script>

<template>
  <Layout
    stack
    main
  >
    <!-- TODO: `yarn lint:tsc` doesn't understand the `Prop` type for `Header` while the language server does. It may be a question of typescript version... Investigate and fix! https://dev.funkwhale.audio/funkwhale/funkwhale/-/issues/2437 -->
    <!-- @vue-ignore -->
    <Header
      v-if="store.state.auth.authenticated"
      :h1="t('views.playlists.List.header.browse')"
      page-heading
      :action="{
        text: t('views.playlists.List.button.create'),
        // @ts-ignore
        icon: 'bi-plus',
        // @ts-ignore
        primary: true,
        // @ts-ignore
        onClick: () => { store.commit('playlists/showModal', true) }
      }"
    />
    <Header
      v-else
      page-heading
      :h1="t('views.playlists.List.header.browse')"
    />

    <!-- Search-bar -->
    <Layout
      form
      flex
      :class="['ui', {'loading': isLoading}, 'form']"
      @submit.prevent="search"
    >
      <Input
        id="playlists-search"
        v-model="query"
        search
        name="search"
        :label="t('views.playlists.List.label.search')"
        autofocus
        :placeholder="labels.searchPlaceholder"
      />
      <Layout
        stack
        no-gap
        label
        for="playlists-ordering"
      >
        <span class="label">
          {{ t('views.playlists.List.ordering.label') }}
        </span>
        <select
          id="playlists-ordering"
          v-model="ordering"
          class="dropdown"
        >
          <option
            v-for="(option, key) in orderingOptions"
            :key="key"
            :value="option[0]"
          >
            {{ sharedLabels.filters[option[1]] }}
          </option>
        </select>
      </Layout>
      <Layout
        stack
        no-gap
        label
        for="playlists-ordering-direction"
      >
        <span class="label">
          {{ t('views.playlists.List.ordering.direction.label') }}
        </span>
        <select
          id="playlists-ordering-direction"
          v-model="orderingDirection"
          class="dropdown"
        >
          <option value="+">
            {{ t('views.playlists.List.ordering.direction.ascending') }}
          </option>
          <option value="-">
            {{ t('views.playlists.List.ordering.direction.descending') }}
          </option>
        </select>
      </Layout>
      <Layout
        stack
        no-gap
        label
        for="playlist-results"
      >
        <span class="label">
          {{ t('views.playlists.List.pagination.results') }}
        </span>
        <select
          id="playlist-results"
          v-model="paginateBy"
          class="dropdown"
        >
          <option
            v-for="opt in paginateOptions"
            :key="opt"
            :value="opt"
          >
            {{ opt }}
          </option>
        </select>
      </Layout>
    </Layout>

    <Spacer v-if="result && result.results.length > 0" />

    <!-- Search results -->
    <Section :columns-per-item="3">
      <Loader v-if="isLoading" />
      <Alert
        v-if="result && result.results.length === 0"
        blue
        style="grid-column: 1 / -1;"
      >
        {{ t('views.playlists.List.empty.noResults') }}
        <Spacer />
        <Button
          v-if="store.state.auth.authenticated"
          icon="bi-list"
          primary
          @click="store.commit('playlists/showModal', true)"
        >
          {{ t('views.playlists.List.button.create') }}
        </Button>
      </Alert>
      <Pagination
        v-if="page && result && result.count > paginateBy"
        v-model:page="page"
        style="grid-column: 1 / -1;"
        :pages="Math.ceil(result.count/paginateBy)"
      />
      <PlaylistsCard
        v-for="playlist in (result && result.results.length > 0 ? result.results : [])"
        :key="playlist.uuid"
        :playlist="playlist"
      />
      <Spacer grow />
      <Pagination
        v-if="page && result && result.count > paginateBy"
        v-model:page="page"
        :pages="Math.ceil(result.count/paginateBy)"
        style="grid-column: 1 / -1;"
      />
    </Section>
  </Layout>
</template>
