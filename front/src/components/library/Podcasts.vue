<script setup lang="ts">
import type { OrderingProps } from '~/composables/navigation/useOrdering'
import type { Artist, BackendResponse } from '~/types'
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

import RemoteSearchForm from '~/components/RemoteSearchForm.vue'
import ChannelForm from '~/components/audio/ChannelForm.vue'
import ArtistCard from '~/components/artist/Card.vue'

import useSharedLabels from '~/composables/locale/useSharedLabels'
import useOrdering from '~/composables/navigation/useOrdering'
import useErrorHandler from '~/composables/useErrorHandler'
import usePage from '~/composables/navigation/usePage'
import useLogger from '~/composables/useLogger'
import { useRouter } from 'vue-router'


import Layout from '~/components/ui/Layout.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Loader from '~/components/ui/Loader.vue'
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
  orderingConfigName?: RouteRecordName
}

const props = withDefaults(defineProps<Props>(), {
  scope: 'all',
  orderingConfigName: undefined
})

const page = usePage()

const createForm = ref()
const step = ref(1)
const category = ref('podcast')
const modalContent = ref()
const submittable = ref(false)

const tags = useRouteQuery<string[]>('tag', [])

const q = useRouteQuery('query', '')
const query = ref(q.value)
syncRef(q, query, { direction: 'ltr' })

const result = ref<BackendResponse<Artist>>()

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
  const params = {
    scope: props.scope,
    page: page.value,
    page_size: paginateBy.value,
    q: query.value,
    ordering: orderingString.value,
    tag: tags.value,
    include_channels: 'true',
    content_category: 'podcast'
  }

  const measureLoading = logger.time('Fetching podcasts')
  try {
    const response = await axios.get('artists/', {
      params,
      paramsSerializer: {
        indexes: null
      }
    })

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
</script>

<template>
  <Layout
    stack
    main
  >
    <!-- TODO: Find out why lint:tsc doesn't like `onClick` while language server does -->
    <!-- @vue-ignore -->
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
            .filter(({ name }) => result?.results?.some((object) => object.tags?.includes(name)) && !tags.includes(name))
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
      <Loader v-if="isLoading" />
      <artist-card
        v-for="artist in result.results"
        :key="artist.id"
        :artist="artist"
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
