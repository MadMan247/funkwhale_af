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
import { useUrlParamStore } from '~/ui/stores/urlParam'

import AlbumCard from '~/components/album/Card.vue'

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

const props = defineProps<OrderingProps>()

const { t } = useI18n()
const store = useStore()

// Query

const tabs = [
  { title: t("components.library.Albums.tabs.me"), name: 'me' },
  { title: t("components.library.Albums.tabs.subscribed"), name: 'from_subscribed' },
  { title: t("components.library.Albums.tabs.domain"), name: 'domain:' + store.getters['instance/domain'] },
  { title: t("components.library.Albums.tabs.all"), name: 'all' }
]
const scope = useUrlParamStore('scope', {
  allowedValues: [undefined, 'subscribed', ...tabs.map(t => t.name)] as const
})
if (scope.value === 'subscribed')
 scope.value = 'from_subscribed'
else if (!scope.value)
  scope.value = 'me'

const tags = useUrlParamStore('tag', { scope: 'route', allowedValues: 'array' })

const q = useRouteQuery('query', '')
const query = ref(q.value)
syncRef(q, query, { direction: 'ltr' })

// Pagination

const page = usePage()

const orderingOptions = {
  creation_date: useSharedLabels().filters.creation_date,
  title: useSharedLabels().filters.album_title,
  release_date: useSharedLabels().filters.release_date
} satisfies Partial<Record<OrderingField, string>>

const directionOptions = {
  '+': t('components.library.Albums.ordering.direction.ascending'),
  '-': t('components.library.Albums.ordering.direction.descending')
}

const { orderingString, paginateBy, ordering, orderingDirection } = useOrdering(props)

const paginateOptions = computed<Record<number, string>>(() => Object.fromEntries(sortedUniq([
  12,
  30,
  50,
  paginateBy.value
].toSorted((a, b) => a - b)).map(v => [v, String(v)])))

watch([q, tags, ordering, scope], () => {
  // Reset page when params have changed
  page.value = 1
})

// Search result

const albums = computed(() => useDataStore().albums({
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
}, {
  refetchSignal: store.state.moderation.lastUpdate
}).value)
</script>

<template>
  <!-- TODO: Consider using the URL params directly here - so that users can specify params not exposed in the UI -->
  <Layout
    v-title="t('components.library.Albums.title')"
    stack
    main
  >
    <Header
      page-heading
      :h1="t('components.library.Albums.header.browse')"
    />
    <Spacer />

    <!-- Filters -->

    <Layout
      flex
      form
      @submit.prevent="albums.refetch"
    >
      <Input
        id="album-search"
        v-model="query"
        search
        name="search"
        :label="t('components.library.Albums.label.search')"
        autofocus
        :placeholder="t('components.library.Albums.placeholder.search')"
      />
      <Pills
        :get="model => { tags = model.currents.map(({ label }) => label) }"
        :set="_ => ({
          currents: tags.map(tag => ({ type: 'preset' as const, label: tag })),
          others: useDataStore().tags().value
            .filter(({ name }) => albums.data?.results?.some((object) => object.tags.includes(name)) && !tags.includes(name))
            .map(({ name }) => ({ type: 'preset' as const, label: name })),
        })"
        :label="t('components.library.Albums.label.tags')"
        style="max-width: 350px;"
      />
      <Select
        v-model="ordering"
        :options="orderingOptions"
        :label="t('components.library.Albums.ordering.label')"
        style="flex-grow: 0"
      />
      <Select
        v-model="orderingDirection"
        :options="directionOptions"
        :label="t('components.library.Albums.ordering.direction.label')"
        style="flex-grow: 0"
      />
      <Select
        v-model="paginateBy"
        :options="paginateOptions"
        :label="t('components.library.Albums.pagination.results')"
        style="flex-grow: 0"
      />
    </Layout>

    <!-- Results -->

    <Nav
      :model-value="tabs"
      tab-query-field="scope"
    >
      <Loader v-if="albums.status === 'loading'" />
      <Alert
        v-else-if="albums.status === 'error'"
        red
      >
        <i class="exclamation triangle icon" />
        {{ albums.error }}
      </Alert>
      <template v-if="albums.data">
        <Pagination
          v-if="page && albums.data.count > paginateBy"
          v-model:page="page"
          :pages="Math.ceil((albums.data.count || 0)/paginateBy)"
        />
        <Layout
          v-if="albums.data.count > 0"
          flex
        >
          <AlbumCard
            v-for="album in albums.data.results"
            :key="album.id"
            :album
          />
        </Layout>
        <Layout
          v-else-if="albums.data.count === 0"
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
          v-if="page && albums.data.count > paginateBy"
          v-model:page="page"
          :pages="Math.ceil((albums.data.count || 0)/paginateBy)"
        />
      </template>
    </Nav>
  </Layout>
</template>
