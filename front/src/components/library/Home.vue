<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import { useStore } from '~/store'
import { useUrlParamStore } from '~/ui/stores/urlParam.ts'

import AlbumWidget from '~/components/album/Widget.vue'
import ChannelsWidget from '~/components/audio/ChannelsWidget.vue'
import ListeningWidget from '~/components/audio/listening/Widget.vue'
import FollowWidget from '~/components/federation/FollowWidget.vue'
import PlaylistWidget from '~/components/playlists/Widget.vue'

import Header from '~/components/ui/Header.vue'
import Layout from '~/components/ui/Layout.vue'
import Nav from "~/components/ui/Nav.vue"
import Spacer from '~/components/ui/Spacer.vue'

const store = useStore()
const qualityFilters = computed(() => store.getters['instance/qualityFilters'])

const { t } = useI18n()
const labels = computed(() => ({
  title: t('components.library.Home.title')
}))

const tabs = [
  { title: t("components.library.Home.tabs.me"), name: 'me' },
  { title: t("components.library.Home.tabs.subscribed"), name: 'from_subscribed' },
  { title: t("components.library.Home.tabs.domain"), name: `domain:${store.getters['instance/domain']}` },
  { title: t("components.library.Home.tabs.all"), name: 'all' }
]
const scope = useUrlParamStore('scope', {
  allowedValues: [undefined, 'subscribed', ...tabs.map(t => t.name)] as const
})
if (scope.value === 'subscribed')
  scope.value = 'from_subscribed'
else if (!scope.value)
  scope.value = 'all'
</script>

<template>
  <Layout
    v-title="labels.title"
    main
    stack
  >
    <Header
      page-heading
      :h1="labels.title"
    />
    <Nav
      :model-value="tabs"
      tab-query-field="scope"
    />
    <Spacer />
    <ListeningWidget
      :title="t('components.library.Home.header.recentlyListened')"
      url="history/listenings"
      :query="{
        scope,
        ordering: '-creation_date',
        ...qualityFilters
      }"
      :websocket-handlers="['Listen']"
    />
    <Spacer />
    <ListeningWidget
      :title="t('components.library.Home.header.recentlyFavorited')"
      url="favorites/tracks"
      :query="{
        scope,
        ordering: '-creation_date'
      }"
    />
    <Spacer />
    <AlbumWidget
      :title="t('components.library.Home.header.recentlyAdded')"
      :query="{
        include_channels: true,
        playable: true,
        scope,
        page_size: 4,
        ordering: ['-creation_date'],
        ...qualityFilters
      }"
    />
    <Spacer />
    <PlaylistWidget
      :title="t('components.library.Home.header.playlists')"
      :query="{
        playable: true,
        scope,
        ordering:'-modification_date',
        page_size: 4
      }"
    />
    <Spacer />
    <ChannelsWidget
      :title="t('components.library.Home.header.newChannels')"
      :query="{
        content_category: 'music',
        scope,
        ordering: ['-creation_date'],
        page_size: 4
      }"
      show-modification-date
    />
    <Spacer />
    <ChannelsWidget
      :title="t('components.library.Home.header.podcasts')"
      :query="{
        content_category: 'podcast',
        // playable: true, // Not a valid param!
        scope,
        page_size: 4,
        ordering: ['-creation_date']
      }"
    />
    <Spacer />
    <!-- TODO: Refactor follow-widget to use data store (for deduplication, rate-limiting, caching etc.) -->
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
