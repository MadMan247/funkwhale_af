<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'

import Layout from '~/components/ui/Layout.vue'
import Nav from '~/components/ui/Nav.vue'

const { t } = useI18n()

const labels = computed(() => ({
  manageUsers: t('views.admin.users.Base.title'),
  secondaryMenu: t('views.admin.users.Base.menu.secondary')
}))

const tabs = ref([
  {
    title: t('views.admin.users.Base.link.users'),
    to: { name: 'manage.users.users.list' }
  },

  {
    title: t('views.admin.users.Base.link.invitations'),
    to: { name: 'manage.users.invitations.list' }
  }
])
</script>

<template>
  <Layout
    v-title="labels.manageUsers"
    main
    stack
  >
    <Nav v-model="tabs" />

    <router-view :key="useRoute().fullPath" />
  </Layout>
</template>
