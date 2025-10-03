<script setup lang="ts">
import type { SmartSearchProps } from '~/composables/navigation/useSmartSearch'
import type { OrderingProps } from '~/composables/navigation/useOrdering'
import type { RouteRecordName } from 'vue-router'
import type { OrderingField } from '~/store/ui'
import type { PrivacyLevelEnum } from '~/types'

import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import axios from 'axios'
import ActionTable from '~/components/common/ActionTable.vue'

import useSharedLabels from '~/composables/locale/useSharedLabels'
import useSmartSearch from '~/composables/navigation/useSmartSearch'
import useOrdering from '~/composables/navigation/useOrdering'
import useErrorHandler from '~/composables/useErrorHandler'
import usePage from '~/composables/navigation/usePage'

import Layout from '~/components/ui/Layout.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Input from '~/components/ui/Input.vue'
import Link from '~/components/ui/Link.vue'
import Button from '~/components/ui/Button.vue'
import Loader from '~/components/ui/Loader.vue'
import Pagination from '~/components/ui/Pagination.vue'

interface Props extends SmartSearchProps, OrderingProps {
  filters?: object

  // TODO(wvffle): Remove after https://github.com/vuejs/core/pull/4512 is merged
  orderingConfigName?: RouteRecordName
  defaultQuery?: string
  updateUrl?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  defaultQuery: '',
  updateUrl: false,
  filters: () => ({}),
  orderingConfigName: undefined
})

const search = ref()

const page = usePage()
type ResponseType = { count: number, results: any[] }
const result = ref<null | ResponseType>(null)

const { onSearch, query, addSearchToken, getTokenValue } = useSmartSearch(props)
const { onOrderingUpdate, orderingString, paginateBy, ordering, orderingDirection } = useOrdering(props)

const orderingOptions: [OrderingField, keyof typeof sharedLabels.filters][] = [
  ['creation_date', 'creation_date'],
  ['followers_count', 'followers'],
  ['uploads_count', 'uploads']
]

const { t } = useI18n()
const actionFilters = computed(() => ({ q: query.value, ...props.filters }))
const actions = computed(() => [{
  name: 'delete',
  label: t('components.manage.library.LibrariesTable.action.delete.label'),
  confirmationMessage: t('components.manage.library.LibrariesTable.action.delete.warning'),
  isDangerous: true,
  allowAll: false,
  confirmColor: 'danger'
} as const])

const isLoading = ref(false)
const fetchData = async () => {
  isLoading.value = true
  const params = {
    page: page.value,
    page_size: paginateBy.value,
    q: query.value,
    ordering: orderingString.value,
    ...props.filters
  }

  try {
    const response = await axios.get('/manage/library/libraries/', {
      params
    })

    result.value = response.data
  } catch (error) {
    useErrorHandler(error as Error)
    result.value = null
  } finally {
    isLoading.value = false
  }
}

onSearch(() => (page.value = 1))
watch(page, fetchData)
onOrderingUpdate(fetchData)
fetchData()

const sharedLabels = useSharedLabels()
const labels = computed(() => ({
  searchPlaceholder: t('components.manage.library.LibrariesTable.placeholder.search')
}))

const getPrivacyLevelChoice = (privacyLevel: PrivacyLevelEnum) => {
  return sharedLabels.fields.privacy_level.shortChoices[privacyLevel]
}
</script>

<template>
  <div class="ui inline form">
    <div class="fields">
      <div class="ui six wide field">
        <form @submit.prevent="query = search.value">
          <Input id="libraries-search" ref="search" v-model="query" name="search" search
            :label="t('components.manage.library.LibrariesTable.label.search')"
            :placeholder="labels.searchPlaceholder" />
        </form>
      </div>
      <Spacer :size="16" />
      <Layout flex>
        <Spacer grow />
        <div class="field">
          <label for="libraries-visibility">{{ t('components.manage.library.LibrariesTable.label.visibility') }}</label>
          <select id="libraries-visibility" class="ui dropdown" :value="getTokenValue('privacy_level', '')"
            @change="addSearchToken('privacy_level', ($event.target as HTMLSelectElement).value)">
            <option value="">
              {{ t('components.manage.library.LibrariesTable.option.all') }}
            </option>
            <option value="me">
              {{ sharedLabels.fields.privacy_level.shortChoices.me }}
            </option>
            <option value="instance">
              {{ sharedLabels.fields.privacy_level.shortChoices.instance }}
            </option>
            <option value="everyone">
              {{ sharedLabels.fields.privacy_level.shortChoices.everyone }}
            </option>
          </select>
        </div>
        <div class="field">
          <label for="libraries-ordering">{{ t('components.manage.library.LibrariesTable.ordering.label') }}</label>
          <select id="libraries-ordering" v-model="ordering" class="ui dropdown">
            <option v-for="(option, key) in orderingOptions" :key="key" :value="option[0]">
              {{ sharedLabels.filters[option[1]] }}
            </option>
          </select>
        </div>
        <div class="field">
          <label for="libraries-ordering-direction">{{
            t('components.manage.library.LibrariesTable.ordering.direction.label') }}</label>
          <select id="libraries-ordering-direction" v-model="orderingDirection" class="ui dropdown">
            <option value="+">
              {{ t('components.manage.library.LibrariesTable.ordering.direction.ascending') }}
            </option>
            <option value="-">
              {{ t('components.manage.library.LibrariesTable.ordering.direction.descending') }}
            </option>
          </select>
        </div>
      </Layout>
    </div>
  </div>
  <Loader v-if="isLoading" />
  <action-table v-if="result" :objects-data="result" :actions="actions" action-url="manage/library/libraries/action/"
    :filters="actionFilters" @action-launched="fetchData">
    <template #header-cells>
      <th>
        {{ t('components.manage.library.LibrariesTable.table.library.header.name') }}
      </th>
      <th>
        {{ t('components.manage.library.LibrariesTable.table.library.header.account') }}
      </th>
      <th>
        {{ t('components.manage.library.LibrariesTable.table.library.header.domain') }}
      </th>
      <th>
        {{ t('components.manage.library.LibrariesTable.table.library.header.visibility') }}
      </th>
      <th>
        {{ t('components.manage.library.LibrariesTable.table.library.header.uploads') }}
      </th>
      <th>
        {{ t('components.manage.library.LibrariesTable.table.library.header.followers') }}
      </th>
      <th>
        {{ t('components.manage.library.LibrariesTable.table.library.header.creationDate') }}
      </th>
    </template>
    <template #row-cells="scope">
      <td>
        <router-link :to="{ name: 'manage.library.libraries.detail', params: { id: scope.obj.uuid } }">
          {{ scope.obj.name }}
        </router-link>
      </td>
      <td>
        <Link solid square-small icon="bi-wrench"
          :to="{ name: 'manage.moderation.accounts.detail', params: { id: scope.obj.actor.full_username } }" />
        <a href="" class="discrete link" :title="scope.obj.actor.full_username"
          @click.prevent="addSearchToken('account', scope.obj.actor.full_username)">{{
            scope.obj.actor.preferred_username }}</a>
      </td>
      <td>
        <template v-if="!scope.obj.is_local">
          <Link solid square-small icon="bi-box-arrow-up-right"
            :to="{ name: 'manage.moderation.domains.detail', params: { id: scope.obj.domain } }" />
          <a href="" class="discrete link" :title="scope.obj.domain"
            @click.prevent="addSearchToken('domain', scope.obj.domain)">{{ scope.obj.domain }}</a>
        </template>
        <Button v-else square-small icon="bi-house-fill" @click.prevent="addSearchToken('domain', scope.obj.domain)">
          {{ t('components.manage.library.LibrariesTable.link.local') }}
        </Button>
      </td>
      <td>
        <a href="" class="discrete link" :title="getPrivacyLevelChoice(scope.obj.privacy_level)"
          @click.prevent="addSearchToken('privacy_level', scope.obj.privacy_level)">
          {{ getPrivacyLevelChoice(scope.obj.privacy_level) }}
        </a>
      </td>
      <td>
        {{ scope.obj.uploads_count }}
      </td>
      <td>
        {{ scope.obj.followers_count }}
      </td>
      <td>
        <human-date :date="scope.obj.creation_date" />
      </td>
    </template>
  </action-table>
  <Pagination v-if="page && result && result.count > paginateBy" v-model:page="page"
    :pages="Math.ceil(result.count / paginateBy)" />

  <span v-if="page && result && result.results.length > 0">
    {{ t('components.manage.library.LibrariesTable.pagination.results', {
      start: ((page - 1) * paginateBy) + 1, end:
        ((page - 1) * paginateBy) + result.results.length, total: result.count
    }) }}
  </span>
</template>
