<script setup lang="ts">
import type { OrderingProps } from '~/composables/navigation/useOrdering'
import type { OrderingField } from '~/store/ui'

import { computed, ref, watch } from 'vue'
import { useRouteQuery } from '@vueuse/router'
import { useI18n } from 'vue-i18n'
import { syncRef } from '@vueuse/core'
import { sortedUniq } from 'lodash-es'
import { useRouter } from 'vue-router'
import { useStore } from '~/store'
import { useDataStore } from '~/ui/stores/data'

import useSharedLabels from '~/composables/locale/useSharedLabels'
import { useModal } from '~/ui/composables/useModal.ts'
import usePage from '~/composables/navigation/usePage'
import useOrdering from '~/composables/navigation/useOrdering'

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
import { useUrlParamStore } from '~/ui/stores/urlParam'

const props = defineProps<OrderingProps>()

const router = useRouter()
const store = useStore()
const { t } = useI18n()

  // default scope all

// Query

const tabs = [
  { title: t("views.channels.List.tabs.me"), name: 'me' },
  { title: t("views.channels.List.tabs.subscribed"), name: 'subscribed' },
  { title: t("views.channels.List.tabs.domain"), name: 'domain:' + store.getters['instance/domain'] },
  { title: t("views.channels.List.tabs.all"), name: 'all' }
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
const query = ref(q.value ?? '')
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


const channels = computed(() => useDataStore().channels({
  scope: scope.value,
  subscribed: scope.value === 'subscribed' ? true : undefined, // TODO: Why is this different from Podcasts.vue? What is the correct type?
  content_category: 'music',
  page: page.value,
  page_size: paginateBy.value,
  q: query.value,
  // @ts-expect-error TODO: add strict types to useOrdering
  ordering: [orderingString.value], // TODO: Check if an array is expected here
  tag: tags.value
}, {
  refetchSignal: store.state.moderation.lastUpdate
}).value)


// UI state

// TODO: Tidy up

const step = ref(1)
const submittable = ref(false)
const category = ref('podcast')
const modalContent = ref()
const createForm = ref()
const isLoading = ref(false) // Confusion: what exactly is loading?

const widgetKey = ref(new Date().toLocaleString())
const reloadWidget = () => {
  widgetKey.value = new Date().toLocaleString()
}

// TODO: Check if we can use `useModal` here (for consistency)
const showSubscribeModal = ref(false)
const showCreateModal = ref(false)
</script>

<template>
  <!-- TODO: Check if 84px is the correct choice here -->
  <Layout
    stack
    main
    gap-84
  >
    <Spacer no-size />
    <Section
      :h1="t('views.auth.ProfileContent.header.channels')"
      large-section-heading
    >
      <template
        v-if="store.state.auth.authenticated"
        #action
      >
        <Button
          primary
          icon="bi-plus"
          @click="() => {
            if (scope === 'me') {
              showCreateModal = true
            } else {
              showSubscribeModal = true
            }
          }"
        >
          {{ scope === 'me'
            ? t('views.channels.List.link.addNew')
            : t('views.channels.List.link.addRemote')
          }}
        </Button>
      </template>
      <!-- Subscribe-Modal -->
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

      <!-- Filters -->

      <Layout
        form
        flex
        @submit.prevent="channels.refetch"
      >
        <!-- TODO: Translations -->
        <Input
          id="channel-search"
          v-model="query"
          search
          name="search"
          :label="t('components.library.Podcasts.label.search') /* TODO: Replace with Channels search label */"
          autofocus
          :placeholder="t('views.channels.List.placeholder.search')"
        />
        <Pills
          :get="model => { tags = model.currents.map(({ label }) => label) }"
          :set="_ => ({
            currents: tags.map(tag => ({ type: 'custom' as const, label: tag })),
            others: useDataStore().tags().value
              .filter(({ name }) => channels.data?.results?.some((object) => object.artist.tags?.includes(name)) && !tags.includes(name))
              .map(({ name }) => ({ type: 'preset' as const, label: name })),
          })"
          :label="t('components.library.Podcasts.label.tags') /* TODO: Replace with Channels label */"
          style="max-width: 350px;"
        />
        <Select
          v-model="ordering"
          :options="orderingOptions"
          :label="t('components.library.Podcasts.ordering.label')/* TODO: Replace with Channels label */"
          style="flex-grow: 0"
        />
        <Select
          v-model="orderingDirection"
          :options="directionOptions"
          :label="t('components.library.Podcasts.ordering.direction.label')/* TODO: Replace with Channels label */"
          style="flex-grow: 0"
        />
        <Select
          v-model="paginateBy"
          :options="paginateOptions"
          :label="t('components.library.Podcasts.pagination.results')/* TODO: Replace with Channels label */"
          style="flex-grow: 0"
        />
      </Layout>

      <!-- Results -->

      <Nav
        :model-value="tabs"
        tab-query-field="scope"
      >
        <Loader v-if="isLoading" />

        <template v-if="channels.data">
          <Pagination
            v-if="page && channels.data.count > paginateBy"
            v-model:page="page"
            :pages="Math.ceil(channels.data.count / paginateBy)"
          />
          <Layout
            v-if="channels.data.count > 0"
            flex
          >
            <channel-card
              v-for="channel in channels.data.results"
              :key="channel.uuid"
              :object="channel"
            />
          </Layout>
          <Layout
            v-else-if="channels.data.count === 0"
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
            v-if="page && channels.data.count > paginateBy"
            v-model:page="page"
            :pages="Math.ceil(channels.data.count / paginateBy)"
          />
        </template>
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
