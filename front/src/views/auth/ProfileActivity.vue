<script setup lang="ts">
import type { Actor } from '~/types'

import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'

import PlaylistWidget from '~/components/playlists/Widget.vue'
import TrackWidget from '~/components/audio/track/Widget.vue'
import AlbumWidget from '~/components/album/Widget.vue'
import RadioButton from '~/components/radios/Button.vue'
import Layout from '~/components/ui/Layout.vue'
import Spacer from '~/components/ui/Spacer.vue'
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
    stack
  >
    <Header
      :h1="t('views.auth.ProfileBase.link.overview')"
      page-heading
    >
      <template #action>
        <radio-button
          v-if="recentActivity > 0 && typeof object?.preferred_username === 'string' && typeof object?.full_username === 'string'"
          class="right floated"
          type="account"
          :object-id="{ username: object?.preferred_username, fullUsername: object?.full_username }"
          :client-only="true"
        />
      </template>
    </Header>

    <track-widget
      :url="'history/listenings/'"
      :filters="{ scope: scope, ordering: '-creation_date', playable: true, ...qualityFilters}"
      :websocket-handlers="['Listen']"
      :title="t('components.library.Home.header.recentlyListened')"
      @count="recentActivity = $event"
    />
    <Spacer :size="64" />
    <track-widget
      :url="'favorites/tracks/'"
      :filters="{ scope:scope, playable: true, ordering: '-creation_date'}"
      :title="t('components.library.Home.header.recentlyFavorited')"
    />
    <Spacer />
    <playlist-widget
      :url="'playlists/'"
      :filters="{ scope:scope, playable: true, ordering: '-modification_date'}"
      :title="t('views.auth.ProfileActivity.header.playlists')"
    />
    <Spacer />
    <album-widget
      :filters="{ scope:scope, playable: true, ordering: '-creation_date', ...qualityFilters}"
      :title="t('components.library.Home.header.recentlyAdded')"
    />
  </Layout>
</template>
