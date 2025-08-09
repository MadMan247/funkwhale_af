<script setup lang="ts">
import { computed } from 'vue'
import { useStore } from '~/store'
import { useI18n } from 'vue-i18n'
import { momentFormat } from '~/utils/filters'
import defaultCover from '~/assets/audio/default-cover.png'

import PlayButton from '~/components/audio/PlayButton.vue'
import Layout from '~/components/ui/Layout.vue'
import Card from '~/components/ui/Card.vue'
import Link from '~/components/ui/Link.vue'
import Spacer from '~/components/ui/Spacer.vue'

import { type Album } from '~/types'

interface Props {
  album: Album;
}

const { t } = useI18n()

const props = defineProps<Props>()

const { album } = props

const artistCredit = album.artist_credit || []

const store = useStore()
const imageUrl = computed(() => props.album.cover?.urls.original
  ? store.getters['instance/absoluteUrl'](props.album.cover?.urls.medium_square_crop)
  : defaultCover
)
</script>

<template>
  <Card
    :title="album.title"
    :image="imageUrl"
    :tags="album.tags"
    :to="{ name: 'library.albums.detail', params: { id: album.id } }"
    small
  >
    <template #topright>
      <PlayButton
        icon-only
        :is-playable="album.is_playable"
        :album="album"
      />
    </template>
    <Layout
      flex
      gap-4
      style="overflow: hidden;"
    >
      <template
        v-for="ac in artistCredit"
        :key="ac.artist.id"
      >
        <Link
          align-text="start"
          :to="{ name: 'library.artists.detail', params: { id: ac.artist.id } }"
        >
          {{ ac.credit ?? t('components.Queue.meta.unknownArtist') }}
        </Link>
        <span style="font-weight: 600;">{{ ac.joinphrase }}</span>
      </template>
    </Layout>

    <template #footer>
      <span v-if="album.release_date">
        {{ momentFormat(new Date(album.release_date), 'Y') }}
      </span>
      <i class="bi bi-dot" />
      <span>
        {{ t('components.audio.album.Card.meta.tracks', album.tracks_count) }}
      </span>
      <Spacer
        h
        grow
      />
      <PlayButton
        :dropdown-only="true"
        discrete
        :is-playable="album.is_playable"
        :album="album"
      />
    </template>
  </Card>
</template>

<style scoped>
.play-button {
  top: 16px;
  right: 16px;
}
</style>
