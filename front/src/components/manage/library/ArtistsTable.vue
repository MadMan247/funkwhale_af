<script setup lang="ts">
import type { SmartSearchProps } from '~/composables/navigation/useSmartSearch'
import type { OrderingProps } from '~/composables/navigation/useOrdering'
import type { RouteRecordName } from 'vue-router'
import type { OrderingField } from '~/store/ui'

import { ref, computed, watch } from 'vue'
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

const search = ref()

const page = usePage()
type ResponseType = { count: number, results: any[] }
const result = ref<null | ResponseType>(null)

const { onSearch, query, addSearchToken, getTokenValue } = useSmartSearch(props)
const { onOrderingUpdate, orderingString, paginateBy, ordering, orderingDirection } = useOrdering(props)

const orderingOptions: [OrderingField, keyof typeof sharedLabels.filters][] = [
  ['creation_date', 'creation_date'],
  ['name', 'name']
]

const actionFilters = computed(() => ({ q: query.value, ...props.filters }))
const actions = computed(() => [{
    name: 'delete',
    label: t('components.manage.library.ArtistsTable.action.delete.label'),
    confirmationMessage: t('components.manage.library.ArtistsTable.action.delete.warning'),
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
    const response = await axios.get('/manage/library/artists/', {
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
  searchPlaceholder: t('components.manage.library.ArtistsTable.placeholder.search')
}))

const getUrl = (artist: { channel?: number; id: number }) => {
  return artist.channel
    ? { name: 'manage.channels.detail', params: { id: artist.channel } }
    : { name: 'manage.library.artists.detail', params: { id: artist.id } }
}
</script>

<template>
  <div class="ui inline form">
    <div class="fields">
      <div class="ui six wide field">
        <form @submit.prevent="query = search.value">
          <Input
            id="artists-search"
            ref="search"
            v-model="query"
            name="search"
            search
            :label="t('components.manage.library.ArtistsTable.label.search')"
            :placeholder="labels.searchPlaceholder"
          />
        </form>
      </div>
      <Spacer :size="16" />
      <Layout flex>
        <Spacer grow />
        <div class="field">
          <label for="artists-category">{{ t('components.manage.library.ArtistsTable.label.category') }}</label>
          <select
            id="artists-category"
            class="ui dropdown"
            :value="getTokenValue('category', '')"
            @change="addSearchToken('category', ($event.target as HTMLSelectElement).value)"
          >
            <option value="">
              {{ t('components.manage.library.ArtistsTable.option.all') }}
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
          <label for="artists-ordering">{{ t('components.manage.library.ArtistsTable.ordering.label') }}</label>
          <select
            id="artists-ordering"
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
          <label for="artists-ordering-direction">{{ t('components.manage.library.ArtistsTable.ordering.direction.label') }}</label>
          <select
            id="artists-ordering-direction"
            v-model="orderingDirection"
            class="ui dropdown"
          >
            <option value="+">
              {{ t('components.manage.library.ArtistsTable.ordering.direction.ascending') }}
            </option>
            <option value="-">
              {{ t('components.manage.library.ArtistsTable.ordering.direction.descending') }}
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
    :actions="actions"
    action-url="manage/library/artists/action/"
    :filters="actionFilters"
    @action-launched="fetchData"
  >
    <template #header-cells>
      <th>
        {{ t('components.manage.library.ArtistsTable.table.artist.header.name') }}
      </th>
      <th>
        {{ t('components.manage.library.ArtistsTable.table.artist.header.domain') }}
      </th>
      <th>
        {{ t('components.manage.library.ArtistsTable.table.artist.header.albums') }}
      </th>
      <th>
        {{ t('components.manage.library.ArtistsTable.table.artist.header.tracks') }}
      </th>
      <th>
        {{ t('components.manage.library.ArtistsTable.table.artist.header.creationDate') }}
      </th>
    </template>
    <template
      #row-cells="scope"
    >
      <td>
        <router-link :to="getUrl(scope.obj)">
          {{ scope.obj.name }}
        </router-link>
      </td>
      <td>
        <template v-if="!scope.obj.is_local">
          <Link
            solid
            square-small
            icon="bi-wrench"
            :to="{name: 'manage.moderation.domains.detail', params: {id: scope.obj.domain }}"
          />
          <a
            href=""
            class="discrete link"
            :title="scope.obj.domain"
            @click.prevent="addSearchToken('domain', scope.obj.domain)"
          >{{ scope.obj.domain }}</a>
        </template>
        <a
          v-else
          href=""
          class="ui tiny accent icon link label"
          @click.prevent="addSearchToken('domain', scope.obj.domain)"
        >
          <i class="home icon" />
          {{ t('components.manage.library.ArtistsTable.link.local') }}
        </a>
      </td>
      <td>
        {{ scope.obj.albums_count }}
      </td>
      <td>
        {{ scope.obj.tracks_count }}
      </td>
      <td>
        <human-date :date="scope.obj.creation_date" />
      </td>
    </template>
  </action-table>
  <Pagination
    v-if="page && result && result.count > paginateBy"
    v-model:page="page"
    :pages="Math.ceil(result.count / paginateBy)"
  />

  <span v-if="page && result && result.results.length > 0">
    {{ t('components.manage.library.ArtistsTable.pagination.results', { start: ((page-1) * paginateBy) + 1, end: ((page-1) * paginateBy) + result.results.length, total: result.count }) }}
  </span>
</template>
