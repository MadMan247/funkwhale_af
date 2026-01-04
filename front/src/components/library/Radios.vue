<script setup lang="ts">
import type { OrderingProps } from '~/composables/navigation/useOrdering'
import type { Radio, BackendResponse } from '~/types'
import type { RouteRecordName } from 'vue-router'
import type { OrderingField } from '~/store/ui'

import { computed, ref, watch } from 'vue'
import { useRouteQuery } from '@vueuse/router'
import { useI18n } from 'vue-i18n'
import { syncRef } from '@vueuse/core'
import { sortedUniq } from 'lodash-es'
import { useStore } from '~/store'

import axios from 'axios'

import Layout from '~/components/ui/Layout.vue'
import Header from '~/components/ui/Header.vue'
import Section from '~/components/ui/Section.vue'
import Pagination from '~/components/ui/Pagination.vue'
import RadioCard from '~/components/radios/Card.vue'
import Alert from '~/components/ui/Alert.vue'
import Input from '~/components/ui/Input.vue'
import Link from '~/components/ui/Link.vue'
import Spacer from '~/components/ui/Spacer.vue'

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

const props = withDefaults(defineProps<Props>(), {
  scope: 'all',
  orderingConfigName: undefined
})

const page = usePage()

const q = useRouteQuery('query', '')
const query = ref(q.value)
syncRef(q, query, { direction: 'ltr' })

const result = ref<BackendResponse<Radio>>()

const orderingOptions: [OrderingField, keyof typeof sharedLabels.filters][] = [
  ['creation_date', 'creation_date'],
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
    name__icontains: query.value,
    ordering: orderingString.value
  }

  const measureLoading = logger.time('Fetching radios')
  try {
    const response = await axios.get('radios/radios/', {
      params
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

const store = useStore()
const isAuthenticated = computed(() => store.state.auth.authenticated)
const hasFavorites = computed(() => store.state.favorites.count > 0)

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
  searchPlaceholder: t('components.library.Radios.placeholder.search'),
  title: t('components.library.Radios.title')
}))

const paginateOptions = computed(() => sortedUniq([12, 25, 50, paginateBy.value].sort((a, b) => a - b)))
</script>

<template>
  <Layout
    v-title="labels.title"
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
        :type="'random'"
      />
      <radio-card :type="'recently-added'" />
      <radio-card
        v-if="store.state.auth.authenticated && scope === 'all'"
        :type="'less-listened'"
      />
    </Section>
    <Section
      v-if="isAuthenticated"
      align-left
      :columns-per-item="3"
      :h2="t('components.library.Radios.header.yours')"
    >
      <radio-card
        :type="'random_library'"
      />
      <radio-card
        v-if="isAuthenticated && hasFavorites"
        :type="'favorites'"
      />
      <radio-card
        :type="'less-listened_library'"
      />
    </Section>
    <Section
      :h2="t('components.library.Radios.header.user')"
      align-left
      :action="{
        to: { name: 'library.radios.build' },
        text: t('components.library.Radios.button.create'),
        icon: 'bi-plus',
        solid: true,
        primary: true,
        disabled: !store.state.auth.authenticated || undefined
      }"
    >
      <Layout
        flex
        form
        full
        :class="['ui', {'loading': isLoading}, 'form']"
        @submit.prevent="search"
      >
        <Input
          id="radios-search"
          v-model="query"
          search
          name="search"
          :label="t('components.library.Radios.label.search')"
          :placeholder="labels.searchPlaceholder"
        />
        <Layout
          stack
          no-gap
          label
          for="radios-ordering"
        >
          <span class="label">
            {{ t('components.library.Radios.ordering.label') }}
          </span>
          <select
            id="radios-ordering"
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
          for="radios-ordering-direction"
        >
          <span class="label">
            {{ t('components.library.Radios.ordering.direction.label') }}
          </span>
          <select
            id="radios-ordering-direction"
            v-model="orderingDirection"
            class="dropdown"
          >
            <option value="+">
              {{ t('components.library.Radios.ordering.direction.ascending') }}
            </option>
            <option value="-">
              {{ t('components.library.Radios.ordering.direction.descending') }}
            </option>
          </select>
        </Layout>
        <Layout
          stack
          no-gap
          label
          for="radios-results"
        >
          <span class="label">
            {{ t('components.library.Radios.pagination.results') }}
          </span>
          <select
            id="radios-results"
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
      <Alert
        v-if="result && result.results.length === 0"
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
          style="align-self:center;"
          :to="{name: 'library.radios.build'}"
          icon="bi-boombox-fill"
        >
          {{ t('components.library.Radios.button.add') }}
        </Link>
      </Alert>
      <Layout
        v-if="result && result.results.length > 0"
        full
        flex
      >
        <Pagination
          v-if="page && result && result.count > paginateBy"
          v-model:page="page"
          :pages="Math.ceil(result.count / paginateBy)"
        />
        <radio-card
          v-for="radio in result.results"
          :key="radio.id"
          type="custom"
          :custom-radio="radio"
        />
        <Pagination
          v-if="page && result && result.count > paginateBy"
          v-model:page="page"
          :pages="Math.ceil(result.count / paginateBy)"
        />
      </Layout>
    </Section>
  </Layout>
</template>
