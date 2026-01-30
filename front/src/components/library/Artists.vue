<script setup lang="ts">
import type { OrderingProps } from '~/composables/navigation/useOrdering'
import type { Artist, BackendResponse } from '~/types'
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

import ArtistCard from '~/components/artist/Card.vue'
import Pagination from '~/components/ui/Pagination.vue'
import Card from '~/components/ui/Card.vue'
import Layout from '~/components/ui/Layout.vue'
import Header from '~/components/ui/Header.vue'
import Input from '~/components/ui/Input.vue'
import Toggle from '~/components/ui/Toggle.vue'
import Nav from '~/components/ui/Nav.vue'
import Alert from '~/components/ui/Alert.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Pills from '~/components/ui/Pills.vue'
import Section from '~/components/ui/Section.vue'
import Loader from '~/components/ui/Loader.vue'

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

const tags = useRouteQuery<string[]>('tag', [])

const q = useRouteQuery('query', '')
const query = ref(q.value)
syncRef(q, query, { direction: 'ltr' })

const result = ref<BackendResponse<Artist>>()
const excludeCompilation = ref(true)

const { t } = useI18n()

const orderingOptions: [OrderingField, keyof typeof sharedLabels.filters][] = [
  ['creation_date', 'creation_date'],
  ['name', 'name']
]

const logger = useLogger()
const sharedLabels = useSharedLabels()

const { onOrderingUpdate, orderingString, paginateBy, ordering, orderingDirection } = useOrdering(props)

const scope = useUrlParamCache('scope', { fallback: props.scope })
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

const isLoading = ref(false)
const fetchData = async () => {
  isLoading.value = true
  const params = {
    scope: scope.value,
    page: page.value,
    page_size: paginateBy.value,
    q: query.value,
    ordering: orderingString.value,
    playable: 'true',
    tag: tags.value,
    include_channels: 'true',
    content_category: 'music',
    has_albums: excludeCompilation.value
  }

  const measureLoading = logger.time('Fetching artists')
  try {
    const response = await axios.get('artists/', {
      params,
      paramsSerializer: {
        indexes: null
      }
    })

    result.value = response.data
  } catch (error) {
    useErrorHandler(error as Error)
    result.value = undefined
    setTimeout(() => page.value = 1, 1000)
  } finally {
    measureLoading()
    isLoading.value = false
  }
}

const paginateOptions = computed(() => sortedUniq([12, 30, 50, paginateBy.value].sort((a, b) => a - b)))

const store = useStore()
const dataStore = useDataStore()

const tabs = ref([
  { title: t("components.library.Artists.tabs.me"), name: 'me' },
  { title: t("components.library.Artists.tabs.subscribed"), name: 'from_subscribed' },
  { title: t("components.library.Artists.tabs.domain"), name: 'domain:' + store.getters['instance/domain'] },
  { title: t("components.library.Artists.tabs.all"), name: 'all' }
])

watch([() => store.state.moderation.lastUpdate, excludeCompilation], fetchData)
watch([page, tags, q, ordering, orderingDirection, scope], () => {
  fetchData()
})
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
  searchPlaceholder: t('components.library.Artists.placeholder.search'),
  title: t('components.library.Artists.title')
}))
</script>

<template>
  <Layout
    v-title="labels.title"
    main
    stack
  >
    <Header
      :h1="t('components.library.Artists.header.browse')"
      page-heading
    />
    <Section>
      <Layout
        form
        flex
        :class="['ui', { 'loading': isLoading }, 'form']"
        @submit.prevent="search"
      >
        <Input
          id="artist-search"
          v-model="query"
          search
          name="search"
          :label="t('components.library.Artists.label.search')"
          autofocus
          :placeholder="labels.searchPlaceholder"
        />
        <Pills
          v-if="typeof tags === 'object'"
          :get="model => { tags = model.currents.map(({ label }) => label) }"
          :set="model => ({
            currents: tags.map(tag => ({ type: 'custom' as const, label: tag })),
            others: dataStore.tags().value
              .filter(({ name }) => result?.results?.some((object) => object.tags?.includes(name)) && !tags.includes(name))
              .map(({ name }) => ({ type: 'preset' as const, label: name })),
          })"
          :label="t('components.library.Artists.label.tags')"
          style="max-width: 350px;"
        />
        <Layout
          stack
          no-gap
          label
          for="artist-ordering"
        >
          <span class="label">
            {{ t('components.library.Artists.ordering.label') }}
          </span>
          <select
            id="artist-ordering"
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
          for="artist-ordering-direction"
        >
          <span class="label">
            {{ t('components.library.Artists.ordering.direction.label') }}
          </span>
          <select
            id="artist-ordering-direction"
            v-model="orderingDirection"
            class="dropdown"
          >
            <option value="+">
              {{ t('components.library.Artists.ordering.direction.ascending') }}
            </option>
            <option value="-">
              {{ t('components.library.Artists.ordering.direction.descending') }}
            </option>
          </select>
        </Layout>
        <Layout
          stack
          no-gap
          label
          for="artist-results"
        >
          <span class="label">
            {{ t('components.library.Artists.pagination.results') }}
          </span>
          <select
            id="artist-results"
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
        <Toggle
          id="exclude-compilation"
          v-model="excludeCompilation"
          :label="t('components.library.Artists.label.excludeCompilation')"
          true-value="true"
          false-value="null"
          type="checkbox"
        />
      </Layout>
      <Nav
        v-model="tabs"
        tab-query-field="scope"
      >
        <Loader v-if="isLoading" />
        <Pagination
          v-if="page && result && result.count > paginateBy"
          v-model:page="page"
          :pages="Math.ceil(result.count / paginateBy)"
        />
        <Layout
          v-if="result && result.results.length > 0"
          grid
          style="display:flex; flex-wrap:wrap; gap: 32px; margin-top:32px;"
        >
          <ArtistCard
            v-for="artist in result.results"
            :key="artist.id"
            :artist="artist"
          />
        </Layout>
        <Layout
          v-else-if="result && result.results.length === 0"
          stack
        >
          <Alert yellow>
            <i class="compact disc icon" />
            {{ t('components.library.Artists.empty.noResults') }}
          </Alert>
          <Layout flex>
            <Card
              v-if="store.state.auth.authenticated"
              :title="t('components.library.Artists.button.upload')"
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
          :pages="Math.ceil(result.count / paginateBy)"
        />
      </Nav>
    </Section>
  </Layout>
</template>

<style scoped>
.label {
  margin-top: -18px;
  font-size: 14px;
  font-weight: 600;
}
</style>
