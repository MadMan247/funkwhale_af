<script setup lang="ts">
import { computed } from 'vue'
import { useStore } from '~/store'
import { useI18n } from 'vue-i18n'
import { momentFormat } from '~/utils/filters'
import defaultCover from '~/assets/audio/default-cover.png'

import PlayButton from '~/components/audio/PlayButton.vue'
import Card from '~/components/ui/Card.vue'
import Spacer from '~/components/ui/Spacer.vue'

import { type Album } from '~/types'

interface Props {
  serie: Album
}

const { t } = useI18n()

const props = defineProps<Props>()

const { serie } = props

const store = useStore()
const imageUrl = computed(() => serie?.cover?.urls.original
  ? store.getters['instance/absoluteUrl'](serie.cover?.urls.medium_square_crop)
  : defaultCover
)
</script>

<template>
  <Card
    :title="serie?.title"
    :image="imageUrl"
    :tags="serie?.tags"
    :to="{name: 'library.albums.detail', params: {id: serie?.id}}"
    small
  >
    <template #topright>
      <PlayButton
        icon-only
        :is-playable="serie?.is_playable"
        :album="serie"
      />
    </template>

    <template #footer>
      <span v-if="serie?.release_date">
        {{ momentFormat(new Date(serie?.release_date), 'Y') }}
      </span>
      <i class="bi bi-dot" />
      <span>
        {{ t('components.audio.album.Card.meta.tracks', serie?.tracks_count) }}
      </span>
      <Spacer
        h
        grow
      />
      <PlayButton
        :dropdown-only="true"
        discrete
        :is-playable="serie?.is_playable"
        :album="serie"
      />
    </template>
  </Card>
</template>

<style lang="scss" scoped>
.play-button {
  top: 16px;
  right: 16px;
}
</style>
