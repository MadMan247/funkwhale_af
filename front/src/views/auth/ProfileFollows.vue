<script setup lang="ts">
import type { Actor } from '~/types'

import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'

import FollowWidget from '~/components/federation/FollowWidget.vue'
import Layout from '~/components/ui/Layout.vue'
import Header from '~/components/ui/Header.vue'

interface Props {
  object?: Actor
}

const props = defineProps<Props>()

const { t } = useI18n()
const store = useStore()

const domain = computed(() => {
  if (props.object?.domain) return 'https://' + props.object?.domain
  else return store.state.instance.instanceUrl
})
</script>

<template>
  <Layout
    main
    stack
    gap-84
  >
    <Header
      :h1="t('views.auth.ProfileBase.link.follows')"
      page-heading
    />
    <follow-widget
      :title="t('components.library.Home.header.followers')"
      :url="`${domain}/federation/actors/${props.object?.name}/followers`"
      :page-size="8"
    />
    <follow-widget
      :title="t('components.library.Home.header.following')"
      :url="`${domain}/federation/actors/${props.object?.name}/following`"
      :page-size="8"
    />
  </Layout>
</template>
