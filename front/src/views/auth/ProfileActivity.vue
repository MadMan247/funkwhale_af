<script setup lang="ts">
import type { Actor } from '~/types'

import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'

import TrackWidget from '~/components/audio/track/Widget.vue'
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

    <track-widget
      :url="'history/listenings/'"
      :filters="{ scope: scope, ordering: '-creation_date', playable: true, ...qualityFilters}"
      :websocket-handlers="['Listen']"
      :title="t('components.library.Home.header.recentlyListened')"
      @count="recentActivity = $event"
    />
    <track-widget
      :url="'favorites/tracks/'"
      :filters="{ scope: scope, playable: true, ordering: '-creation_date'}"
      :title="t('components.library.Home.header.recentlyFavorited')"
    />
    <album-widget
      :filters="{ scope: scope, playable: true, ordering: '-creation_date', ...qualityFilters}"
      :limit="8"
      :title="t('components.library.Home.header.recentlyAdded')"
    />
  </Layout>
</template>
