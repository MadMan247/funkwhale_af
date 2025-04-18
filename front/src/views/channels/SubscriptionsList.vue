<script setup lang="ts">
import type { Channel } from '~/types'

import { useI18n } from 'vue-i18n'
import { ref, computed } from 'vue'

import axios from 'axios'

import ChannelsWidget from '~/components/audio/ChannelsWidget.vue'
import RemoteSearchForm from '~/components/RemoteSearchForm.vue'
import Layout from '~/components/ui/Layout.vue'
import Header from '~/components/ui/Header.vue'
import Button from '~/components/ui/Button.vue'
import Modal from '~/components/ui/Modal.vue'

import useErrorHandler from '~/composables/useErrorHandler'

interface Props {
  defaultQuery?: string
}

const props = withDefaults(defineProps<Props>(), {
  defaultQuery: ''
})

const query = ref(props.defaultQuery)
const widgetKey = ref(new Date().toLocaleString())

const { t } = useI18n()
const labels = computed(() => ({
  title: t('views.channels.SubscriptionsList.title'),
  searchPlaceholder: t('views.channels.SubscriptionsList.placeholder.search')
}))

const previousPage = ref()
const nextPage = ref()
const channels = ref([] as Channel[])
const count = ref(0)
const isLoading = ref(false)
const fetchData = async () => {
  isLoading.value = true

  try {
    const response = await axios.get('channels/', { params: { subscribed: 'true', q: query.value } })
    previousPage.value = response.data.previous
    nextPage.value = response.data.next
    channels.value.push(...response.data.results)
    count.value = response.data.count
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}
fetchData()

const reloadWidget = () => (widgetKey.value = new Date().toLocaleString())
const showSubscribeModal = ref(false)
</script>

<template>
  <Layout
    v-title="labels.title"
    stack
    main
  >
    <!-- TODO: `yarn lint:tsc` doesn't understand the `Prop` type for `Header` while the language server does. It may be a question of typescript version... Investigate and fix! https://dev.funkwhale.audio/funkwhale/funkwhale/-/issues/2437 -->
    <!-- @vue-ignore -->
    <Header
      :h1="labels.title"
      :action="{
        text: t('views.channels.SubscriptionsList.link.addNew'),
        // @ts-ignore
        onClick: () => { showSubscribeModal = true },
        // @ts-ignore
        primary: true,
        // @ts-ignore
        icon: 'bi-plus'
      }"
      page-heading
    />
    <Modal
      v-model="showSubscribeModal"
      :title="t('views.channels.SubscriptionsList.modal.subscription.header')"
      class="tiny"
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

    <inline-search-bar
      v-model="query"
      :placeholder="labels.searchPlaceholder"
      @search="reloadWidget"
    />
    <channels-widget
      :key="widgetKey"
      :limit="50"
      :show-modification-date="true"
      :filters="{q: query, subscribed: 'true', ordering: '-modification_date'}"
    />
  </Layout>
</template>
