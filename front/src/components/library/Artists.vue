<script setup lang="ts">
import { syncRef } from '@vueuse/core'
import { useRouteQuery } from '@vueuse/router'
import { sortedUniq } from 'lodash-es'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import useSharedLabels from '~/composables/locale/useSharedLabels'
import type { OrderingProps } from '~/composables/navigation/useOrdering'
import useOrdering from '~/composables/navigation/useOrdering'
import usePage from '~/composables/navigation/usePage'
import { useStore } from '~/store'
import type { OrderingField } from '~/store/ui'
import { useModal } from '~/ui/composables/useModal.ts'
import { useDataStore } from '~/ui/stores/data'
import { useUrlParamStore } from '~/ui/stores/urlParam.ts'

import ArtistCard from '~/components/artist/Card.vue'

import Alert from '~/components/ui/Alert.vue'
import Card from '~/components/ui/Card.vue'
import Header from '~/components/ui/Header.vue'
import Input from '~/components/ui/Input.vue'
import Layout from '~/components/ui/Layout.vue'
import Loader from '~/components/ui/Loader.vue'
import Nav from '~/components/ui/Nav.vue'
import Pagination from '~/components/ui/Pagination.vue'
import Pills from '~/components/ui/Pills.vue'
import Select from '~/components/ui/Select.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Toggle from '~/components/ui/Toggle.vue'

const props = defineProps<OrderingProps>()

const { t } = useI18n()
const store = useStore()

// Query

const tabs = [
  { title: t("components.library.Artists.tabs.me"), name: 'me' },
  { title: t("components.library.Artists.tabs.subscribed"), name: 'from_subscribed' },
  { title: t("components.library.Artists.tabs.domain"), name: `domain:${store.getters['instance/domain']}` },
  { title: t("components.library.Artists.tabs.all"), name: 'all' }
]
const scope = useUrlParamStore('scope', {
  allowedValues: [undefined, 'subscribed', ...tabs.map(t => t.name)] as const
})
if (scope.value === 'subscribed')
  scope.value = 'from_subscribed'
else if (!scope.value)
  scope.value = 'all'

const tags = useUrlParamStore('tag', { scope: 'route', allowedValues: 'array' })

const q = useRouteQuery('query', '')
const query = ref(q.value)
syncRef(q, query, { direction: 'ltr' })

const has_albums = useUrlParamStore('has_albums', { allowedValues: [undefined, 'true', 'false'] as const })
if (!has_albums.value)
  has_albums.value='true'
const isCompilationExcluded = computed({
  get: () => has_albums.value === 'true',
  set: v => has_albums.value = v ? 'true' : 'false'
})

// Pagination

const page = usePage()

const orderingOptions = {
  creation_date: useSharedLabels().filters.creation_date,
  name: useSharedLabels().filters.name
} satisfies Partial<Record<OrderingField, string>>

const directionOptions = {
  '+':  t('components.library.Artists.ordering.direction.ascending'),
  '-': t('components.library.Artists.ordering.direction.descending')
}

const { orderingString, paginateBy, ordering, orderingDirection } = useOrdering(props)

const paginateOptions = computed<Record<number, string>>(() => Object.fromEntries(sortedUniq([
  12,
  30,
  50,
  paginateBy.value
].toSorted((a, b) => a - b)).map(v => [v, String(v)])))

watch([q, tags, ordering, has_albums, scope], () => {
  // Reset page when params have changed
  page.value = 1
})

// Search result

const artists = computed(() => useDataStore().artists({
  scope: scope.value,
  page: page.value,
  page_size: paginateBy.value,
  q: query.value,
  // @ts-expect-error `useOrdering` types are too loose, need strict type
  ordering: orderingString.value,
  playable: true,
  tag: tags.value,
  include_channels: true,
  content_category: 'music',
  has_albums: isCompilationExcluded.value
}, {
  refetchSignal: store.state.moderation.lastUpdate
}).value)
</script>

<template>
  <Layout
    v-title="t('components.library.Artists.title')"
    main
    stack
  >
    <Header
      page-heading
      :h1="t('components.library.Artists.header.browse')"
    />
    <Spacer />

    <!-- Filters -->

    <Layout
      flex
      form
      @submit.prevent="artists.refetch"
    >
      <Input
        id="artist-search"
        v-model="query"
        search
        name="search"
        :label="t('components.library.Artists.label.search')"
        autofocus
        :placeholder="t('components.library.Artists.placeholder.search')"
      />
      <Pills
        v-if="typeof tags === 'object'"
        :get="model => { tags = model.currents.map(({ label }) => label) }"
        :set="_ => ({
          currents: tags.map(tag => ({ type: 'custom' as const, label: tag })),
          others: useDataStore().tags().value
            .filter(({ name }) => artists.data?.results?.some(object => object.tags.includes(name)) && !tags.includes(name))
            .map(({ name }) => ({ type: 'preset' as const, label: name })),
        })"
        :label="t('components.library.Artists.label.tags')"
        style="max-width: 350px;"
      />
      <Select
        v-model="ordering"
        :options="orderingOptions"
        :label="t('components.library.Artists.ordering.label')"
        style="flex-grow: 0"
      />
      <Select
        v-model="orderingDirection"
        :options="directionOptions"
        :label="t('components.library.Artists.ordering.direction.label')"
        style="flex-grow: 0"
      />
      <Select
        v-model="paginateBy"
        :options="paginateOptions"
        :label="t('components.library.Artists.pagination.results')"
        style="flex-grow: 0"
      />
    </Layout>
    <Toggle
      v-model="isCompilationExcluded"
      :label="t('components.library.Artists.label.excludeCompilation')"
    />

    <!-- Results -->

    <Nav
      :model-value="tabs"
      tab-query-field="scope"
    >
      <Loader v-if="artists.status === 'loading'" />
      <Alert
        v-else-if="artists.status === 'error'"
        red
      >
        <i class="exclamation triangle icon" />
        {{ artists.error }}
      </Alert>
      <template v-if="artists.data">
        <Pagination
          v-if="page && artists.data.count > paginateBy"
          v-model:page="page"
          :pages="Math.ceil(artists.data.count / paginateBy)"
        />
        <Layout
          v-if="artists.data?.count > 0"
          flex
        >
          <ArtistCard
            v-for="artist in artists.data.results"
            :key="artist.id"
            :artist
          />
        </Layout>
        <Layout
          v-else-if="artists.data?.count === 0"
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
          v-if="page && artists.data && artists.data.count > paginateBy"
          v-model:page="page"
          :pages="Math.ceil(artists.data.count / paginateBy)"
        />
      </template>
    </Nav>
  </Layout>
</template>
