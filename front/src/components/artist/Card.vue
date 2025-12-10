<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { components } from '~/generated/types.ts'

import PlayButton from '~/components/audio/PlayButton.vue'
import Card from '~/components/ui/Card.vue'
import Spacer from '~/components/ui/Spacer.vue'

import type { Artist, Album } from '~/types'

const albums = ref([] as Album[])

interface Props {
  artist: Artist | components['schemas']['ArtistWithAlbums'];
}

const { t } = useI18n()

const props = defineProps<Props>()

const { artist } = props

if ('albums' in artist && Array.isArray(artist.albums)) {
  albums.value = artist.albums
}
// TODO: This is cover logic. We use it a lot. Should all go into a single, smart, parametrised function.
// Something like `useCover.ts`!
const cover = computed(() => {
  const artistCover = artist.cover

  const albumCover = albums.value?.find(
    (album: Album) => album.cover
  )?.cover

  return artistCover
  || albumCover
})
</script>

<template>
  <Card
    :title="artist.name"
    class="artist-card"
    :tags="artist.tags"
    :to="{name: 'library.artists.detail', params: {id: artist.id}}"
    small
  >
    <template #topright>
      <PlayButton
        icon-only
        :is-playable="true"
        :artist="artist"
      />
    </template>

    <template #image>
      <img
        v-if="cover"
        v-lazy="cover.urls.medium_square_crop"
        :alt="artist.name"
        :class="[artist.content_category === 'podcast' ? 'podcast-image' : 'channel-image']"
      >
      <i
        v-else
        class="bi bi-person-circle"
        style="font-size: 167px; margin: 16px;"
      />
    </template>

    <template #footer>
      <span v-if="artist.content_category === 'music' && 'tracks_count' in artist">
        {{ t('components.audio.artist.Card.meta.tracks', artist.tracks_count) }}
      </span>
      <span v-else-if="'tracks_count' in artist">
        {{ t('components.audio.artist.Card.meta.episodes', artist.tracks_count) }}
      </span>
      <i
        v-if="albums"
        class="bi bi-dot"
      />
      <span v-if="albums">
        {{ t('components.audio.artist.Card.meta.albums', albums.length) }}
      </span>
      <Spacer style="flex-grow: 1" />
      <PlayButton
        :dropdown-only="true"
        :is-playable="Boolean(albums.find(album => album.is_playable))"
        :artist="artist"
        discrete
      />
    </template>
  </Card>
</template>

<style lang="scss" scoped>
.channel-image {
  border-radius: 50%;
  width: 168px;
  height: 168px;
  margin: 16px;
}

.podcast-image {
  width: 168px;
  height: 168px;
  margin: 16px;
}

.play-button {
  top: 16px;
  right: 16px;
}
</style>
