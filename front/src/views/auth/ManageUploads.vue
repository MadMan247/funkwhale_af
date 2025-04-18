<script setup lang="ts">
import type { ImportStatus, PrivacyLevel, Upload } from '~/types'
import type { SmartSearchProps } from '~/composables/navigation/useSmartSearch'
import type { OrderingProps } from '~/composables/navigation/useOrdering'
import type { RouteRecordName } from 'vue-router'
import type { OrderingField } from '~/store/ui'
import type { Actor } from '~/types'
import type { paths, components } from '~/generated/types'

import { humanSize, truncate } from '~/utils/filters'
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import axios from 'axios'

import ImportStatusModal from '~/components/library/ImportStatusModal.vue'
import ActionTable from '~/components/common/ActionTable.vue'

import useSmartSearch from '~/composables/navigation/useSmartSearch'
import useSharedLabels from '~/composables/locale/useSharedLabels'
import useOrdering from '~/composables/navigation/useOrdering'
import useErrorHandler from '~/composables/useErrorHandler'
import usePage from '~/composables/navigation/usePage'

import Layout from '~/components/ui/Layout.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Button from '~/components/ui/Button.vue'
import Link from '~/components/ui/Link.vue'
import Pill from '~/components/ui/Pill.vue'
import Input from '~/components/ui/Input.vue'
import Loader from '~/components/ui/Loader.vue'
import Pagination from '~/components/ui/Pagination.vue'
import Table from '~/components/ui/Table.vue'
import Slider from '~/components/ui/Slider.vue'

interface Props extends SmartSearchProps, OrderingProps {
  object: Actor
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
const result = ref<paths['/api/v2/uploads/']['get']['responses']['200']['content']['application/json']>()

const sharedLabels = useSharedLabels()

type Item = components['schemas']['UploadForOwner'] & {
  selected: boolean
}

const items = ref<Item[]>([])

const selectedItems = computed(() =>
  items.value.filter(({ selected }) => selected)
)

// After fetch, keep only those items selected that were selected before
watch(result, r => {
  items.value = r
    ? r.results.map((result, index) => ({
        ...result,
        selected: items.value.at(index)?.selected || false
      }))
    : []
})

// Model for use in global checkbox `select all`
const isAllSelected = computed<boolean | 'mixed'>({
  get: () =>
    items.value.every(({ selected }) => selected)
      ? true
      : items.value.some(({ selected }) => selected)
        ? 'mixed'
          : false,
  set: function (isTrue) {
    items.value
      = items.value.map(item => ({
        ...item,
        selected: isTrue ? true : false
      }))
  }
})

// For privacy slider
const options = {
  me: sharedLabels.fields.privacy_level.choices.me,
  instance: sharedLabels.fields.privacy_level.choices.instance,
  everyone: sharedLabels.fields.privacy_level.choices.everyone
} as const satisfies Record<PrivacyLevel, string>


// Model for use in global slider `privacy_level`
const globalPrivacyLevel = computed<PrivacyLevel | undefined>({
  get () {
    return selectedItems.value.length === 0
      ? undefined
      : selectedItems.value.map(({ privacy_level }) => privacy_level)
        .reduce((acc, item) =>
          acc === item
          ? acc
          : undefined
        )
    },
  set (level) {
    if (level === undefined) return

    const changes = []

    for (const [index, item] of items.value.entries()) {
      if (!item.selected || item.privacy_level === level)
        continue;

      changes.push({
        uuid: item.uuid,
        privacy_level: level
      })

      items.value[index].privacy_level = level
    }

    // Note: This will never set privacy_level to undefined.
    // privacy_level as undefined is only a workaround for items in legacy libraries.
    axios.patch<paths['/api/v2/uploads/bulk_update/']['patch']['responses']['200']['content']['application/json']>(
      'uploads/bulk_update/',
      changes
    )
  }
})

const { onSearch, query, addSearchToken, getTokenValue } = useSmartSearch(props)
const { onOrderingUpdate, orderingString, paginateBy, ordering, orderingDirection } = useOrdering(props)

const orderingOptions: [OrderingField, keyof typeof sharedLabels.filters][] = [
  ['creation_date', 'creation_date'],
  ['modification_date', 'modification_date'],
  ['accessed_date', 'accessed_date'],
  ['size', 'size'],
  ['bitrate', 'bitrate'],
  ['duration', 'duration']
]

const { t } = useI18n()
const actionFilters = computed(() => ({ q: query.value, ...props.filters }))
const actions = computed(() => [
  {
    name: 'delete',
    label: t('components.manage.library.UploadsTable.action.delete.label'),
    confirmationMessage: t('components.manage.library.UploadsTable.action.delete.warning'),
    isDangerous: true,
    allowAll: false,
    confirmColor: 'danger' as const
  }
])

// .delete<api/v2/uploads/{uid}>(...)

const isLoading = ref(false)
const fetchData = async () => {
  isLoading.value = true
  try {
    const response = await axios.get<paths['/api/v2/uploads/']['get']['responses']['200']['content']['application/json']>('/uploads/', { params: {
      scope: 'me',
      page: page.value,
      page_size: paginateBy.value,
      q: query.value,
      ordering: orderingString.value,
      ...props.filters
    }})

    result.value = response.data
  } catch (error) {
    useErrorHandler(error as Error)
    result.value = undefined
  } finally {
    isLoading.value = false
  }
}

onSearch(() => (page.value = 1))
watch(page, fetchData)
onOrderingUpdate(fetchData)
fetchData()

const labels = computed(() => ({
  searchPlaceholder: t('components.manage.library.UploadsTable.placeholder.search')
}))

const displayName = (item: Item): string => {
  return item.filename ?? item.source ?? item.uuid
}

const detailedUpload = ref<Item>()
const showUploadDetailModal = ref(false)

const getImportStatusChoice = (importStatus: ImportStatus) => {
  return sharedLabels.fields.import_status.choices[importStatus]
}

const getPrivacyLevelChoice = (privacyLevel: PrivacyLevel) => {
  return sharedLabels.fields.privacy_level.shortChoices[privacyLevel]
}
</script>

<template>
  <div class="ui inline form">
    <div class="fields">
      <div class="ui six wide field">
        <form @submit.prevent="query = search.value">
          <Input
            id="uploads-search"
            ref="search"
            v-model="query"
            name="search"
            search
            :label="t('components.manage.library.UploadsTable.label.search')"
            :placeholder="labels.searchPlaceholder"
          />
        </form>
      </div>
      <Spacer :size="16" />
      <Layout flex>
        <Spacer grow />
        <div class="field">
          <label for="uploads-visibility">{{ t('components.manage.library.UploadsTable.label.visibility') }}</label>
          <select
            id="uploads-visibility"
            class="ui dropdown"
            :value="getTokenValue('privacy_level', '')"
            @change="addSearchToken('privacy_level', ($event.target as HTMLSelectElement).value)"
          >
            <option value="">
              {{ t('components.manage.library.UploadsTable.option.all') }}
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
          <label for="uploads-status">{{ t('components.manage.library.UploadsTable.label.status') }}</label>
          <select
            id="uploads-status"
            class="ui dropdown"
            :value="getTokenValue('status', '')"
            @change="addSearchToken('status', ($event.target as HTMLSelectElement).value)"
          >
            <option value="">
              {{ t('components.manage.library.UploadsTable.option.all') }}
            </option>
            <option value="pending">
              {{ t('components.manage.library.UploadsTable.option.pending') }}
            </option>
            <option value="skipped">
              {{ t('components.manage.library.UploadsTable.option.skipped') }}
            </option>
            <option value="errored">
              {{ t('components.manage.library.UploadsTable.option.failed') }}
            </option>
            <option value="finished">
              {{ t('components.manage.library.UploadsTable.option.finished') }}
            </option>
          </select>
        </div>
        <div class="field">
          <label for="uploads-ordering">{{ t('components.manage.library.UploadsTable.ordering.label') }}</label>
          <select
            id="uploads-ordering"
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
          <label for="uploads-ordering-direction">{{ t('components.manage.library.UploadsTable.ordering.direction.label') }}</label>
          <select
            id="uploads-ordering-direction"
            v-model="orderingDirection"
            class="ui dropdown"
          >
            <option value="+">
              {{ t('components.manage.library.UploadsTable.ordering.direction.ascending') }}
            </option>
            <option value="-">
              {{ t('components.manage.library.UploadsTable.ordering.direction.descending') }}
            </option>
          </select>
        </div>
      </Layout>

      <!-- Edit the currently selected items -->

      <Spacer />
      <Spacer />
      <div
        class="default solid raised"
        style="margin: -32px; padding: 32px;"
      >
        <Slider
          v-model="globalPrivacyLevel"
          :disabled="selectedItems.length === 0 ? true : undefined"
          :options="options"
          :label="`Privacy level (${ selectedItems.length } items)`"
        />
      </div>
      <Spacer />
    </div>
  </div>
  <!-- TODO (wvffle): Check if :upload shouldn't be v-model:upload -->
  <!-- Alternative design: v-model of type components['schemas']['UploadForOwner'] | null (:show would be non-null) -->
  <!-- TODO (flupsi): Check if we can safely upgrade from type Upload to type components['schemas']['UploadForOwner'] -->
  <import-status-modal
    v-if="detailedUpload"
    v-model:show="showUploadDetailModal"
    :upload="detailedUpload as unknown as Upload"
  />
  <Loader v-if="isLoading" />

  <Table
    v-if="result"
    :grid-template-columns="['auto', 'auto', 'auto', 'auto', 'auto', 'auto']"
  >
    <template #header>
      <!-- 0. select -->
      <b>
        <input
          v-model="isAllSelected"
          type="checkbox"
          title="Select/Deselect all"
        >
      </b>
      <!-- 1. filename -->
      <b>
        {{ t('components.manage.library.UploadsTable.table.upload.header.name') }}
      </b>
      <!-- 2. privacy_level -->
      <b>
        {{ t('components.manage.library.UploadsTable.table.upload.header.visibility') }}
      </b>
      <!-- 3. import_status -->
      <b>
        {{ t('components.manage.library.UploadsTable.table.upload.header.importStatus') }}
      </b>
      <!-- 4. size -->
      <b>
        {{ t('components.manage.library.UploadsTable.table.upload.header.size') }}
      </b>
      <!-- 5. date of upload (not creation) -->
      <b>
        {{ t('components.manage.library.UploadsTable.table.upload.header.accessedDate') }}
      </b>
    </template>
    <template
      v-for="item in items"
      :key="item.uuid"
    >
      <!-- 0. select -->

      <b>
        <input
          v-model="item.selected"
          type="checkbox"
          title="Select"
        >
      </b>

      <!-- 1. filename -->

      <Link
        :to="{
          name: 'manage.library.uploads.detail',
          params: { id: item.uuid }
        }"
      >
        {{ truncate(displayName(item), 30, undefined, true) }}
      </Link>

      <!-- 2. privacy_level -->

      <Pill
        :title="t('components.manage.library.UploadsTable.table.upload.header.visibility')"
        v-bind="item.privacy_level
          ? { onClick: () => addSearchToken('privacy_level', item.privacy_level as PrivacyLevel) }
          : { disabled: true }
        "
      >
        {{ item.privacy_level }}
      </Pill>

      <!-- 3. import_status -->

      <Pill
        :title="t('components.manage.library.UploadsTable.table.upload.header.importStatus')"
        v-bind="{ [{
          draft: 'yellow',
          pending: 'blue',
          finished: 'green',
          errored: 'red',
          skipped: 'purple'
        }[item.import_status]]: true }"
        @click="addSearchToken('import_status', item.import_status)"
      >
        {{ item.import_status }}
        <template #action>
          <Button
            ghost
            primary
            round
            icon="bi-info-circle-fill"
            :title="sharedLabels.fields.import_status.label"
            @click="detailedUpload = item; showUploadDetailModal = true"
          />
        </template>
      </Pill>

      <!-- 4. size -->

      <span>
        {{ item.size
          ? humanSize(item.size)
          : t('components.manage.library.UploadsTable.notApplicable')
        }}
      </span>

      <!-- 5. date -->

      <human-date
        v-if="item.import_date"
        :date="item.import_date"
      />
      <span v-else>
        {{ t('components.manage.library.UploadsTable.notApplicable') }}
      </span>
    </template>
  </Table>

  <!-- Yes -->

  <action-table
    v-if="result"
    :objects-data="result"
    :actions="actions"
    action-url="manage/library/uploads/action/"
    :filters="actionFilters"
    @action-launched="fetchData"
  >
    <template #header-cells>
      <th>
        {{ t('components.manage.library.UploadsTable.table.upload.header.name') }}
      </th>
      <th>
        {{ t('components.manage.library.UploadsTable.table.upload.header.library') }}
      </th>
      <th>
        {{ t('components.manage.library.UploadsTable.table.upload.header.account') }}
      </th>
      <th>
        {{ t('components.manage.library.UploadsTable.table.upload.header.domain') }}
      </th>
      <th>
        {{ t('components.manage.library.UploadsTable.table.upload.header.visibility') }}
      </th>
      <th>
        {{ t('components.manage.library.UploadsTable.table.upload.header.importStatus') }}
      </th>
      <th>
        {{ t('components.manage.library.UploadsTable.table.upload.header.size') }}
      </th>
      <th>
        {{ t('components.manage.library.UploadsTable.table.upload.header.creationDate') }}
      </th>
      <th>
        {{ t('components.manage.library.UploadsTable.table.upload.header.accessedDate') }}
      </th>
    </template>
    <template #row-cells="scope">
      <td>
        <router-link :to="{name: 'manage.library.uploads.detail', params: {id: scope.obj.uuid }}">
          {{ truncate(displayName(scope.obj), 30, undefined, true) }}
        </router-link>
      </td>
      <td>
        <!-- <router-link :to="{name: 'manage.library.libraries.detail', params: {id: scope.obj.library.uuid }}">
          <i class="wrench icon" />
        </router-link>
        <a
          href=""
          class="discrete link"
          :title="scope.obj.library.name"
          @click.prevent="addSearchToken('library_id', scope.obj.library.id)"
        >
          {{ truncate(scope.obj.library.name, 20) }}
        </a> -->
      </td>
      <td>
        <!-- <router-link :to="{name: 'manage.moderation.accounts.detail', params: {id: scope.obj.library.actor.full_username }}" />
        <a
          href=""
          class="discrete link"
          :title="scope.obj.library.actor.full_username"
          @click.prevent="addSearchToken('account', scope.obj.library.actor.full_username)"
        >{{ scope.obj.library.actor.preferred_username }}</a> -->
      </td>
      <td>
        <!-- <template v-if="!scope.obj.is_local">
          <router-link :to="{name: 'manage.moderation.domains.detail', params: {id: scope.obj.domain }}">
            <i class="wrench icon" />
          </router-link>
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
          {{ t('components.manage.library.UploadsTable.link.local') }}
        </a> -->
      </td>
      <td>
        <a
          href=""
          class="discrete link"
          :title="getPrivacyLevelChoice(scope.obj.library.privacy_level)"
          @click.prevent="addSearchToken('privacy_level', scope.obj.library.privacy_level)"
        >
          {{ getPrivacyLevelChoice(scope.obj.library.privacy_level) }}
        </a>
      </td>
      <td>
        <a
          href=""
          class="discrete link"
          :title="getImportStatusChoice(scope.obj.import_status).help"
          @click.prevent="addSearchToken('status', scope.obj.import_status)"
        >
          {{ getImportStatusChoice(scope.obj.import_status).label }}
        </a>
        <Button
          class="tiny"
          icon="bi-question-circle"
          :title="sharedLabels.fields.import_status.label"
          @click="detailedUpload = scope.obj; showUploadDetailModal = true"
        />
      </td>
      <td>
        <span v-if="scope.obj.size">{{ humanSize(scope.obj.size) }}</span>
        <span v-else>
          {{ t('components.manage.library.UploadsTable.notApplicable') }}
        </span>
      </td>
      <td>
        <human-date :date="scope.obj.creation_date" />
      </td>
      <td>
        <human-date
          v-if="scope.obj.accessed_date"
          :date="scope.obj.accessed_date"
        />
        <span v-else>
          {{ t('components.manage.library.UploadsTable.notApplicable') }}
        </span>
      </td>
    </template>
  </action-table>
  <Pagination
    v-if="page && result && result.count > paginateBy"
    v-model:page="page"
    :pages="Math.ceil(result.count / paginateBy)"
  />

  <span v-if="page && result && result.results.length > 0">
    {{ t('components.manage.library.UploadsTable.pagination.results', { start: ((page-1) * paginateBy) + 1, end: ((page-1) * paginateBy) + result.results.length, total: result.count }) }}
  </span>
</template>
