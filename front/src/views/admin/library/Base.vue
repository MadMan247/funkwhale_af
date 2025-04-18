<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'

import Layout from '~/components/ui/Layout.vue'
import Nav from '~/components/ui/Nav.vue'

const { t } = useI18n()
const labels = computed(() => ({
  title: t('views.admin.library.Base.title'),
  secondaryMenu: t('views.admin.library.Base.menu.secondary')
}))

const tabs = ref([
  {
    title: t('views.admin.library.Base.link.edits'),
    to: {name: 'manage.library.edits'}
  }, {
    title: t('views.admin.library.Base.link.channels'),
    to: {name: 'manage.channels'}
  }, {
    title: t('views.admin.library.Base.link.artists'),
    to: {name: 'manage.library.artists'}
  }, {
    title: t('views.admin.library.Base.link.albums'),
    to: {name: 'manage.library.albums'}
  }, {
    title: t('views.admin.library.Base.link.tracks'),
    to: {name: 'manage.library.tracks'}
  }, {
    title: t('views.admin.library.Base.link.libraries'),
    to: {name: 'manage.library.libraries'}
  }, {
    title: t('views.admin.library.Base.link.uploads'),
    to: {name: 'manage.library.uploads'}
  }, {
    title: t('views.admin.library.Base.link.tags'),
    to: {name: 'manage.library.tags'}
  }
])

const route = useRoute()
</script>

<template>
  <Layout
    v-title="labels.title"
    main
    stack
    class="page-admin-library"
  >
    <Nav v-model="tabs" />

    <router-view :key="route.fullPath" />
  </Layout>
</template>
