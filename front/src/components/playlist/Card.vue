<script setup lang="ts">
import Card from '~/components/ui/Card.vue'
import PlayButton from '~/components/audio/PlayButton.vue'
import OptionsButton from '~/components/ui/button/Options.vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { computed } from 'vue'

import type { Playlist } from '~/types'

const { t } = useI18n()

// TODO: Check if the following emit is ever caught anywhere
// const play = defineEmit<[playlist: Playlist]>()

const { playlist } = defineProps<{playlist: Playlist}>()

const covers = computed(() => playlist.album_covers
  .filter((src, index, array) => array.indexOf(src) === index)
  .slice(0, 4)
)

const profileParams = computed(() => {
  const [username, domain] = playlist.actor.full_username.split('@')
  return { username, domain }
})

let navigate = (to: 'playlist' | 'user') => {}

if (import.meta.env.PROD) {
  const router = useRouter()
  navigate = (to: 'playlist' | 'user') => to === 'playlist'
    ? router.push({ name: 'library.playlists.detail', params: { id: playlist.uuid } })
    : router.push({ name: 'profile.full', params: profileParams.value })
}
</script>

<template>
  <Card
    :title="playlist.name"
    class="playlist-card"
    @click="navigate('playlist')"
  >
    <template #image>
      <img
        v-for="src in covers"
        :key="src"
        :src="src"
      >
      <div
        v-for="i in Math.max(0, 4 - covers.length)"
        :key="i"
      />
    </template>

    <PlayButton
      :icon-only="true"
      :is-playable="playlist.is_playable"
      :playlist="playlist"
    />

    <a
      class="funkwhale link"
      @click.stop="navigate('user')"
    >
      {{ t('vui.by-user', playlist.actor.full_username) }}
    </a>

    <template #footer>
      {{ t('vui.tracks', playlist.tracks_count) }}
      <OptionsButton />
    </template>
  </Card>
</template>

<style lang="scss">
@import './style.scss'
</style>
