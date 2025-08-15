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
import { useRouter } from 'vue-router'
import { useStore } from '~/store'

import axios from 'axios'

import useSharedLabels from '~/composables/locale/useSharedLabels'
import usePage from '~/composables/navigation/usePage'
import useErrorHandler from '~/composables/useErrorHandler'
import useOrdering from '~/composables/navigation/useOrdering'
import useLogger from '~/composables/useLogger'

import ChannelsWidget from '~/components/audio/ChannelsWidget.vue'
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

interface Props extends OrderingProps {
  scope?: 'me' | 'all'

  // TODO(wvffle): Remove after https://github.com/vuejs/core/pull/4512 is merged
  orderingConfigName?: RouteRecordName
  defaultQuery?: string
}

const props = withDefaults(defineProps<Props>(), {
  scope: 'all',
  orderingConfigName: undefined,
  defaultQuery: ''
})

const subscribedQuery = ref(props.defaultQuery)
const q = useRouteQuery('query', '')
const query = ref(q.value ?? '')
syncRef(q, query, { direction: 'ltr' })

const result = ref<PaginatedChannelList>()

const widgetKey = ref(new Date().toLocaleString())

const { t } = useI18n()
const labels = computed(() => ({
  searchPlaceholder: t('views.channels.SubscriptionsList.placeholder.search')
}))

const router = useRouter()
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

const count = ref(0)
const isLoading = ref(false)
const fetchData = async () => {
  isLoading.value = true
  const params : operations['get_channels_2']['parameters']['query'] = {
    scope: props.scope,
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

const store = useStore()
watch(() => store.state.moderation.lastUpdate, fetchData)

const reloadWidget = () => (widgetKey.value = new Date().toLocaleString())

watch([page, tags, q, ordering, orderingDirection], fetchData)

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
    <Section
      v-if="store.state.auth.authenticated"
      :h1="t('views.channels.SubscriptionsList.title')"
      :action="{
        text: t('views.channels.SubscriptionsList.link.addNew'),
        onClick: () => { showSubscribeModal = true },
        primary: true,
        icon: 'bi-plus'
      }"
      large-section-heading
    >
      <Modal
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
      <inline-search-bar
        v-if="store.state.auth.authenticated"
        v-model="subscribedQuery"
        :placeholder="labels.searchPlaceholder"
        @search="reloadWidget"
      />
      <channels-widget
        v-if="store.state.auth.authenticated"
        :key="widgetKey"
        :limit="4"
        :show-modification-date="true"
        :filters="{q: subscribedQuery, subscribed: 'true'}"
      />
    </Section>
    <!-- TODO: `yarn lint:tsc` doesn't understand the `Prop` type for `Header` while the language server does. It may be a question of typescript version... Investigate and fix! https://dev.funkwhale.audio/funkwhale/funkwhale/-/issues/2437 -->
    <!-- @vue-ignore -->
    <Section
      :h1="t('views.auth.ProfileOverview.header.channels')"
      :action="{
        text: t('views.channels.SubscriptionsList.link.addNew'),
        // @ts-ignore
        onClick: () => { showCreateModal = true },
        // @ts-ignore
        icon: 'bi-plus',
        // @ts-ignore
        primary: true
      }"
      large-section-heading
    >
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
            ...model,
            others: [],
            currents: tags.map(tag => ({ type: 'custom' as const, label: tag })),
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
      <channels-widget
        :key="widgetKey"
        :limit="paginateBy"
        :show-modification-date="true"
        :filters="{q: subscribedQuery, subscribed: 'false'}"
      />

      <Modal
        v-model="showCreateModal"
        :title="
          step === 1
            ? t('views.auth.ProfileOverview.modal.createChannel.header')
            : category === 'podcast'
              ? t('views.auth.ProfileOverview.modal.createChannel.podcast.header')
              : t('views.auth.ProfileOverview.modal.createChannel.artist.header')
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
            {{ t('views.auth.ProfileOverview.button.cancel') }}
          </Button>
          <Spacer grow />
          <Button
            v-if="step > 1"
            secondary
            @click.stop.prevent="step -= 1"
          >
            {{ t('views.auth.ProfileOverview.button.previous') }}
          </Button>
          <Button
            v-if="step === 1"
            primary
            @click.stop.prevent="step += 1"
          >
            {{ t('views.auth.ProfileOverview.button.next') }}
          </Button>
          <Button
            v-if="step === 2"
            primary
            type="submit"
            :disabled="!submittable && !isLoading"
            :is-loading="isLoading"
            @click.prevent.stop="createForm.submit"
          >
            {{ t('views.auth.ProfileOverview.button.createChannel') }}
          </Button>
        </template>
      </Modal>
    </Section>
  </Layout>
</template>
