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

const { onSearch, query, addSearchToken } = useSmartSearch(props)
const { onOrderingUpdate, orderingString, paginateBy, ordering, orderingDirection } = useOrdering(props)

const orderingOptions: [OrderingField, keyof typeof sharedLabels.filters][] = [
  ['creation_date', 'creation_date'],
  ['release_date', 'release_date'],
  ['name', 'name']
]

const { t } = useI18n()
const actionFilters = computed(() => ({ q: query.value, ...props.filters }))
const actions = computed<{
  name: string
  label: string
  isDangerous?: boolean
  allowAll?: boolean
  confirmColor?: 'success' | 'danger'
  confirmationMessage?: string
  filterChackable?: (item: any) => boolean
}[]>(() => [
  {
    name: 'delete',
    label: t('components.manage.library.AlbumsTable.action.delete.label'),
    confirmationMessage: t('components.manage.library.AlbumsTable.action.delete.warning'),
    isDangerous: true,
    allowAll: false,
    confirmColor: 'danger'
  }
])

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
    const response = await axios.get('/manage/library/albums/', {
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
  searchPlaceholder: t('components.manage.library.AlbumsTable.placeholder.search'),
  openModeration: t('components.manage.library.AlbumsTable.link.moderation')
}))
</script>

<template>
  <div class="ui inline form">
    <div class="fields">
      <div class="ui six wide field">
        <form @submit.prevent="query = search.value">
          <Input
            id="albums-search"
            ref="search"
            v-model="query"
            name="search"
            search
            :label="t('components.manage.library.AlbumsTable.label.search')"
            :placeholder="labels.searchPlaceholder"
          />
        </form>
      </div>
      <Spacer :size="16" />
      <Layout flex>
        <Spacer grow />
        <div class="field">
          <label for="albums-ordering">{{ t('components.manage.library.AlbumsTable.ordering.label') }}</label>
          <select
            id="albums-ordering"
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
          <label for="albums-ordering-direction">{{ t('components.manage.library.AlbumsTable.ordering.direction.label') }}</label>
          <select
            v-model="orderingDirection"
            class="ui dropdown"
          >
            <option value="+">
              {{ t('components.manage.library.AlbumsTable.ordering.direction.ascending') }}
            </option>
            <option value="-">
              {{ t('components.manage.library.AlbumsTable.ordering.direction.descending') }}
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
    action-url="manage/library/albums/action/"
    :filters="actionFilters"
    @action-launched="fetchData"
  >
    <template #header-cells>
      <th>
        {{ t('components.manage.library.AlbumsTable.table.album.header.name') }}
      </th>
      <th>
        {{ t('components.manage.library.AlbumsTable.table.album.header.artist') }}
      </th>
      <th>
        {{ t('components.manage.library.AlbumsTable.table.album.header.domain') }}
      </th>
      <th>
        {{ t('components.manage.library.AlbumsTable.table.album.header.tracks') }}
      </th>
      <th>
        {{ t('components.manage.library.AlbumsTable.table.album.header.releaseDate') }}
      </th>
      <th>
        {{ t('components.manage.library.AlbumsTable.table.album.header.creationDate') }}
      </th>
    </template>
    <template
      #row-cells="scope"
    >
      <td>
        <router-link :to="{name: 'manage.library.albums.detail', params: {id: scope.obj.id }}">
          {{ scope.obj.title }}
        </router-link>
      </td>
      <td>
        <Link
          icon="bi-wrench"
          solid
          square-small
          :to="{name: 'manage.library.artists.detail', params: {id: scope.obj.artist_credit[0].artist.id }}"
        >
          <span class="visually-hidden">{{ labels.openModeration }}</span>
        </Link>
        <a
          href=""
          class="discrete link"
          :title="scope.obj.artist_credit[0].artist.name"
          @click.prevent="addSearchToken('artist', scope.obj.artist_credit[0].artist.name)"
        >{{ scope.obj.artist_credit[0].artist.name }}</a>
      </td>
      <td>
        <template v-if="!scope.obj.is_local">
          <Link
            icon="bi-box-arrow-up-right"
            solid
            square-small
            :to="{name: 'manage.moderation.domains.detail', params: {id: scope.obj.domain }}"
          >
            <span class="visually-hidden">{{ labels.openModeration }}</span>
          </Link>
          <a
            href=""
            class="discrete link"
            @click.prevent="addSearchToken('domain', scope.obj.domain)"
          >{{ scope.obj.domain }}</a>
        </template>
        <Button
          v-else
          icon="bi-house-fill"
          square-small
          @click.prevent="addSearchToken('domain', scope.obj.domain)"
        >
          {{ t('components.manage.library.AlbumsTable.link.local') }}
        </Button>
      </td>
      <td>
        {{ scope.obj.tracks_count }}
      </td>
      <td>
        <human-date
          v-if="scope.obj.release_date"
          :date="scope.obj.release_date"
        />
        <span v-else>
          {{ t('components.manage.library.AlbumsTable.notApplicable') }}
        </span>
      </td>
      <td>
        <human-date :date="scope.obj.creation_date" />
      </td>
    </template>
  </action-table>
  <Pagination
    v-if="page && page !== undefined && result && result.count > paginateBy"
    v-model:page="page"
    :pages="Math.ceil(result.count / paginateBy)"
  />

  <span v-if="page && result && result.results.length > 0">
    {{ t('components.manage.library.AlbumsTable.pagination.results', {start: ((page-1) * paginateBy) + 1, end: ((page-1) * paginateBy) + result.results.length, total: result.count}) }}
  </span>
</template>
