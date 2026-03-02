<script setup lang="ts">
import type { Actor } from '~/types'

import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'

import ListeningWidget from '~/components/audio/listening/Widget.vue'
import AlbumWidget from '~/components/album/Widget.vue'
import Layout from '~/components/ui/Layout.vue'
import Header from '~/components/ui/Header.vue'

interface Props {
  object?: Actor
}

const props = defineProps<Props>()

const recentActivity = ref(0)

const store = useStore()
const qualityFilters = computed(() => store.getters['instance/qualityFilters'])

const { t } = useI18n()

const scope = computed(() =>
  store.state.auth.authenticated && props.object?.full_username === store.state.auth.fullUsername
    ? 'me'
    : `actor:${props.object?.full_username ?? ''}`
)

</script>

<template>
  <Layout
    main
    stack
    gap-84
  >
    <Header
      :h1="t('views.auth.ProfileBase.link.activity')"
      page-heading
    />

    <ListeningWidget
      :query="{
        playable: true,
        ordering: '-creation_date',
        scope,
        ...qualityFilters
      }"
      :title="t('components.library.Home.header.recentlyListened')"
      url="history/listenings"
      :websocket-handlers="['Listen']"
      @count="recentActivity = $event"
    />
    <ListeningWidget
      :title="t('components.library.Home.header.recentlyFavorited')"
      url="favorites/tracks"
      :query="{
        //playable: true, /*TODO: according to schema, `playable` is not available for this endpoint. Investigate! */
        ordering: '-creation_date',
        scope
      }"
    />
    <AlbumWidget
      :title="t('components.library.Home.header.recentlyAdded')"
      :query="{
        scope,
        ordering: ['-creation_date'],
        page_size: 8,
        ...qualityFilters
      }"
    />
  </Layout>
</template>
