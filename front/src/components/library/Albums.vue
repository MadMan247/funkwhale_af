<script setup lang="ts">
import type { OrderingProps } from '~/composables/navigation/useOrdering'
import type { PaginatedAlbumList } from '~/types'
import type { operations } from '~/generated/types.ts'
import type { RouteRecordName } from 'vue-router'
import type { OrderingField } from '~/store/ui'

import { computed, ref, watch } from 'vue'
import { useRouteQuery } from '@vueuse/router'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { syncRef } from '@vueuse/core'
import { sortedUniq } from 'lodash-es'
import { useStore } from '~/store'
import { useDataStore } from '~/ui/stores/data'
import { useModal } from '~/ui/composables/useModal.ts'

import axios from 'axios'

import Pagination from '~/components/ui/Pagination.vue'
import Card from '~/components/ui/Card.vue'
import AlbumCard from '~/components/album/Card.vue'
import Layout from '~/components/ui/Layout.vue'
import Header from '~/components/ui/Header.vue'
import Input from '~/components/ui/Input.vue'
import Alert from '~/components/ui/Alert.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Pills from '~/components/ui/Pills.vue'
import Loader from '~/components/ui/Loader.vue'
import Nav from '~/components/ui/Nav.vue'

import useUrlParamCache from '~/ui/composables/useUrlParamCache.ts'
import useSharedLabels from '~/composables/locale/useSharedLabels'
import useOrdering from '~/composables/navigation/useOrdering'
import useErrorHandler from '~/composables/useErrorHandler'
import usePage from '~/composables/navigation/usePage'
import useLogger from '~/composables/useLogger'

interface Props extends OrderingProps {
  scope?: 'me' | 'from_subscribed' | 'domain' | 'all'

  // TODO(wvffle): Remove after https://github.com/vuejs/core/pull/4512 is merged
  orderingConfigName?: RouteRecordName
}

const props = withDefaults(defineProps<Props>(), {
  scope: 'me',
  orderingConfigName: undefined
})

const page = usePage()

const tags = useRouteQuery<string[]>('tag', [], { transform: (param: string[]) => param.filter(p => p.trim() !== '') })

const q = useRouteQuery('query', '')
const query = ref(q.value ?? '')
syncRef(q, query, { direction: 'ltr' })

const result = ref<PaginatedAlbumList>()

const { t } = useI18n()

const orderingOptions: [OrderingField, keyof typeof sharedLabels.filters][] = [
  ['creation_date', 'creation_date'],
  ['title', 'album_title'],
  ['release_date', 'release_date']
]

const logger = useLogger()
const sharedLabels = useSharedLabels()

const { onOrderingUpdate, orderingString, paginateBy, ordering, orderingDirection } = useOrdering(props)

const store = useStore()
const dataStore = useDataStore()

const tabs = ref([
  { title: t("components.library.Albums.tabs.me"), name: 'me' },
  { title: t("components.library.Albums.tabs.subscribed"), name: 'from_subscribed' },
  { title: t("components.library.Albums.tabs.domain"), name: 'domain:' + store.getters['instance/domain'] },
  { title: t("components.library.Albums.tabs.all"), name: 'all' }
])
const scope = useUrlParamCache('scope', { fallback: props.scope })

const isLoading = ref(false)
const fetchData = async () => {
  isLoading.value = true
  const params : operations['get_album_fetches']['parameters']['query'] = {
    scope: scope.value,
    page: page.value,
    page_size: paginateBy.value,
    q: query.value,
    // @ts-expect-error TODO: add strict types to useOrdering
    ordering: orderingString.value,
    playable: true,
    tag: tags.value,
    include_channels: true,
    include_tracks: false,
    content_category: 'music'
  }

  const measureLoading = logger.time('Fetching albums')
  try {
    const response = await axios.get<PaginatedAlbumList>('albums/', {
      params,
      paramsSerializer: {
        indexes: null
      }
    })

    result.value = response.data
  } catch (error) {
    useErrorHandler(error as Error)
    result.value = undefined
    setTimeout(()=> page.value = 1, 1000)
  } finally {
    measureLoading()
    isLoading.value = false
  }
}

watch(() => store.state.moderation.lastUpdate, fetchData)

watch([page, tags, q, ordering, orderingDirection, scope], () => {
  fetchData()
})

watch(scope, () => {
  page.value = 1
})

const route = useRoute()
const router = useRouter()

watch(() => route.query.scope, async (newScope) => {
  const scopeQuery = Array.isArray(newScope) ? newScope[0] : newScope
  if (!scopeQuery) {
    await router.replace({
      ...route,
      query: { ...route.query, scope: scope.value }
    })
  } else if (scopeQuery === 'subscribed') {
    await router.replace({
      ...route,
      query: { ...route.query, scope: 'from_subscribed' }
    })
  }
}, { immediate: true })

fetchData()

const search = () => {
  page.value = 1
  q.value = query.value
}

onOrderingUpdate(() => {
  page.value = 1
  fetchData()
})

const labels = computed(() => ({
  searchPlaceholder: t('components.library.Albums.placeholder.search'),
  title: t('components.library.Albums.title')
}))

const paginateOptions = computed(() => sortedUniq([12, 30, 50, paginateBy.value].sort((a, b) => a - b)))
</script>

<template>
  <Layout
    v-title="labels.title"
    stack
    main
  >
    <Header
      page-heading
      :h1="t('components.library.Albums.header.browse')"
    />
    <Layout
      form
      flex
      :class="['ui', {'loading': isLoading}, 'form']"
      @submit.prevent="search"
    >
      <Input
        id="album-search"
        v-model="query"
        search
        name="search"
        :label="t('components.library.Albums.label.search')"
        autofocus
        :placeholder="labels.searchPlaceholder"
      />
      <Pills
        v-if="typeof tags === 'object'"
        :get="model => { tags = model.currents.map(({ label }) => label) }"
        :set="model => ({
          currents: tags.map(tag => ({ type: 'preset' as const, label: tag })),
          others: dataStore.tags().value
            .filter(({ name }) => result?.results?.some((object) => object.tags?.includes(name)) && !tags.includes(name))
            .map(({ name }) => ({ type: 'preset' as const, label: name })),
        })"
        :label="t('components.library.Albums.label.tags')"
        style="max-width: 350px;"
      />
      <Layout
        stack
        no-gap
        label
        for="album-ordering"
      >
        <span class="label">
          {{ t('components.library.Albums.ordering.label') }}
        </span>
        <select
          id="album-ordering"
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
        for="album-ordering-direction"
      >
        <span class="label">
          {{ t('components.library.Albums.ordering.direction.label') }}
        </span>
        <select
          id="album-ordering-direction"
          v-model="orderingDirection"
          class="dropdown"
        >
          <option value="+">
            {{ t('components.library.Albums.ordering.direction.ascending') }}
          </option>
          <option value="-">
            {{ t('components.library.Albums.ordering.direction.descending') }}
          </option>
        </select>
      </Layout>
      <Layout
        stack
        no-gap
        label
        for="album-results"
      >
        <span class="label">
          {{ t('components.library.Albums.pagination.results') }}
        </span>
        <select
          id="album-results"
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

    <Nav
      v-model="tabs"
      tab-query-field="scope"
    >
      <Loader v-if="isLoading" />
      <Pagination
        v-if="page && result && result.count > paginateBy"
        v-model:page="page"
        :pages="Math.ceil((result.count || 0)/paginateBy)"
      />
      <Layout
        v-if="result && result.results.length > 0"
        grid
        style="display:flex; flex-wrap:wrap; gap: 32px; margin-top:32px;"
      >
        <AlbumCard
          v-for="album in result.results"
          :key="album.id"
          :album="album"
        />
      </Layout>
      <Layout
        v-else-if="result && result.results.length === 0"
        stack
      >
        <Alert blue>
          <i class="bi bi-disc" />
          {{ t('components.library.Albums.empty.noResults') }}
        </Alert>
        <Layout flex>
          <Card
            v-if="store.state.auth.authenticated"
            :title="t('components.library.Albums.link.addMusic')"
            primary
            style="text-align: center;"
            :to="useModal('upload').to"
          >
            <template #image>
              <i
                class="bi bi-upload"
                style="font-size: 100px; position: relative; top: 50px;"
              />
            </template>
          </Card>
        </Layout>
      </Layout>
      <Spacer grow />
      <Pagination
        v-if="page && result && result.count > paginateBy"
        v-model:page="page"
        :pages="Math.ceil((result.count || 0)/paginateBy)"
      />
    </Nav>
  </Layout>
</template>
