<script setup lang="ts">
import type { SmartSearchProps } from '~/composables/navigation/useSmartSearch'
import type { OrderingProps } from '~/composables/navigation/useOrdering'
import type { RouteRecordName } from 'vue-router'
import type { OrderingField } from '~/store/ui'

import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import axios from 'axios'

import ActionTable from '~/components/common/ActionTable.vue'

import useSmartSearch from '~/composables/navigation/useSmartSearch'
import useSharedLabels from '~/composables/locale/useSharedLabels'
import useOrdering from '~/composables/navigation/useOrdering'
import useErrorHandler from '~/composables/useErrorHandler'
import usePage from '~/composables/navigation/usePage'

import Layout from '~/components/ui/Layout.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Input from '~/components/ui/Input.vue'
import Link from '~/components/ui/Link.vue'
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

const page = usePage()
type ResponseType = { count: number, results: any[] }
const result = ref<null | ResponseType>(null)
const search = ref()

const { onSearch, query, addSearchToken, getTokenValue } = useSmartSearch(props)
const { onOrderingUpdate, orderingString, paginateBy, ordering, orderingDirection } = useOrdering(props)

const orderingOptions: [OrderingField, keyof typeof sharedLabels.filters][] = [
  ['creation_date', 'creation_date'],
  ['name', 'name']
]

const actionFilters = computed(() => ({ q: query.value, ...props.filters }))

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
    const response = await axios.get('/manage/channels/', {
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
const { t } = useI18n()
const labels = computed(() => ({
  searchPlaceholder: t('components.manage.ChannelsTable.placeholder.search'),
  openModeration: t('components.manage.ChannelsTable.link.moderation')
}))
</script>

<template>
  <div class="ui inline form">
    <div class="fields">
      <div class="ui six wide field">
        <form @submit.prevent="query = search.value">
          <Input
            id="channel-search"
            ref="search"
            v-model="query"
            name="search"
            search
            :label="t('components.manage.ChannelsTable.label.search')"
            :placeholder="labels.searchPlaceholder"
          />
        </form>
      </div>
      <Spacer :size="16" />
      <Layout flex>
        <Spacer grow />
        <div class="field">
          <label for="channel-category">{{ t('components.manage.ChannelsTable.label.category') }}</label>
          <select
            id="channel-category"
            class="ui dropdown"
            :value="getTokenValue('category', '')"
            @change="addSearchToken('category', ($event.target as HTMLSelectElement).value)"
          >
            <option value="">
              {{ t('components.manage.ChannelsTable.option.all') }}
            </option>
            <option value="podcast">
              {{ sharedLabels.fields.content_category.choices.podcast }}
            </option>
            <option value="music">
              {{ sharedLabels.fields.content_category.choices.music }}
            </option>
            <option value="other">
              {{ sharedLabels.fields.content_category.choices.other }}
            </option>
          </select>
        </div>
        <div class="field">
          <label for="channel-ordering">{{ t('components.manage.ChannelsTable.ordering.label') }}</label>
          <select
            id="channel-ordering"
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
          <label for="channel-ordering-direction">{{ t('components.manage.ChannelsTable.ordering.direction.label') }}</label>
          <select
            id="channel-ordering-direction"
            v-model="orderingDirection"
            class="ui dropdown"
          >
            <option value="+">
              {{ t('components.manage.ChannelsTable.ordering.direction.ascending') }}
            </option>
            <option value="-">
              {{ t('components.manage.ChannelsTable.ordering.direction.descending') }}
            </option>
          </select>
        </div>
      </Layout>
    </div>
  </div>
  <Loader v-if="isLoading" />
  <action-table
    v-if="result"
    :objects-data="result"
    :actions="[]"
    action-url="manage/library/artists/action/"
    :filters="actionFilters"
    @action-launched="fetchData"
  >
    <template #header-cells>
      <th>
        {{ t('components.manage.ChannelsTable.table.channel.header.name') }}
      </th>
      <th>
        {{ t('components.manage.ChannelsTable.table.channel.header.account') }}
      </th>
      <th>
        {{ t('components.manage.ChannelsTable.table.channel.header.domain') }}
      </th>
      <th>
        {{ t('components.manage.ChannelsTable.table.channel.header.albums') }}
      </th>
      <th>
        {{ t('components.manage.ChannelsTable.table.channel.header.tracks') }}
      </th>
      <th>
        {{ t('components.manage.ChannelsTable.table.channel.header.creationDate') }}
      </th>
    </template>
    <template
      #row-cells="scope"
    >
      <td>
        <router-link :to="{name: 'manage.channels.detail', params: {id: scope.obj.actor.full_username }}">
          {{ scope.obj.artist.name }}
        </router-link>
      </td>
      <td>
        <Link
          icon="bi-wrench"
          solid
          square-small
          :to="{name: 'manage.moderation.accounts.detail', params: {id: scope.obj.attributed_to.full_username }}"
        >
          <span class="visually-hidden">{{ labels.openModeration }}</span>
        </Link>
        <a
          href=""
          class="discrete link"
          @click.prevent="addSearchToken('account', scope.obj.attributed_to.full_username)"
        >{{ scope.obj.attributed_to.preferred_username }}</a>
      </td>
      <td>
        <template v-if="!scope.obj.is_local">
          <Link
            icon="bi-wrench"
            solid
            square-small
            :to="{name: 'manage.moderation.domains.detail', params: {id: scope.obj.attributed_to.domain }}"
          >
            <span class="visually-hidden">{{ labels.openModeration }}</span>
          </Link>
          <a
            href=""
            class="discrete link"
            @click.prevent="addSearchToken('domain', scope.obj.attributed_to.domain)"
          >{{ scope.obj.attributed_to.domain }}</a>
        </template>
        <a
          v-else
          href=""
          class="ui tiny accent icon link label"
          @click.prevent="addSearchToken('domain', scope.obj.attributed_to.domain)"
        >
          <i class="home icon" />
          {{ t('components.manage.ChannelsTable.link.local') }}
        </a>
      </td>
      <td>
        {{ scope.obj.artist.albums_count }}
      </td>
      <td>
        {{ scope.obj.artist.tracks_count }}
      </td>
      <td>
        <human-date :date="scope.obj.creation_date" />
      </td>
    </template>
  </action-table>
  <div>
    <Pagination
      v-if="page && result && result.count > paginateBy"
      v-model:page="page"
      :pages="Math.ceil(result.count / paginateBy)"
    />

    <span v-if="page && result && result.results.length > 0">
      {{ t('components.manage.ChannelsTable.pagination.results', { start: ((page-1) * paginateBy) + 1, end: ((page-1) * paginateBy) + result.results.length, total: result.count }) }}
    </span>
  </div>
</template>
