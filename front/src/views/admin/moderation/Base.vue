<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { computed, ref } from 'vue'
import { get } from 'lodash-es'
import { useStore } from '~/store'
import { useRoute } from 'vue-router'

import axios from 'axios'

import Layout from '~/components/ui/Layout.vue'
import Nav from '~/components/ui/Nav.vue'


const store = useStore()
const { t } = useI18n()
const route = useRoute()

const allowListEnabled = ref(false)
const labels = computed(() => ({
  moderation: t('views.admin.moderation.Base.title'),
  secondaryMenu: t('views.admin.moderation.Base.menu.secondary')
}))

const tabs = ref([{
  title: t('views.admin.moderation.Base.link.reports'),
  to: { name: 'manage.moderation.reports.list', query: { q: 'resolved:no' } },
  badge: store.state.ui.notifications.pendingReviewReports > 0 ? store.state.ui.notifications.pendingReviewReports : undefined

}, {
  title: t('views.admin.moderation.Base.link.userRequests'),
  to: { name: 'manage.moderation.requests.list', query: { q: 'status:pending' } },
  badge: store.state.ui.notifications.pendingReviewRequests > 0 ? store.state.ui.notifications.pendingReviewRequests : undefined
}, {
  title: t('views.admin.moderation.Base.link.domains'),
  to: { name: 'manage.moderation.domains.list' }
}, {
  title: t('views.admin.moderation.Base.link.accounts'),
  to: { name: 'manage.moderation.accounts.list' }
}
])

const fetchNodeInfo = async () => {
  const response = await axios.get('instance/nodeinfo/2.1/')
  allowListEnabled.value = get(response.data, 'metadata.allowList.enabled', false)
}

fetchNodeInfo()
</script>

<template>
  <!-- TODO: Replace with Tabs component -->
  <Layout
    v-title="labels.moderation"
    main
    no-gap
  >
    <Nav v-model="tabs" />

    <router-view
      :key="route.fullPath"
      :allow-list-enabled="allowListEnabled"
    />
  </Layout>
</template>
