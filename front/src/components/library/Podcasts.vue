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
import { useStore } from '~/store'
import { useDataStore } from '~/ui/stores/data'
import { useModal } from '~/ui/composables/useModal.ts'

import axios from 'axios'

import ChannelsWidget from '~/components/audio/ChannelsWidget.vue'
import RemoteSearchForm from '~/components/RemoteSearchForm.vue'
import ChannelForm from '~/components/audio/ChannelForm.vue'

import useSharedLabels from '~/composables/locale/useSharedLabels'
import useOrdering from '~/composables/navigation/useOrdering'
import useErrorHandler from '~/composables/useErrorHandler'
import usePage from '~/composables/navigation/usePage'
import useLogger from '~/composables/useLogger'
import { useRouter } from 'vue-router'


import Layout from '~/components/ui/Layout.vue'
import Section from '~/components/ui/Section.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Header from '~/components/ui/Header.vue'
import Card from '~/components/ui/Card.vue'
import Button from '~/components/ui/Button.vue'
import Input from '~/components/ui/Input.vue'
import Alert from '~/components/ui/Alert.vue'
import Pills from '~/components/ui/Pills.vue'
import Pagination from '~/components/ui/Pagination.vue'
import Modal from '~/components/ui/Modal.vue'

interface Props extends OrderingProps {
  scope?: 'me' | 'all'

  // TODO(wvffle): Remove after https://github.com/vuejs/core/pull/4512 is merged
  orderingConfigName?: RouteRecordName,
  defaultQuery?: string
}

const props = withDefaults(defineProps<Props>(), {
  scope: 'all',
  orderingConfigName: undefined,
  defaultQuery: ''
})

const page = usePage()

const createForm = ref()
const step = ref(1)
const category = ref('podcast')
const modalContent = ref()
const submittable = ref(false)

const tags = useRouteQuery<string[]>('tag', [])

const subscribedQuery = ref(props.defaultQuery)
const q = useRouteQuery('query', '')
const query = ref(q.value)
syncRef(q, query, { direction: 'ltr' })

const result = ref<PaginatedChannelList>()

const widgetKey = ref(new Date().toLocaleString())

const orderingOptions: [OrderingField, keyof typeof sharedLabels.filters][] = [
  ['creation_date', 'creation_date'],
  ['name', 'name']
]

const router = useRouter()
const logger = useLogger()
const sharedLabels = useSharedLabels()

const { onOrderingUpdate, orderingString, paginateBy, ordering, orderingDirection } = useOrdering(props)

const isLoading = ref(false)
const fetchData = async () => {
  isLoading.value = true
  const params : operations['get_channels']['parameters']['query'] = {
    scope: props.scope,
    page: page.value,
    page_size: paginateBy.value,
    q: query.value,
    ordering: [orderingString.value] as ("creation_date" | "modification_date" | "-creation_date" | "-modification_date" | "-random" | "random")[],
    tag: tags.value
  }

  const measureLoading = logger.time('Fetching podcasts')
  try {
    const response = await axios.get<PaginatedChannelList>('channels/', {
      params,
      paramsSerializer: {
        indexes: null
      }
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
const dataStore = useDataStore()
watch(() => store.state.moderation.lastUpdate, fetchData)
watch([page, tags, q, ordering, orderingDirection], fetchData)
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
  searchPlaceholder: t('components.library.Podcasts.placeholder.search'),
  title: t('components.library.Podcasts.title')
}))

const paginateOptions = computed(() => sortedUniq([12, 30, 50, paginateBy.value].sort((a, b) => a - b)))

const { isOpen: subscribeIsOpen, to: subscribe } = useModal('subscribe')
const { isOpen: channelIsOpen } = useModal('channel')
const { to: upload } = useModal('upload')

const reloadWidget = () => (widgetKey.value = new Date().toLocaleString())
const showSubscribeModal = ref(false)
</script>

<template>
  <Layout
    stack
    main
  >
    <Spacer no-size />
    <Section
      v-if="store.state.auth.authenticated"
      :h1="t('components.library.Podcasts.header.title')"
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
        :filters="{q: subscribedQuery, subscribed: 'true', content_category:'podcast'}"
      />
    </Section>
    <Header
      page-heading
      :h1="t('components.library.Podcasts.header.browse')"
      :action="{
        text: t('views.channels.SubscriptionsList.link.addNew'),
        onClick: () => { channelIsOpen = true },
        icon: 'bi-plus',
        primary: true
      }"
    />
    <Layout
      form
      flex
      :class="['ui', {'loading': isLoading}, 'form']"
      @submit.prevent="search"
    >
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
      <Layout
        stack
        no-gap
        label
        for="artist-ordering"
      >
        <span class="label">
          {{ t('components.library.Podcasts.ordering.label') }}
        </span>
        <select
          id="artist-ordering"
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
        for="artist-ordering-direction"
      >
        <span class="label">
          {{ t('components.library.Podcasts.ordering.direction.label') }}
        </span>
        <select
          id="artist-ordering-direction"
          v-model="orderingDirection"
          class="dropdown"
        >
          <option value="+">
            {{ t('components.library.Podcasts.ordering.direction.ascending') }}
          </option>
          <option value="-">
            {{ t('components.library.Podcasts.ordering.direction.descending') }}
          </option>
        </select>
      </Layout>
      <Layout
        stack
        no-gap
        label
        for="artist-results"
      >
        <span class="label">
          {{ t('components.library.Podcasts.pagination.results') }}
        </span>
        <select
          id="artist-results"
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
    <Layout
      v-if="result && result.results.length > 0"
      grid
      style="display:flex; flex-wrap:wrap; gap: 32px; margin-top:32px;"
    >
      <channels-widget
        :key="widgetKey"
        :limit="paginateBy"
        :show-modification-date="true"
        :filters="{q: query, subscribed: 'false', content_category:'podcast'}"
      />
    </Layout>
    <Layout
      v-else-if="result && result.results.length === 0"
      stack
    >
      <Alert yellow>
        {{ t('components.library.Podcasts.empty.noResults') }}
      </Alert>
      <Layout flex>
        <Card
          v-if="store.state.auth.authenticated"
          :title="t('components.library.Podcasts.button.feed')"
          solid
          small
          primary
          style="text-align: center;"
          :to="subscribe"
        >
          <template #image>
            <i
              class="bi bi-plus"
              style="font-size: 100px; position: relative; top: 50px;"
            />
          </template>
        </Card>
        <Card
          v-if="store.state.auth.authenticated"
          :title="t('components.library.Podcasts.button.channel')"
          solid
          small
          primary
          style="text-align: center;"
          :to="upload"
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
      :page="page"
      :pages="Math.ceil((result?.results.length || 0)/paginateBy)"
    />
    <Modal
      v-model="subscribeIsOpen"
      :title="t('components.library.Podcasts.modal.subscription.header')"
      :cancel="t('components.library.Podcasts.button.cancel')"
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
          @subscribed="subscribeIsOpen = false; fetchData()"
        />
      </div>
      <template #actions>
        <Button
          primary
          form="remote-search"
          type="submit"
        >
          <i class="bookmark icon" />
          {{ t('components.library.Podcasts.button.subscribe') }}
        </Button>
      </template>
    </Modal>

    <Modal
      v-model="channelIsOpen"
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
          @click="channelIsOpen = false"
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
  </Layout>
</template>
