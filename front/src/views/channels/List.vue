<script setup lang="ts">
import type { OrderingProps } from '~/composables/navigation/useOrdering'
import type { PaginatedChannelList } from '~/types'
import { type operations } from '~/generated/types.ts'
import type { RouteRecordName } from 'vue-router'
import type { OrderingField } from '~/store/ui'

import { computed, ref, watch } from 'vue'
import { useRouteQuery } from '@vueuse/router'
import { useI18n } from 'vue-i18n'
import { syncRef } from '@vueuse/core'
import { sortedUniq } from 'lodash-es'
import { useRouter, useRoute } from 'vue-router'
import { useStore } from '~/store'
import { useDataStore } from '~/ui/stores/data'

import axios from 'axios'

import useUrlParamCache from '~/ui/composables/useUrlParamCache.ts'
import useSharedLabels from '~/composables/locale/useSharedLabels'
import { useModal } from '~/ui/composables/useModal.ts'
import usePage from '~/composables/navigation/usePage'
import useErrorHandler from '~/composables/useErrorHandler'
import useOrdering from '~/composables/navigation/useOrdering'
import useLogger from '~/composables/useLogger'

import ChannelCard from '~/components/audio/ChannelCard.vue'
import Loader from '~/components/ui/Loader.vue'
import Pagination from '~/components/ui/Pagination.vue'
import RemoteSearchForm from '~/components/RemoteSearchForm.vue'
import ChannelForm from '~/components/audio/ChannelForm.vue'
import Layout from '~/components/ui/Layout.vue'
import Modal from '~/components/ui/Modal.vue'
import Button from '~/components/ui/Button.vue'
import Input from '~/components/ui/Input.vue'
import Pills from '~/components/ui/Pills.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Section from '~/components/ui/Section.vue'
import Select from '~/components/ui/Select.vue'
import Nav from '~/components/ui/Nav.vue'

interface Props extends OrderingProps {
  scope?: 'me' | 'subscribed' | 'domain' | 'all'

  // TODO(wvffle): Remove after https://github.com/vuejs/core/pull/4512 is merged
  orderingConfigName?: RouteRecordName
  defaultQuery?: string
}

const props = withDefaults(defineProps<Props>(), {
  scope: 'all',
  orderingConfigName: undefined,
  defaultQuery: ''
})

const q = useRouteQuery('query', '')
const query = ref(q.value ?? '')
syncRef(q, query, { direction: 'ltr' })

const result = ref<PaginatedChannelList>()

const widgetKey = ref(new Date().toLocaleString())

const { t } = useI18n()
const labels = computed(() => ({
  searchPlaceholder: t('views.channels.List.placeholder.search')
}))

const router = useRouter()
const route = useRoute()
const logger = useLogger()
const sharedLabels = useSharedLabels()

const step = ref(1)
const submittable = ref(false)
const category = ref('podcast')
const modalContent = ref()
const createForm = ref()
const page = usePage()
const tags = useRouteQuery<string[]>('tag', [])

const { onOrderingUpdate, orderingString, paginateBy, ordering, orderingDirection } = useOrdering(props)

const store = useStore()
const dataStore = useDataStore()

const tabs = ref([
  { title: t("views.channels.List.tabs.me"), name: 'me' },
  { title: t("views.channels.List.tabs.subscribed"), name: 'subscribed' },
  { title: t("views.channels.List.tabs.domain"), name: 'domain:' + store.getters['instance/domain'] },
  { title: t("views.channels.List.tabs.all"), name: 'all' }
])
const scope = useUrlParamCache('scope', { fallback: props.scope })

watch(() => route.query.scope, async (newScope) => {
  await router.isReady()
  const scopeQuery = Array.isArray(newScope) ? newScope[0] : newScope
  if (!scopeQuery) {
    await router.replace({
      ...route,
      query: { ...route.query, scope: scope.value }
    })
  } else if (scopeQuery === 'from_subscribed') {
    await router.replace({
      ...route,
      query: { ...route.query, scope: 'subscribed' }
    })
  }
}, { immediate: true })

const scopeFilter = computed(() => {
  if (scope.value === 'subscribed') return 'all'
  else return scope.value
})

const subscribedFilter = computed(() => {
  if (scope.value === 'subscribed') return true
  else return undefined
})

const count = ref(0)
const isLoading = ref(false)
const fetchData = async () => {
  isLoading.value = true
  const params : operations['get_channels']['parameters']['query'] = {
    scope: scopeFilter.value,
    subscribed: subscribedFilter.value,
    content_category: 'music',
    page: page.value,
    page_size: paginateBy.value,
    q: query.value,
    ordering: [orderingString.value] as ("creation_date" | "modification_date" | "-creation_date" | "-modification_date" | "-random" | "random")[],
    tag: tags.value
  }

  const measureLoading = logger.time('Fetching channels')
  try {
    const response = await axios.get<PaginatedChannelList>('channels/', {
      params,
      paramsSerializer: {
        indexes: null
      }
    })
    count.value = response.data.count
    result.value = response.data
  } catch (error) {
    useErrorHandler(error as Error)
    result.value = undefined
  } finally {
    measureLoading()
    isLoading.value = false
  }
}

watch(() => store.state.moderation.lastUpdate, fetchData)

const reloadWidget = () => (widgetKey.value = new Date().toLocaleString())

watch([page, tags, q, ordering, orderingDirection, scope], fetchData)
watch([tags, q, ordering, orderingDirection, scope], () => {
  page.value = 1
})

const search = () => {
  page.value = 1
  q.value = query.value
}

onOrderingUpdate(() => {
  page.value = 1
  fetchData()
})

const paginateOptions = computed<Record<number, string>>(() =>
  Object.fromEntries(
    sortedUniq([12, 30, 50, paginateBy.value].sort((a, b) => a - b))
      .map(v=>[v,`${v}`])
  )
)

  // ({ ...(sortedUniq([12, 30, 50, paginateBy.value].sort((a, b) => a - b))) }))

/* Options and `refs` for each filter `<Select>` control */
const searchFilters = ref({
  'ordering': {
    label: t('components.manage.library.UploadsTable.ordering.label'),
    current: ordering,
    options: {
      'creation_date': sharedLabels.filters.creation_date,
      'modification_date': sharedLabels.filters.modification_date
    } satisfies Partial<Record<OrderingField, string>>
  },
  'orderingDirection': {
    label: t('components.manage.library.UploadsTable.ordering.direction.label'),
    current: orderingDirection,
    options: {
      '+': t('components.manage.library.UploadsTable.ordering.direction.ascending'),
      '-': t('components.manage.library.UploadsTable.ordering.direction.descending')
    }
  },
  'pagination': {
    label: t('components.library.Podcasts.pagination.results'),
    current: paginateBy,
    options: paginateOptions
  }
} as const )

const showSubscribeModal = ref(false)
const showCreateModal = ref(false)
</script>

<template>
  <Layout
    stack
    main
    gap-84
  >
    <Spacer no-size />
    <!-- TODO: `yarn lint:tsc` doesn't understand the `Prop` type for `Header` while the language server does. It may be a question of typescript version... Investigate and fix! https://dev.funkwhale.audio/funkwhale/funkwhale/-/issues/2437 -->
    <!-- @vue-ignore -->
    <Section
      :h1="t('views.auth.ProfileContent.header.channels')"
      :action="{
        text: ScopeOption === 'me' ? t('views.channels.List.link.addNew') : t('views.channels.List.link.addRemote'),
        // @ts-ignore
        onClick: () => {
          if (ScopeOption === 'me') { showCreateModal = true }
          else { showSubscribeModal = true }
        },
        // @ts-ignore
        primary: true,
        // @ts-ignore
        icon: 'bi-plus'
      }"
      large-section-heading
    >
      <Modal
        v-if="store.state.auth.authenticated"
        v-model="showSubscribeModal"
        :title="t('views.channels.SubscriptionsList.modal.subscription.header')"
      >
        <div
          ref="modalContent"
          class="scrolling content"
        >
          <remote-search-form
            initial-type="both"
            :show-submit="false"
            :standalone="false"
            :redirect="true"
            @subscribed="showSubscribeModal = false; reloadWidget()"
          />
        </div>
        <template #actions>
          <Button
            secondary
            @click="showSubscribeModal = false"
          >
            {{ t('views.channels.SubscriptionsList.button.cancel') }}
          </Button>
          <Button
            form="remote-search"
            type="submit"
            icon="bi-bookmark-check-fill"
            primary
          >
            {{ t('views.channels.SubscriptionsList.button.subscribe') }}
          </Button>
        </template>
      </Modal>
      <Spacer no-size />
      <Layout
        form
        flex
        @submit.prevent="search"
      >
        <!-- TODO: Translations -->
        <Input
          id="artist-search"
          v-model="query"
          search
          name="search"
          :label="t('components.library.Podcasts.label.search')"
          autofocus
          :placeholder="labels.searchPlaceholder"
        />
        <Pills
          v-if="typeof tags === 'object'"
          :get="model => { tags = model.currents.map(({ label }) => label) }"
          :set="model => ({
            currents: tags.map(tag => ({ type: 'custom' as const, label: tag })),
            others: dataStore.tags().value
              .filter(({ name }) => result?.results?.some((object) => object.artist.tags?.includes(name)) && !tags.includes(name))
              .map(({ name }) => ({ type: 'preset' as const, label: name })),
          })"
          :label="t('components.library.Podcasts.label.tags')"
          style="max-width: 350px;"
        />
        <Select
          v-for="[id, filter] in Object.entries(searchFilters)"
          :id="`artist-${id}`"
          :key="id"
          v-model:current="filter.current"
          v-model:options="filter.options"
          :label="filter.label"
        />
      </Layout>

      <Nav
        v-model="tabs"
        tab-query-field="scope"
      >
        <Loader v-if="isLoading" />
        <Pagination
          v-if="page && result && result.count > paginateBy"
          v-model:page="page"
          :pages="Math.ceil(result.count / paginateBy)"
        />
        <Layout
          v-if="result && result.results.length > 0"
          grid
          style="display:flex; flex-wrap:wrap; gap: 32px; margin-top:32px;"
        >
          <channel-card
            v-for="channel in result?.results"
            :key="channel.uuid"
            :object="channel"
          />
        </Layout>
        <Layout
          v-else-if="result && result.results.length === 0"
          stack
        >
          <Alert yellow>
            <i class="compact disc icon" />
            {{ t('components.library.Artists.empty.noResults') }}
          </Alert>
          <Layout flex>
            <Card
              v-if="store.state.auth.authenticated"
              :title="t('components.library.Artists.button.upload')"
              primary
              style="text-align: center;"
              :to="useModal('upload').to"
            >
              <template #image>
                <i
                  class="bi bi-upload"
                  style="font-size: 100px; position: relative; top: 50px;"
                />
              </template>
            </Card>
          </Layout>
        </Layout>
        <Spacer grow />
        <Pagination
          v-if="page && result && result.count > paginateBy"
          v-model:page="page"
          :pages="Math.ceil(result.count / paginateBy)"
        />
        <Modal
          v-model="showCreateModal"
          :title="
            step === 1
              ? t('views.auth.ProfileContent.modal.createChannel.header')
              : category === 'podcast'
                ? t('views.auth.ProfileContent.modal.createChannel.podcast.header')
                : t('views.auth.ProfileContent.modal.createChannel.artist.header')
          "
        >
          <channel-form
            ref="createForm"
            :object="null"
            :step="step"
            @loading="isLoading = $event"
            @submittable="submittable = $event"
            @category="category = $event"
            @errored="modalContent.scrollTop = 0"
            @created="router.push({name: 'channels.detail', params: {id: $event.actor.preferred_username}})"
          />
          <template #actions>
            <Button
              secondary
              autofocus
              @click="showCreateModal = false"
            >
              {{ t('views.auth.ProfileContent.button.cancel') }}
            </Button>
            <Spacer grow />
            <Button
              v-if="step > 1"
              secondary
              @click.stop.prevent="step -= 1"
            >
              {{ t('views.auth.ProfileContent.button.previous') }}
            </Button>
            <Button
              v-if="step === 1"
              primary
              @click.stop.prevent="step += 1"
            >
              {{ t('views.auth.ProfileContent.button.next') }}
            </Button>
            <Button
              v-if="step === 2"
              primary
              type="submit"
              :disabled="!submittable && !isLoading"
              :is-loading="isLoading"
              @click.prevent.stop="createForm.submit"
            >
              {{ t('views.auth.ProfileContent.button.createChannel') }}
            </Button>
          </template>
        </Modal>
      </Nav>
    </Section>
  </Layout>
</template>
