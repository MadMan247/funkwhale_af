<script setup lang="ts">
import type { Playlist } from '~/types'

import PlaylistsCard from '~/components/playlists/Card.vue'

interface Props {
  playlists: Playlist[]
}

defineProps<Props>()
</script>

<template>
  <!-- TODO: Remove this module -->
  <PlaylistsCard
    v-for="playlist in playlists"
    :key="playlist.id"
    :playlist="playlist"
  />
</template>
