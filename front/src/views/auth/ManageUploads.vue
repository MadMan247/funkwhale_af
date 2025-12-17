<script setup lang="ts">
import type { PrivacyLevelEnum, Upload } from '~/types'
import type { SmartSearchProps } from '~/composables/navigation/useSmartSearch'
import type { OrderingProps } from '~/composables/navigation/useOrdering'
import type { RouteRecordName } from 'vue-router'
import type { OrderingField } from '~/store/ui'
import type { Actor } from '~/types'
import type { paths, components } from '~/generated/types'

import { humanSize, truncate } from '~/utils/filters'
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouteQuery } from '@vueuse/router'

import axios from 'axios'

import ImportStatusModal from '~/components/library/ImportStatusModal.vue'

// TODO (2.0.0+): Consolidate token logic from useSmartSearch and search.ts
// import useSmartSearch from '~/composables/navigation/useSmartSearch'
import useSharedLabels from '~/composables/locale/useSharedLabels'
import useOrdering from '~/composables/navigation/useOrdering'
import useErrorHandler from '~/composables/useErrorHandler'
import usePage from '~/composables/navigation/usePage'
import Quota from '~/views/content/libraries/Quota.vue'

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
import Select from '~/components/ui/Select.vue'
import DangerousButton from '~/components/common/DangerousButton.vue'

interface Props extends SmartSearchProps, OrderingProps {
  object: Actor
  filters?: object

  // TODO(wvffle): Remove after https://github.com/vuejs/core/pull/4512 is merged
  // // Was merged on 2022-10-26
  //  // https://github.com/vuejs/core/issues/4498
  // TODO (2.0.0+): Simplify this code if possible. It seems that it supports unnecessary cases (?), and Vue might support a more declarative way to express its intention by now... (?)
  orderingConfigName?: RouteRecordName
  defaultQuery?: string
  updateUrl?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  defaultQuery: '',
  updateUrl: true,
  filters: () => ({}),
  orderingConfigName: undefined
})
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
      selected: items.value.find(i => i.uuid === result.uuid)?.selected || false
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

// For privacy slider and <select>
const changes = ref<{ uuid: string, privacy_level: PrivacyLevelEnum }[]>([])

// Model for use in global slider `privacy_level`
const globalPrivacyLevel = computed<PrivacyLevelEnum | undefined>({
  get() {
    return selectedItems.value.length === 0
      ? undefined
      : selectedItems.value.map(({ privacy_level }) => privacy_level)
        .reduce((acc, item) =>
          acc === item
            ? acc
            : undefined
        )
  },
  set(level) {
    if (level === undefined) return

    changes.value = []
    for (const [index, item] of items.value.entries()) {
      if (!item.selected || item.privacy_level === level)
        continue;

      changes.value.push({
        uuid: item.uuid,
        privacy_level: level
      })

      items.value[index]!.privacy_level = level
    }
  }
})

const submit = async () => {
  if (changes.value.length === 0) return

  isLoading.value = true
  await axios.patch(
      'uploads/bulk_update/',
      changes.value
    )

  isLoading.value = false
}

/// SEARCH

// const { onSearch, query, addSearchToken, getTokenValue, token } = useSmartSearch(props)
const { onOrderingUpdate, orderingString, paginateBy, ordering, orderingDirection } = useOrdering(props)

const { t } = useI18n()

const isLoading = ref(false)
const fetchData = async () => {
  isLoading.value = true
  try {
    const response = await axios.get<paths['/api/v2/uploads/']['get']['responses']['200']['content']['application/json']>('/uploads/', {
      params: {
        scope: 'me',
        page: page.value,
        page_size: paginateBy.value,
        ordering: orderingString.value,
        ...Object.fromEntries(tokens.get()),
        ...props.filters
      }
    })

    result.value = response.data
  } catch (error) {
    useErrorHandler(error as Error)
    result.value = undefined
    setTimeout(()=> page.value = 1, 1000)
  } finally {
    isLoading.value = false
  }
}

const deleteSelectedUploads = async () => {
  try {
    isLoading.value = true
   await axios.post(`/uploads/action/`, {
      action: "delete",
      objects: selectedItems.value.map((upload) => upload.uuid)
    })
    await fetchData()
  } catch (error) {
    useErrorHandler(error as Error)
  } finally {
    isLoading.value = false
  }

}

const labels = computed(() => ({
  searchPlaceholder: t('components.manage.library.UploadsTable.placeholder.search')
}))

const displayName = (item: Item): string => {
  return item.filename ?? item.source ?? item.uuid
}

const detailedUpload = ref<Item>()
const showUploadDetailModal = ref(false)

const privacyOptions = {
  me: sharedLabels.fields.privacy_level.choices.me,
  instance: sharedLabels.fields.privacy_level.choices.instance,
  followers: sharedLabels.fields.privacy_level.choices.followers,
  everyone: sharedLabels.fields.privacy_level.choices.everyone
} as const satisfies Record<PrivacyLevelEnum, string>


// Current logic:
// - [x] `ordering` and `orderingDirection` are 2-way synced with the
//          `ordering` parameter of the URL and parametrize `fetchData`
// - [x] `query` is 2-way synced with the `query` parameter of the URL
// - [x] `query.q` field is 2-way synced with the `search` input
// - [x] `status` and `privacy_level` are linked to tokens/fields inside `query`
// - [x] Inside `q`, quoted ranges are interpreted as atomic tokens;
//          otherwise words are tokens (Is this backend logic?).
// - [x] `query` provides parameters for search (`fetchData`)
//
// TODO (2.0.0+): Consolidate token logic from useSmartSearch and search.ts
// - [ ] Document usage sites for tokenized search logic
// - [ ] Document logic and check in with backend to confirm completeness
// - [ ] Consolidate search.ts with useSmartSearch composable if possible
// - [ ] Once ES2025 is activated, refactor logic to use iterator method chain
//         instead of imperative procedures
// - [ ] Strongly type parameters according to endpoint (check if schema is complete)
// - [ ] Integrate into `useDataStore` (data.ts) to activate search result caching and
//         eager fetching
//
// Test cases (draft):
// - q = `"Hello you"` searches a single full-text token
// - q = `"Hello you" privacy_level:me` filters it by privacy_level==='me'
// - q = `a b` gives the same result as `b a` because the tokens form a set (?)
//
// Ux considerations:
// - The `token` behavior is not communicated through the Ui.
//    A potential way to communicate it would be to
//    - Draw pill-shaped pastel backgrounds behind each token
//    - Integrate the (duplicate) `Select` controls into the `Input`
//    - Replace `Search` with `Filter` to make it clear that we are already
//       operating on a smaller pool: the user's Uploads, not global/federation.
// - The ordering is cumbersome and at the wrong place (it's not a filter).
//    - Use conventional arrow controls on table headers for switching
//       between all the ordering configurations
// TODO (2.0.0+): User-test, re-design and consolidate search/filter interface
// **A11y (UX):**
// The search/filter interface is perceivable
// - [ ] All users gather the purpose and semantics of all operations available
// The search/filter interface is operable
// - [ ] Users can access all controls by using only their keyboard
// - [ ] Users have enough time
// - [ ] No seizures or physical reactions
// - [ ] Users can always tell where they are (navigation, focus, cursor...) and how to find what they are looking for
// - [ ] Users can operate the interface with pointers (including aborting functions)
// The search/filter interface is understandable
// - [ ] User can easily read and understand content
// - [ ] Users can successfully predict next steps
// - [ ] Context changes are only initiated on user request
// - [ ] If errors are possible, correcting them is easy
// The search/filter interface is robust
// - [ ] It can be interpreted by 95% of browsers, and by standard assistive tech
// The search/filter interface conforms to WCAG 2.1
// **Consolidation (DX):**
// - [ ] Where possible, search/filter interfaces are implemented with the same patterns,
//         or abstracted into components if that reduces cognitive load on developers
// - [ ] Data handling is consolidated around the generated schema and the Url as the
//         source of truth, and abstracted into composables/stores where possible

/* Sync up `query` with tokens stored in the `q` parameter of the Url */
const query = useRouteQuery<string>('query', '')
// const query = ref(query.value ?? '')
// syncRef(q, query, { direction: 'ltr' })

/* Go to first page whenever the query parameters change  */
watch([query, ordering], () => { page.value = 1 }
)

/* Represent the `q` parameter of the Url as a Map of tokens.
- Key-Value pairs `key:value` are stored as [key, value] in the Map
- Deduplication: The last key in the Url overrides all previous ones
- Words `w` and phrases `"x y` are concatenated in order of insertion under the `''` key
   and moved to the start of `q` resp. `tokens`.

TODO (2.0.0+): The quote/unquote feature from search.ts is still missing in this file!
*/
const tokens = {
  get: () => query.value
    .split(' ')
    .filter(token => token.trim())
    .map(token => token.split(':'))
    .filter(([head, ...tail]) => tail.length !== 1 || tail[0]!.trim())
    .reduce((dict, [head, ...tail]) =>
      // TODO: Once we activate ES2025, we can use pattern matching here:
      tail.length === 1
        ? dict.set(head!, tail[0]!)
        : dict.set('q', `${dict.get('q') ?? ''} ${head} ${tail.join(':')}`.trim())
      , new Map<string, string>()),
  set: (dict: Map<string, string>) => {
    const fullText = dict.get('q') ?? ''
    const keyValuePairs = Array.from(dict)
      .filter(([key]) => key !== 'q')
      .map(([key, value]) => `${key}:${value}`)

    query.value = [fullText, ...keyValuePairs].filter(part => part.trim()).join(' ')
  }
}

/* Ref with a token of form `key:value` within the Url parameter `q`.
 - Updating the `q` parameter updates the token, and vice versa
 - Deduplication: The last key in the Url overrides all previous ones
 - Words and phrases are accessible under the `'q'` key */
const token = (key: string) =>
  computed({
    get: () => tokens.get().get(key) ?? '',
    set: (value: string) => tokens.set(tokens.get().set(key, value))
  })

const search = token('q')

/* Options and `refs` for each filter `<Select>` control */
const searchFilters = ref({
  'privacy_level': {
    label: t('components.manage.library.UploadsTable.label.visibility'),
    current: token('privacy_level'),
    options: {
      '': t('components.manage.library.UploadsTable.option.all'),
      ...privacyOptions
    }
  },
  'status': {
    label: t('components.manage.library.UploadsTable.label.status'),
    current: token('import_status'),
    options: {
      '': t('components.manage.library.UploadsTable.option.all'),
      'pending': t('components.manage.library.UploadsTable.option.pending'),
      'skipped': t('components.manage.library.UploadsTable.option.skipped'),
      'errored': t('components.manage.library.UploadsTable.option.failed'),
      'finished': t('components.manage.library.UploadsTable.option.finished')
    }
  },
  'ordering': {
    label: t('components.manage.library.UploadsTable.ordering.label'),
    current: ordering,
    options: {
      'creation_date': sharedLabels.filters.creation_date,
      'modification_date': sharedLabels.filters.modification_date,
      'accessed_date': sharedLabels.filters.accessed_date,
      'size': sharedLabels.filters.size,
      'bitrate': sharedLabels.filters.bitrate,
      'duration': sharedLabels.filters.duration
    } satisfies Partial<Record<OrderingField, string>>
  },
  'orderingDirection': {
    label: t('components.manage.library.UploadsTable.ordering.direction.label'),
    current: orderingDirection,
    options: {
      '+': t('components.manage.library.UploadsTable.ordering.direction.ascending'),
      '-': t('components.manage.library.UploadsTable.ordering.direction.descending')
    }
  }
} as const)

// Reload data when changing page data
watch(page, fetchData)

// Reset page and reload data when privacy level or import status changes
watch([token('privacy_level'), token('import_status')], () => {
  if (page.value !== 1) {
    page.value = 1
  } else {
    fetchData()
  }
})

const handlePurged = () => {
  page.value = 1
  fetchData()
}

onOrderingUpdate(fetchData)
fetchData()
</script>

<template>
  <Spacer />
  <quota @purged="handlePurged" />
  <Spacer size="64" />
  <Layout
    form
    flex
    @submit.prevent="fetchData"
  >
    <!-- Enter a search string and start the search -->

    <!-- TODO (2.0.0+): Replace with `Pills` component and allow editing all tokens (filters) -->

    <Input
      v-model="search"
      :label="t('components.manage.library.UploadsTable.label.search')"
      :placeholder="labels.searchPlaceholder"
      search
      style="min-width: min(100%, 520px)"
    />

    <!-- Filter the search results -->

    <!-- TODO (2.0.0+): Integrate these filters as `Pills` into above control -->

    <Select
      v-for="[id, filter] in Object.entries(searchFilters)"
      :id="`uploads-${id}`"
      :key="id"
      v-model:current="filter.current"
      v-model:options="filter.options"
      :label="filter.label"
    />
  </Layout>

  <Spacer />

  <!-- Edit the currently selected items -->
  <div
    :class="['default solid raised', $style.toolbox]"
    style="display: flex; align-items: center; gap: 1rem;"
  >
    <Spacer />
    <Slider
      v-model="globalPrivacyLevel"
      :disabled="selectedItems.length === 0 ? true : undefined"
      :options="privacyOptions"
      :label="`Privacy level (${selectedItems.length} items)`"
      style="flex: 1;"
    />
  </div>
  <div
    :class="['default solid raised', $style.toolbox]"
    style="display: flex; align-items: center; gap: 1rem;"
  >
    <DangerousButton
      :disabled="selectedItems.length === 0 ? true : undefined"
      :action="deleteSelectedUploads"
    >
      {{ t('components.manage.library.UploadsTable.action.delete.label') }} {{ selectedItems.length > 0 ? `(${selectedItems.length})` : '' }}
      <template #content>
        {{ t('components.manage.library.UploadsTable.action.delete.warning') }}
      </template>
    </DangerousButton>
    <Spacer grow />
    <Button
      type="submit"
      primary
      :class="[{'loading': isLoading}]"
      @click="submit"
    >
      {{ t('components.auth.Plugin.button.save') }}
    </Button>
  </div>


  <!-- Select my items -->

  <!-- TODO (wvffle): Check if :upload shouldn't be v-model:upload -->
  <!-- Alternative design: v-model of type components['schemas']['UploadForOwner'] | null (:show would be non-null) -->
  <!-- TODO (2.0.0+): Check if we can safely upgrade from type Upload to type components['schemas']['UploadForOwner'] -->
  <import-status-modal
    v-if="detailedUpload"
    v-model:show="showUploadDetailModal"
    :upload="detailedUpload as unknown as Upload"
  />
  <Loader
    v-if="isLoading"
    style="height: 0;"
  />

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
        {{ t('components.manage.library.UploadsTable.table.upload.header.creationDate') }}
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
          :disabled="item.import_status !== 'finished'"
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
          ? { onClick: () => { token('privacy_level').value = item.privacy_level as PrivacyLevelEnum } }
          : { disabled: true }
        "
      >
        {{ item.privacy_level }}
      </Pill>

      <!-- 3. import_status -->

      <Pill
        :title="t('components.manage.library.UploadsTable.table.upload.header.importStatus')"
        v-bind="{
          [{
            draft: 'yellow',
            pending: 'blue',
            finished: 'green',
            errored: 'red',
            skipped: 'purple',
          }[item.import_status]]: true
        }"
        @click="() => { token('import_status').value = item.import_status }"
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

  <Pagination
    v-if="page && result && result.count > paginateBy"
    v-model:page="page"
    :pages="Math.ceil(result.count / paginateBy)"
  />

  <span v-if="page && result && result.results.length > 0">
    {{ t('components.manage.library.UploadsTable.pagination.results', {
      start: ((page - 1) * paginateBy) + 1, end:
        ((page - 1)
          * paginateBy) + result.results.length, total: result.count
    }) }}
  </span>
</template>

<style module>
.toolbox {
  margin: 0 -32px;
  padding: 32px;
  max-height: 20em;
  transition: opacity 0.2s ease-in-out;

  &:has([disabled]) {
    opacity: 0.5;
    pointer-events: none;
  }
}
</style>
