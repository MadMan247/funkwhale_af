<script setup lang="ts">
import { syncRef } from '@vueuse/core'
import { useRouteQuery } from '@vueuse/router'
import { sortedUniq } from 'lodash-es'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import { useRouter } from 'vue-router'
import useSharedLabels from '~/composables/locale/useSharedLabels'
import type { OrderingProps } from '~/composables/navigation/useOrdering'
import useOrdering from '~/composables/navigation/useOrdering'
import usePage from '~/composables/navigation/usePage'
import { useStore } from '~/store'
import type { OrderingField } from '~/store/ui'
import { useModal } from '~/ui/composables/useModal.ts'
import { useDataStore } from '~/ui/stores/data'
import { useUrlParamStore } from '~/ui/stores/urlParam'

import ChannelCard from '~/components/audio/ChannelCard.vue'
import ChannelForm from '~/components/audio/ChannelForm.vue'
import RemoteSearchForm from '~/components/RemoteSearchForm.vue'

import Alert from '~/components/ui/Alert.vue'
import Button from '~/components/ui/Button.vue'
import Card from '~/components/ui/Card.vue'
import Header from '~/components/ui/Header.vue'
import Input from '~/components/ui/Input.vue'
import Layout from '~/components/ui/Layout.vue'
import Modal from '~/components/ui/Modal.vue'
import Nav from '~/components/ui/Nav.vue'
import Pagination from '~/components/ui/Pagination.vue'
import Pills from '~/components/ui/Pills.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Select from '../ui/Select.vue'

const props = defineProps<OrderingProps>()

  const router = useRouter()
  const store = useStore()
  const { t } = useI18n()

// Query

const tabs = [
  { title: t("components.library.Podcasts.tabs.me"), name: 'me' },
  { title: t("components.library.Podcasts.tabs.subscribed"), name: 'subscribed' },
  { title: t("components.library.Podcasts.tabs.domain"), name: 'domain:' + store.getters['instance/domain'] },
  { title: t("components.library.Podcasts.tabs.all"), name: 'all' }
]
const scope = useUrlParamStore('scope', {
  allowedValues: [undefined, 'from_subscribed', ...tabs.map(t => t.name)] as const
})
// TODO: Possibly wrong translation here. https://hub.funkwhale.audio/funkwhale/pl/cmrtish3stbp7fn76gyfo4ywkw
if (scope.value === 'subscribed')
  scope.value = 'all'
else if (scope.value === 'from_subscribed')
  scope.value = 'subscribed'
else if (!scope.value)
  scope.value = 'all'

const tags = useUrlParamStore('tag', { allowedValues: 'array' })

const q = useRouteQuery('query', '')
const query = ref(q.value)
syncRef(q, query, { direction: 'ltr' })

// Pagination

const page = usePage()

const orderingOptions = {
  creation_date: useSharedLabels().filters.creation_date,
  name: useSharedLabels().filters.name
} satisfies Partial<Record<OrderingField, string>>

const directionOptions = {
  '+':  t('components.library.Podcasts.ordering.direction.ascending'),
  '-': t('components.library.Podcasts.ordering.direction.descending')
}

const paginateOptions = computed<Record<number, string>>(() => Object.fromEntries(sortedUniq([
  12,
  30,
  50,
  paginateBy.value
].toSorted((a, b) => a - b)).map(v => [v, String(v)])))

const { orderingString, paginateBy, ordering, orderingDirection } = useOrdering(props)

watch([tags, q, ordering, orderingDirection, scope], () => {
  page.value = 1
})

// Search result

const podcasts = computed(() => useDataStore().channels({
  scope: scope.value,
  subscribed: scope.value === 'subscribed', // TODO: Check if binary or ternary type here!
  content_category: 'podcast',
  page: page.value,
  page_size: paginateBy.value,
  q: query.value,
  // @ts-expect-error TODO: add strict types to useOrdering
  ordering: [orderingString.value], // TODO: Check if an array is expected here
  tag: tags.value
}, {
  refetchSignal: [store.state.moderation.lastUpdate, subscribeIsOpen]
}).value)

// UI state

// TODO: Tidy up...

const step = ref(1)
const category = ref('podcast')
const modalContent = ref()
const createForm = ref()
const submittable = ref(false)
const isLoading = ref(false) // Confusion: what exactly is loading? Not the podcast request.

// Might be better inline (`:isOpen: "useModal('subscribe').isOpen"`) so that we don't need to rename `isOpen`.
const { isOpen: subscribeIsOpen, to: subscribe } = useModal('subscribe')
const { isOpen: channelIsOpen } = useModal('channel')
const { to: upload } = useModal('upload')

// Can be implemented with `generation` (start at 0, increment with `++`)
const widgetKey = ref(new Date().toLocaleString())
const reloadWidget = () => {
  widgetKey.value = new Date().toLocaleString()
}

// names feel confusing (`subscribeIsOpen` vs `showSubscribeModal` etc.) - can we use `useModal` here?)
const showSubscribeModal = ref(false)
const showCreateModal = ref(false)
</script>

<template>
  <Layout
    v-title="t('components.library.Podcasts.title')"
    stack
    main
  >
    <Header
      page-heading
      :h1="t('components.library.Podcasts.header.browse')"
      :action="{
        text: scope === 'me'
          ? t('views.channels.List.link.addNew')
          : t('views.channels.List.link.addRemote'),
        onClick: () => {
          if (scope === 'me')
            showCreateModal = true
          else
            showSubscribeModal = true
        },
        primary: true,
        icon: 'bi-plus'
      }"
    />

    <!-- Filters -->

    <Layout
      form
      flex
      @submit.prevent="podcasts.refetch"
    >
      <Input
        id="podcast-search"
        v-model="query"
        search
        name="search"
        :label="t('components.library.Podcasts.label.search')"
        autofocus
        :placeholder="t('components.library.Podcasts.placeholder.search')"
      />
      <Pills
        :get="model => { tags = model.currents.map(({ label }) => label) }"
        :set="_ => ({
          currents: tags.map(tag => ({ type: 'custom' as const, label: tag })),
          others: useDataStore().tags().value
            .filter(({ name }) => podcasts.data?.results?.some((object) => object.artist.tags?.includes(name)) && !tags.includes(name))
            .map(({ name }) => ({ type: 'preset' as const, label: name })),
        })"
        :label="t('components.library.Podcasts.label.tags')"
        style="max-width: 350px;"
      />
      <Select
        v-model="ordering"
        :options="orderingOptions"
        :label="t('components.library.Podcasts.ordering.label')"
        style="flex-grow: 0"
      />
      <Select
        v-model="orderingDirection"
        :options="directionOptions"
        :label="t('components.library.Podcasts.ordering.direction.label')"
        style="flex-grow: 0"
      />
      <Select
        v-model="paginateBy"
        :options="paginateOptions"
        :label="t('components.library.Podcasts.pagination.results')"
        style="flex-grow: 0"
      />
    </Layout>

    <!-- Results -->

    <Nav
      :model-value="tabs"
      tab-query-field="scope"
    >
      <template v-if="podcasts.data">
        <Layout
          v-if="podcasts.data.count > 0"
          flex
        >
          <channel-card
            v-for="channel in podcasts.data.results"
            :key="channel.uuid"
            :object="channel"
          />
        </Layout>
        <Layout
          v-else-if="podcasts.data.count === 0"
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
          v-if="page && podcasts.data && podcasts.data.count > paginateBy"
          :page="page"
          :pages="Math.ceil(podcasts.data.count/paginateBy)"
        />
      </template>
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
            @subscribed="subscribeIsOpen = false"
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
        <!-- Todo: Replace event listeners with v-model to make possible states explicit -->
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
