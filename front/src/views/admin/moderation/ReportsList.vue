<script setup lang="ts">
import type { SmartSearchProps } from '~/composables/navigation/useSmartSearch'
import type { OrderingProps } from '~/composables/navigation/useOrdering'
import type { Report, BackendResponse } from '~/types'
import type { RouteRecordName } from 'vue-router'
import type { OrderingField } from '~/store/ui'

import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'

import axios from 'axios'

import ReportCategoryDropdown from '~/components/moderation/ReportCategoryDropdown.vue'
import ReportCard from '~/components/manage/moderation/ReportCard.vue'

import Layout from '~/components/ui/Layout.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Header from '~/components/ui/Header.vue'
import Input from '~/components/ui/Input.vue'
import Pagination from '~/components/ui/Pagination.vue'

import useSmartSearch from '~/composables/navigation/useSmartSearch'
import useSharedLabels from '~/composables/locale/useSharedLabels'
import useOrdering from '~/composables/navigation/useOrdering'
import useErrorHandler from '~/composables/useErrorHandler'
import usePage from '~/composables/navigation/usePage'
import useLogger from '~/composables/useLogger'

interface Props extends SmartSearchProps, OrderingProps {
  mode?: 'card'

  // TODO(wvffle): Remove after https://github.com/vuejs/core/pull/4512 is merged
  defaultQuery?: string
  orderingConfigName?: RouteRecordName
  updateUrl?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  defaultQuery: '',
  updateUrl: false,
  mode: 'card',
  orderingConfigName: undefined
})

const logger = useLogger()

const search = ref()

const result = ref<BackendResponse<Report>>()

const { onOrderingUpdate, orderingString, paginateBy, ordering, orderingDirection } = useOrdering(props)
const { onSearch, query, addSearchToken, getTokenValue } = useSmartSearch(props)

const page = usePage()
const pages = computed(() => result.value?.count ? Math.ceil(result.value.count / paginateBy.value) : 0)

const orderingOptions: [OrderingField, keyof typeof sharedLabels.filters][] = [
  ['creation_date', 'creation_date'],
  ['applied_date', 'applied_date']
]

const store = useStore()
const isLoading = ref(false)
const fetchData = async () => {
  isLoading.value = true
  const params = {
    page: page.value,
    page_size: paginateBy.value,
    q: query.value,
    ordering: orderingString.value
  }

  try {
    const response = await axios.get('manage/moderation/reports/', {
      params
    })

    result.value = response.data
    if (query.value === 'resolved:no') {
      logger.log('Refreshing sidebar notifications')
      store.commit('ui/incrementNotifications', {
        type: 'pendingReviewReports',
        value: response.data.count
      })
    }
  } catch (error) {
    useErrorHandler(error as Error)
    result.value = undefined
  } finally {
    isLoading.value = false
  }
}

onSearch(() => (page.value = 1))
watch([page, query], fetchData)
onOrderingUpdate(fetchData)
fetchData()

const { t } = useI18n()
const sharedLabels = useSharedLabels()
const labels = computed(() => ({
  searchPlaceholder: t('views.admin.moderation.ReportsList.placeholder.search'),
  reports: t('views.admin.moderation.ReportsList.title')
}))
</script>

<template>
  <Layout
    v-title="labels.reports"
    stack
  >
    <Header
      page-heading
      :h1="t('views.admin.moderation.ReportsList.header.reports')"
    />
    <div class="ui inline form">
      <div class="fields">
        <div class="ui field">
          <label for="reports-search">{{ t('views.admin.moderation.ReportsList.label.search') }}</label>
          <form @submit.prevent="query = search.value">
            <Input
              id="reports-search"
              ref="search"
              v-model="query"
              name="search"
              search
              :placeholder="labels.searchPlaceholder"
            />
          </form>
        </div>
        <Spacer :size="16" />
        <Layout
          flex
        >
          <Spacer grow />
          <div class="field">
            <label for="reports-status">{{ t('views.admin.moderation.ReportsList.label.status') }}</label>
            <select
              id="reports-status"
              class="ui dropdown"
              :value="getTokenValue('resolved', '')"
              @change="addSearchToken('resolved', ($event.target as HTMLSelectElement).value)"
            >
              <option value="">
                {{ t('views.admin.moderation.ReportsList.option.status.all') }}
              </option>
              <option value="yes">
                {{ t('views.admin.moderation.ReportsList.option.status.resolved') }}
              </option>
              <option value="no">
                {{ t('views.admin.moderation.ReportsList.option.status.unresolved') }}
              </option>
            </select>
          </div>
          <report-category-dropdown
            class="field"
            :all="true"
            :label="true"
            :model-value="getTokenValue('category', '')"
            @update:model-value="addSearchToken('category', $event)"
          />
          <div class="field">
            <label for="reports-ordering">{{ t('views.admin.moderation.ReportsList.ordering.label') }}</label>
            <select
              id="reports-ordering"
              v-model="ordering"
              class="ui dropdown"
            >
              <option
                v-for="(option, key) in orderingOptions"
                :key="key"
                :value="option[0]"
              >
                {{ sharedLabels.filters[option[1]] }}
              </option>
            </select>
          </div>
          <div class="field">
            <label for="reports-ordering-direction">{{ t('views.admin.moderation.ReportsList.ordering.direction.label') }}</label>
            <select
              id="reports-ordering-direction"
              v-model="orderingDirection"
              class="ui dropdown"
            >
              <option value="+">
                {{ t('views.admin.moderation.ReportsList.ordering.direction.ascending') }}
              </option>
              <option value="-">
                {{ t('views.admin.moderation.ReportsList.ordering.direction.descending') }}
              </option>
            </select>
          </div>
        </Layout>
      </div>
    </div>
    <div
      v-if="isLoading"
      class="ui active inverted dimmer"
    >
      <div class="ui loader" />
    </div>
    <div v-else-if="!result || result.count === 0">
      <empty-state
        :refresh="true"
        @refresh="fetchData()"
      />
    </div>
    <div v-else-if="mode === 'card'">
      <report-card
        v-for="obj in result.results"
        :key="obj.uuid"
        :init-obj="obj"
        @handled="fetchData"
      />
    </div>
    <div class="ui center aligned basic segment">
      <Pagination
        v-if="page && result && result.count > paginateBy"
        v-model:page="page"
        :pages="pages"
        :paginate-by="paginateBy"
      />
    </div>
  </Layout>
</template>
