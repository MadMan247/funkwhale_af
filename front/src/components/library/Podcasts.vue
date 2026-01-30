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

import ChannelCard from '~/components/audio/ChannelCard.vue'
import RemoteSearchForm from '~/components/RemoteSearchForm.vue'
import ChannelForm from '~/components/audio/ChannelForm.vue'

import useUrlParamCache from '~/ui/composables/useUrlParamCache.ts'
import useSharedLabels from '~/composables/locale/useSharedLabels'
import useOrdering from '~/composables/navigation/useOrdering'
import useErrorHandler from '~/composables/useErrorHandler'
import usePage from '~/composables/navigation/usePage'
import useLogger from '~/composables/useLogger'
import { useRoute, useRouter } from 'vue-router'

import Layout from '~/components/ui/Layout.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Header from '~/components/ui/Header.vue'
import Card from '~/components/ui/Card.vue'
import Button from '~/components/ui/Button.vue'
import Input from '~/components/ui/Input.vue'
import Alert from '~/components/ui/Alert.vue'
import Pills from '~/components/ui/Pills.vue'
import Pagination from '~/components/ui/Pagination.vue'
import Modal from '~/components/ui/Modal.vue'
import Nav from '~/components/ui/Nav.vue'

interface Props extends OrderingProps {
  scope?: 'me' | 'subscribed' | 'domain' | 'all'

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

// TODO: Check if this is necessary (the following line has no effect)
const q = useRouteQuery('query', '')
const query = ref(q.value)
syncRef(q, query, { direction: 'ltr' })

const result = ref<PaginatedChannelList>()

const widgetKey = ref(new Date().toLocaleString())

const orderingOptions: [OrderingField, keyof typeof sharedLabels.filters][] = [
  ['creation_date', 'creation_date'],
  ['name', 'name']
]

const { t } = useI18n()
const router = useRouter()
const logger = useLogger()
const sharedLabels = useSharedLabels()

const { onOrderingUpdate, orderingString, paginateBy, ordering, orderingDirection } = useOrdering(props)

const store = useStore()
const dataStore = useDataStore()

const tabs = ref([
  { title: t("components.library.Podcasts.tabs.me"), name: 'me' },
  { title: t("components.library.Podcasts.tabs.subscribed"), name: 'subscribed' },
  { title: t("components.library.Podcasts.tabs.domain"), name: 'domain:' + store.getters['instance/domain'] },
  { title: t("components.library.Podcasts.tabs.all"), name: 'all' }
])
const scope = useUrlParamCache('scope', { fallback: props.scope })

const scopeFilter = computed(() => {
  if (scope.value === 'subscribed') return 'all'
  else return scope.value
  return undefined
})

const subscribedFilter = computed(() => {
  if (scope.value === 'subscribed') return true
  else return undefined
})

const isLoading = ref(false)
const fetchData = async () => {
  isLoading.value = true
  const params : operations['get_channels']['parameters']['query'] = {
    scope: scopeFilter.value,
    subscribed: subscribedFilter.value,
    content_category: 'podcast',
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

watch(() => store.state.moderation.lastUpdate, fetchData)

watch([page, tags, q, ordering, orderingDirection, scope], fetchData)

watch([tags, q, ordering, orderingDirection, scope], () => {
  page.value = 1
})

const route = useRoute()
watch(() => route.query.scope, async (newScope) => {
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

fetchData()

const search = () => {
  page.value = 1
  q.value = query.value
}

onOrderingUpdate(() => {
  page.value = 1
  fetchData()
})

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
const showCreateModal = ref(false)
</script>

<template>
  <Layout
    stack
    main
  >
    <Header
      page-heading
      :h1="t('components.library.Podcasts.header.browse')"
      :action="{
        text: scope === 'me' ? t('views.channels.List.link.addNew') : t('views.channels.List.link.addRemote'),
        // @ts-ignore
        onClick: () => {
          if (scope === 'me') { showCreateModal = true }
          else { showSubscribeModal = true }
        },
        // @ts-ignore
        primary: true,
        // @ts-ignore
        icon: 'bi-plus'
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
    <Nav
      v-model="tabs"
      tab-query-field="scope"
    >
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
            @click="channelIsOpen = false"
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
  </Layout>
</template>
