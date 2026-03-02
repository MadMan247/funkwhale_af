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
import { useDataStore } from '~/ui/stores/data'
import { useUrlParamStore } from '~/ui/stores/urlParam.ts'

import PlaylistsCard from '~/components/playlists/Card.vue'
import Pagination from '~/components/ui/Pagination.vue'

import Alert from '~/components/ui/Alert.vue'
import Button from '~/components/ui/Button.vue'
import Header from '~/components/ui/Header.vue'
import Input from '~/components/ui/Input.vue'
import Layout from '~/components/ui/Layout.vue'
import Loader from '~/components/ui/Loader.vue'
import Nav from '~/components/ui/Nav.vue'
import Section from '~/components/ui/Section.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Select from '~/components/ui/Select.vue'

const props = defineProps<OrderingProps>()

const store = useStore()
const { t } = useI18n()

// Query

const tabs = [
  { title: t("components.library.Artists.tabs.me"), name: 'me' },
  { title: t("components.library.Artists.tabs.subscribed"), name: 'from_subscribed' },
  { title: t("components.library.Artists.tabs.domain"), name: `domain:${store.getters['instance/domain']}` },
  { title: t("components.library.Artists.tabs.all"), name: 'all' }
]
const scope = useUrlParamStore('scope', {
  persistence: 'localStorage',
  allowedValues: [undefined, 'subscribed', ...tabs.map(t => t.name)] as const
})
if (scope.value === 'subscribed')
  scope.value = 'from_subscribed'
else if (!scope.value)
  scope.value = 'me'

const q = useRouteQuery('query', '')
const query = ref(q.value)
syncRef(q, query, { direction: 'ltr' })

// Pagination

const page = usePage()

const orderingOptions = {
  creation_date: useSharedLabels().filters.creation_date,
  modification_date: useSharedLabels().filters.modification_date,
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

watch([q, ordering, orderingDirection, scope], () => {
  // Reset page when params have changed
  page.value = 1
})

// Search result

const playlists = computed(() => useDataStore().playlists({
    scope: scope.value,
    page: page.value,
    page_size: paginateBy.value,
    q: query.value,
    // Type for `ordering` field is loose in this schema, unlike in Artists and Albums params
    ordering: orderingString.value,
    playable: true
}, {
  refetchSignal: store.state.moderation.lastUpdate
}).value)
</script>

<template>
  <Layout
    v-title="t('views.playlists.List.header.playlists')"
    main
    stack
  >
    <Header
      v-if="store.state.auth.authenticated"
      page-heading
      :h1="t('views.playlists.List.header.browse')"
      :action="{
        text: t('views.playlists.List.button.create'),
        icon: 'bi-plus',
        primary: true,
        onClick: () => { store.commit('playlists/showModal', true) }
      }"
    />
    <Header
      v-else
      page-heading
      :h1="t('views.playlists.List.header.browse')"
    />

    <!-- Filters -->

    <Layout
      flex
      form
      @submit.prevent="playlists.refetch"
    >
      <Input
        id="playlists-search"
        v-model="query"
        search
        name="search"
        :label="t('views.playlists.List.label.search')"
        autofocus
        :placeholder="t('views.playlists.List.placeholder.search')"
      />
      <Select
        v-model="ordering"
        :options="orderingOptions"
        :label="t('views.playlists.List.ordering.label')"
        style="flex-grow: 0"
      />
      <Select
        v-model="orderingDirection"
        :options="directionOptions"
        :label="t('views.playlists.List.ordering.direction.label')"
        style="flex-grow: 0"
      />
      <Select
        v-model="paginateBy"
        :options="paginateOptions"
        :label="t('views.playlists.List.pagination.results')"
        style="flex-grow: 0"
      />
    </Layout>

    <!-- Results -->

    <Nav
      :model-value="tabs"
      tab-query-field="scope"
    >
      <Spacer v-if="playlists.data && playlists.data.count > 0" />

      <Section :columns-per-item="3">
        <Loader v-if="playlists.status === 'loading'" />
        <Alert
          v-else-if="playlists.status === 'error'"
          red
          style="grid-column: 1 / -1;"
        >
          <i class="exclamation triangle icon" />
          {{ playlists.error }}
        </Alert>
        <Alert
          v-else-if="playlists.data?.count === 0"
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
        <template v-if="playlists.data">
          <Pagination
            v-if="page && playlists.data.count > paginateBy"
            v-model:page="page"
            style="grid-column: 1 / -1;"
            :pages="Math.ceil(playlists.data.count/paginateBy)"
          />
          <PlaylistsCard
            v-for="playlist in playlists.data.results"
            :key="playlist.uuid"
            :playlist="playlist"
          />
          <Spacer grow />
          <Pagination
            v-if="page && playlists.data.count > paginateBy"
            v-model:page="page"
            :pages="Math.ceil(playlists.data.count/paginateBy)"
            style="grid-column: 1 / -1;"
          />
        </template>
      </Section>
    </Nav>
  </Layout>
</template>
