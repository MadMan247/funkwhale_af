<script setup lang="ts">
import type { Album } from '~/types'

import AlbumCard from '~/components/album/Card.vue'

interface Props {
  album: Album
}

defineProps<Props>()

</script>

<template>
  <AlbumCard :album="album" />
</template>
