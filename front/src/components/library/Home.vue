<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { ref, computed } from 'vue'
import { useStore } from '~/store'
import { useRoute } from 'vue-router'

import axios from 'axios'

import ChannelsWidget from '~/components/audio/ChannelsWidget.vue'
import PlaylistWidget from '~/components/playlists/Widget.vue'
import TrackWidget from '~/components/audio/track/Widget.vue'
import AlbumWidget from '~/components/album/Widget.vue'
import ArtistWidget from '~/components/artist/Widget.vue'
import Header from '~/components/ui/Header.vue'
import Layout from '~/components/ui/Layout.vue'
import Spacer from '~/components/ui/Spacer.vue'

import useErrorHandler from '~/composables/useErrorHandler'
import useLogger from '~/composables/useLogger'

interface Props {
  scope?: string
}

withDefaults(defineProps<Props>(), {
  scope: 'all'
})

const store = useStore()
const route = useRoute()
const qualityFilters = computed(() => store.getters['instance/qualityFilters'])

const artists = ref([])

const logger = useLogger()

const { t } = useI18n()
const labels = computed(() => ({
  title: t('components.library.Home.title')
}))

const isLoading = ref(false)
const fetchData = async () => {
  isLoading.value = true
  const measureLoading = logger.time('Loading latest artists')

  const params = {
    ordering: '-creation_date',
    playable: true
  }

  try {
    const response = await axios.get('artists/', { params })
    artists.value = response.data.results
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
  measureLoading()
}

fetchData()
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
      :h1="t('components.Sidebar.header.explore')"
    />
    <album-widget
      :filters="{scope: scope, playable: true, ordering: '-creation_date', ...qualityFilters}"
      :limit="4"
      :title="t('components.library.Home.header.recentlyAdded')"
    />
    <Spacer />
    <track-widget
      :title="t('components.library.Home.header.recentlyListened')"
      :url="'history/listenings/'"
      :filters="{ scope, ordering: '-creation_date', ...qualityFilters }"
      :websocket-handlers="['Listen']"
    />
    <Spacer />
    <playlist-widget
      :url="'playlists/'"
      :filters="{scope: scope, playable: true, ordering: '-modification_date', limit: 4}"
      :title="t('components.library.Home.header.playlists')"
    />
    <Spacer />
    <track-widget
      :title="t('components.library.Home.header.recentlyFavorited')"
      :url="'favorites/tracks/'"
      :filters="{scope: scope, ordering: '-creation_date'}"
    />
    <Spacer />
    <channels-widget
      :limit="4"
      :filters="{ordering: '-creation_date', external: 'false'}"
      :title="t('components.library.Home.header.newChannels')"
      :show-modification-date="true"
    />
    <Spacer />
    <artist-widget
      :limit="4"
      :filters="{playable: true, ordering: '-creation_date', include_channels: true, content_category: 'podcast'}"
      title="Podcasts hosted on Funkwhale"
    />
  </Layout>
</template>
