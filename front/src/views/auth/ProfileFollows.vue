<script setup lang="ts">
import type { Actor } from '~/types'

import { computed, onMounted } from 'vue'
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

const isOwnProfile = computed(() => {
  return props.object?.full_username === store.state.auth.profile?.full_username
})

onMounted(() => {
  if (isOwnProfile.value) {
    store.dispatch('users/fetchFollows')
    store.dispatch('users/fetchIncomingFollows')
  }
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
      :is-own-profile="isOwnProfile"
    />
    <follow-widget
      :title="t('components.library.Home.header.following')"
      :url="`${domain}/federation/actors/${props.object?.name}/following`"
      :page-size="8"
      :is-own-profile="isOwnProfile"
    />
  </Layout>
</template>
