<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'

import Nav from '~/components/ui/Nav.vue'
import Spacer from '~/components/ui/Spacer.vue'

const { t } = useI18n()
const route = useRoute()

const tabs = ref([{
  title: t('views.content.Base.link.libraries'),
  to: { name: 'content.libraries.index'}
},
{
  title: t('views.content.Base.link.tracks'),
  to: { name: 'content.libraries.files' }
}])

const labels = computed(() => ({
  secondaryMenu: t('views.content.Base.menu.secondary'),
  title: t('views.content.Base.title')
}))
</script>

<template>
  <main
    v-title="labels.title"
    class="main"
  >
    <Nav
      v-model="tabs"
      :aria-label="labels.secondaryMenu"
    />
    <Spacer />
    <router-view :key="route.fullPath" />
  </main>
</template>
