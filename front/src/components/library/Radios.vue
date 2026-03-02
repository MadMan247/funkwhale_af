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
import { useUrlParamStore } from '~/ui/stores/urlParam'

import RadioCard from '~/components/radios/Card.vue'
import Alert from '~/components/ui/Alert.vue'
import Header from '~/components/ui/Header.vue'
import Input from '~/components/ui/Input.vue'
import Layout from '~/components/ui/Layout.vue'
import Link from '~/components/ui/Link.vue'
import Loader from '~/components/ui/Loader.vue'
import Nav from '~/components/ui/Nav.vue'
import Pagination from '~/components/ui/Pagination.vue'
import Section from '~/components/ui/Section.vue'
import Select from '~/components/ui/Select.vue'
import Spacer from '~/components/ui/Spacer.vue'

const props = defineProps<OrderingProps>()

const store = useStore()
const { t } = useI18n()

// Query

const tabs = [
  { title: t("components.library.Radios.tabs.me"), name: 'me' },
  { title: t("components.library.Radios.tabs.domain"), name: 'all' }
]
const scope = useUrlParamStore('scope', {
  allowedValues: [undefined, ...tabs.map(t => t.name)] as const
})
if (!scope.value)
  scope.value = 'all'

const q = useRouteQuery('query', '')
const query = ref(q.value)
syncRef(q, query, { direction: 'ltr' })

// Pagination

const page = usePage()

const orderingOptions = {
  creation_date: useSharedLabels().filters.creation_date,
  name: useSharedLabels().filters.name
} satisfies Partial<Record<OrderingField, string>>

const directionOptions = {
  '+':  t('components.library.Radios.ordering.direction.ascending'),
  '-': t('components.library.Radios.ordering.direction.descending')
}

const { orderingString, paginateBy, ordering, orderingDirection } = useOrdering(props)

const paginateOptions = computed<Record<number, string>>(() => Object.fromEntries(sortedUniq([
  12,
  25, // This is inconsistent with the other pages
  50,
  paginateBy.value
].toSorted((a, b) => a - b)).map(v => [v, String(v)])))

watch([q, ordering, scope], () => {
  // Reset page when params have changed
  page.value = 1
})

// Search result

const radios = computed(() => useDataStore().radios({
  scope: scope.value,
  page: page.value,
  page_size: paginateBy.value,
  name__icontains: query.value,
  ordering: orderingString.value
}).value)
// TODO: Does this need an external refetch signal (store.state.moderation.lastUpdate)?
</script>

<template>
  <Layout
    v-title="t('components.library.Radios.title')"
    main
    stack
    gap-84
  >
    <Header
      page-heading
      :h1="t('components.library.Radios.header.browse')"
    />
    <Section
      align-left
      :columns-per-item="3"
      :h2="t('components.library.Radios.header.instance')"
    >
      <radio-card
        v-if="scope === 'all'"
        type="random"
      />
      <radio-card type="recently-added" />
      <radio-card
        v-if="store.state.auth.authenticated && scope === 'all'"
        type="less-listened"
      />
    </Section>
    <Section
      v-if="store.state.auth.authenticated"
      align-left
      :columns-per-item="3"
      :h2="t('components.library.Radios.header.yours')"
    >
      <radio-card
        :type="'random_library'"
      />
      <radio-card
        v-if="store.state.auth.authenticated && store.state.favorites.count>0"
        :type="'favorites'"
      />
      <radio-card
        :type="'less-listened_library'"
      />
    </Section>
    <Section
      :h2="t('components.library.Radios.header.user')"
      align-left
    >
      <template #action>
        <Link
          :to="{ name: 'library.radios.build' }"
          icon="bi-plus"
          solid
          primary
          disabled="!store.state.auth.authenticated || undefined"
        >
          {{ t('components.library.Radios.button.create') }}
        </Link>
      </template>
      <Spacer no-size />

      <!-- Filters -->

      <Layout
        flex
        form
        full
        @submit.prevent="radios.refetch"
      >
        <Input
          id="radios-search"
          v-model="query"
          search
          name="search"
          :label="t('components.library.Radios.label.search')"
          :placeholder="t('components.library.Radios.placeholder.search')"
        />
        <Select
          v-model="ordering"
          :options="orderingOptions"
          :label="t('components.library.Radios.ordering.label')"
          style="flex-grow: 0"
        />
        <Select
          v-model="orderingDirection"
          :options="directionOptions"
          :label="t('components.library.Radios.ordering.direction.label')"
          style="flex-grow: 0"
        />
        <Select
          v-model="paginateBy"
          :options="paginateOptions"
          :label="t('components.library.Radios.pagination.results')"
          style="flex-grow: 0"
        />
      </Layout>

      <!-- Results -->

      <Nav
        :model-value="tabs"
        tab-query-field="scope"
      >
        <Loader v-if="radios.status === 'loading'" />
        <Alert
          v-else-if="radios.status === 'error'"
          red
        >
          <i class="exclamation triangle icon" />
          {{ radios.error }}
        </Alert>
        <template v-if="radios.data">
          <Alert
            v-if="radios.data.count === 0"
            blue
            style="align-items: center; grid-column: 1 / -1;"
          >
            <i
              class="bi bi-broadcast-pin"
              style="font-size: 80px"
            />
            <Spacer />
            {{ t('components.library.Radios.empty.noResults') }}
            <Spacer />
            <Link
              v-if="store.state.auth.authenticated"
              primary
              style="align-self: center;"
              :to="{ name: 'library.radios.build' }"
              icon="bi-boombox-fill"
            >
              {{ t('components.library.Radios.button.add') }}
            </Link>
          </Alert>
          <Layout
            v-else-if="radios.data.count > 0"
            full
            flex
          >
            <Pagination
              v-if="page && radios.data.count > paginateBy"
              v-model:page="page"
              :pages="Math.ceil(radios.data.count / paginateBy)"
            />
            <radio-card
              v-for="radio in radios.data.results"
              :key="radio.id"
              type="custom"
              :custom-radio="radio"
            />
            <Pagination
              v-if="page && radios.data.count > paginateBy"
              v-model:page="page"
              :pages="Math.ceil(radios.data.count / paginateBy)"
            />
          </Layout>
        </template>
      </Nav>
    </Section>
  </Layout>
</template>
