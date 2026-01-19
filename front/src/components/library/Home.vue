<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { ref, computed, watch } from 'vue'
import { useStore } from '~/store'
import { useRoute, useRouter } from 'vue-router'

import useUrlParamCache from '~/ui/composables/useUrlParamCache.ts'

import ChannelsWidget from '~/components/audio/ChannelsWidget.vue'
import PlaylistWidget from '~/components/playlists/Widget.vue'
import TrackWidget from '~/components/audio/track/Widget.vue'
import AlbumWidget from '~/components/album/Widget.vue'
import FollowWidget from '~/components/federation/FollowWidget.vue'
import Header from '~/components/ui/Header.vue'
import Layout from '~/components/ui/Layout.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Nav from "~/components/ui/Nav.vue"


interface Props {
  scope?: 'me' | 'from_subscribed' | 'domain' | 'all'
}

const props = withDefaults(defineProps<Props>(), {
  scope: 'me'
})

const store = useStore()
const route = useRoute()
const qualityFilters = computed(() => store.getters['instance/qualityFilters'])

const { t } = useI18n()
const labels = computed(() => ({
  title: t('components.library.Home.title')
}))

const tabs = ref([
  { title: t("components.library.Home.tabs.me"), name: 'me'},
  { title: t("components.library.Home.tabs.subscribed"), name: 'from_subscribed'},
  { title: t("components.library.Home.tabs.domain"), name: 'domain:' + store.getters['instance/domain']},
  { title: t("components.library.Home.tabs.all"), name: 'all'}
])

const scope = useUrlParamCache('scope', { fallback: props.scope })

const router = useRouter()
watch(() => route.query.scope, async (newScope) => {
  const scopeQuery = Array.isArray(newScope) ? newScope[0] : newScope
  if (!scopeQuery) {
    await router.replace({
      ...route,
      query: { ...route.query, scope: scope.value }
    })
  } else if (scopeQuery === 'subscribed') {
    await router.replace({
      ...route,
      query: { ...route.query, scope: 'from_subscribed' }
    })
  }
}, { immediate: true })

</script>

<template>
  <Layout
    :key="route?.name ?? undefined"
    v-title="labels.title"
    main
    stack
  >
    <Header
      page-heading
      :h1="labels.title"
    />
    <Nav
      v-model="tabs"
      tab-query-field="scope"
    />
    <Spacer />
    <track-widget
      :title="t('components.library.Home.header.recentlyListened')"
      :url="'history/listenings/'"
      :filters="{ scope: scope, ordering: '-creation_date', ...qualityFilters }"
      :websocket-handlers="['Listen']"
    />
    <Spacer />
    <track-widget
      :title="t('components.library.Home.header.recentlyFavorited')"
      :url="'favorites/tracks/'"
      :filters="{ scope: scope ?? '', ordering: '-creation_date' }"
    />
    <Spacer />
    <album-widget
      :filters="{ scope: scope ?? '', include_channels: true, playable: true, ordering: '-creation_date', ...qualityFilters }"
      :limit="4"
      :title="t('components.library.Home.header.recentlyAdded')"
    />
    <Spacer />
    <playlist-widget
      :url="'playlists/'"
      :filters="{ scope: scope ?? '', playable: true, ordering: '-modification_date', limit: 4 }"
      :title="t('components.library.Home.header.playlists')"
    />
    <Spacer />
    <channels-widget
      :limit="4"
      :filters="{ scope: scope ?? '', ordering: '-creation_date', content_category: 'music' }"
      :title="t('components.library.Home.header.newChannels')"
      :show-modification-date="true"
    />
    <Spacer />
    <channels-widget
      :limit="4"
      :filters="{ scope: scope ?? '', playable: true, ordering: '-creation_date', content_category: 'podcast' }"
      :title="t('components.library.Home.header.podcasts')"
    />
    <Spacer />
    <follow-widget
      v-if="scope === 'me'"
      :title="t('components.library.Home.header.following')"
      :url="`${store.state.instance.instanceUrl}federation/actors/${store.state.auth.profile?.username}/following`"
      :page-size="4"
    />
    <Spacer />
    <follow-widget
      v-if="scope === 'me'"
      :title="t('components.library.Home.header.followers')"
      :url="`${store.state.instance.instanceUrl}federation/actors/${store.state.auth.profile?.username}/followers`"
      :target="store.state.auth.profile?.id"
      :page-size="4"
    />
  </Layout>
</template>
