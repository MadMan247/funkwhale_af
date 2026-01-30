<script setup lang="ts">
import type { OrderingProps } from '~/composables/navigation/useOrdering'
import type { RouteRecordName } from 'vue-router'
import type { OrderingField } from '~/store/ui'
import type { UserTrackFavorite } from '~/types'

import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { sortedUniq } from 'lodash-es'
import { useStore } from '~/store'

import axios from 'axios'

import TrackTable from '~/components/audio/track/Table.vue'
import RadioButton from '~/components/radios/Button.vue'
import Layout from '~/components/ui/Layout.vue'
import Header from '~/components/ui/Header.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Link from '~/components/ui/Link.vue'
import Alert from '~/components/ui/Alert.vue'
import Pagination from '~/components/ui/Pagination.vue'
import Loader from '~/components/ui/Loader.vue'

import useSharedLabels from '~/composables/locale/useSharedLabels'
import useOrdering from '~/composables/navigation/useOrdering'
import useErrorHandler from '~/composables/useErrorHandler'
import usePage from '~/composables/navigation/usePage'
import useLogger from '~/composables/useLogger'

interface Props extends OrderingProps {
  // TODO(wvffle): Remove after https://github.com/vuejs/core/pull/4512 is merged
  orderingConfigName?: RouteRecordName
}

const props = withDefaults(defineProps<Props>(), {
  defaultPage: 1,
  orderingConfigName: undefined
})

const store = useStore()

const page = usePage()

const orderingOptions: [OrderingField, keyof typeof sharedLabels.filters][] = [
  ['creation_date', 'creation_date'],
  ['title', 'track_title'],
  ['album__title', 'album_title'],
  ['artist__name', 'artist_name']
]

const logger = useLogger()
const sharedLabels = useSharedLabels()

const { onOrderingUpdate, orderingString, paginateBy, ordering, orderingDirection } = useOrdering(props)

const results = reactive<UserTrackFavorite[]>([])
const nextLink = ref()
const previousLink = ref()
const count = ref(0)

const isLoading = ref(false)
const fetchFavorites = async () => {
  isLoading.value = true

  const params = {
    page: page.value,
    page_size: paginateBy.value,
    ordering: orderingString.value,
    scope: "me"
  }

  const measureLoading = logger.time('Loading user favorites')
  try {
    const response = await axios.get('favorites/tracks/', { params })

    results.length = 0
    results.push(...response.data.results)

    for (const trackfavorite of results) {
      store.commit('favorites/track', { id: trackfavorite.track.id, value: true })
    }

    count.value = response.data.count
    nextLink.value = response.data.next
    previousLink.value = response.data.previous
  } catch (error) {
    useErrorHandler(error as Error)
  } finally {
    measureLoading()
    isLoading.value = false
  }
}

onMounted(() => {
  fetchFavorites()
})

watch([() => paginateBy, page],
  () => fetchFavorites(),
  { deep: true }
)

onOrderingUpdate(() => {
  page.value = 1
  fetchFavorites()
})

const { t } = useI18n()
const labels = computed(() => ({
  title: t('components.favorites.List.title')
}))

const paginateOptions = computed(() => sortedUniq([12, 25, 50, paginateBy.value].sort((a, b) => a - b)))
</script>

<template>
  <Layout
    v-title="labels.title"
    main
    stack
    no-gap
    align-left
  >
    <Header
      page-heading
      :h1="labels.title"
    >
      <template #action>
        <RadioButton
          v-if="store.state.favorites.count > 0"
          type="favorites"
        />
      </template>
    </Header>

    <Loader v-if="isLoading" />
    <Layout
      v-if="store.state.favorites.count > 0"
      form
      stack
      :class="['ui', { 'loading': isLoading }, 'form']"
    >
      <Spacer no-size />
      <Layout
        flex
        style="justify-content: flex-end;"
      >
        <Layout
          stack
          no-gap
          label
          for="favorites-ordering"
        >
          <span class="label">
            {{ t('components.favorites.List.ordering.label') }}
          </span>
          <select
            id="favorites-ordering"
            v-model="ordering"
            class="dropdown"
          >
            <option
              v-for="option in orderingOptions"
              :key="option[0]"
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
          for="favorites-ordering-direction"
        >
          <span class="label">
            {{ t('components.favorites.List.ordering.direction.label') }}
          </span>
          <select
            id="favorites-ordering-direction"
            v-model="orderingDirection"
            class="dropdown"
          >
            <option value="+">
              {{ t('components.favorites.List.ordering.direction.ascending') }}
            </option>
            <option value="-">
              {{ t('components.favorites.List.ordering.direction.descending') }}
            </option>
          </select>
        </Layout>
        <Layout
          stack
          no-gap
          label
          for="favorites-results"
        >
          <span class="label">
            {{ t('components.favorites.List.pagination.results') }}
          </span>
          <select
            id="favorites-results"
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
      <Pagination
        v-if="page && results && count > paginateBy"
        v-model:page="page"
        :pages="Math.ceil((count || 0) / paginateBy)"
        style="grid-column: 1 / -1;"
      />
      <TrackTable
        v-if="results"
        :search="true"
        :show-artist="true"
        :show-album="true"
        :tracks="results.map(r => r.track)"
      />
    </Layout>
    <Alert
      v-else-if="!isLoading"
      blue
      align-items="center"
    >
      <i
        class="bi bi-heartbreak-fill"
        style="font-size: 100px;"
      />
      <Spacer />
      {{ t('components.favorites.List.empty.noFavorites') }}
      <Spacer :size="32" />
      <Link
        to="/library"
        solid
        primary
        icon="bi-headphones"
      >
        {{ t('components.favorites.List.link.library') }}
      </Link>
    </Alert>
  </Layout>
</template>
