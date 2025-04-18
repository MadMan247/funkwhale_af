<script setup lang="ts">
import type { Artist } from '~/types'

import { computed } from 'vue'
import { useStore } from '~/store'
import { truncate } from '~/utils/filters'
import { useI18n } from 'vue-i18n'

import PlayButton from '~/components/audio/PlayButton.vue'
import TagsList from '~/components/tags/List.vue'

interface Props {
  artist: Artist
}

const { t } = useI18n()

const props = defineProps<Props>()

const cover = computed(() => !props.artist.cover?.urls.original
  ? undefined // TODO: Also check Albums. Like in props.artist.albums.find(album => !!album.cover?.urls.original)?.cover
  : props.artist.cover
)

const store = useStore()
const imageUrl = computed(() => cover.value?.urls.original
  ? store.getters['instance/absoluteUrl'](cover.value.urls.medium_square_crop)
  : null
)
</script>

<template>
  <div class="app-card card">
    <router-link
      class="discrete link"
      :to="{name: 'library.artists.detail', params: {id: artist.id}}"
    >
      <div
        v-lazy:background-image="imageUrl"
        :class="['ui', 'head-image', 'circular', 'image', {'default-cover': !cover || !cover.urls.original}]"
      >
        <play-button
          :icon-only="true"
          :is-playable="true /* TODO: check if artist.is_playable exists instead */"
          :button-classes="['ui', 'circular', 'large', 'vibrant', 'icon', 'button']"
          :artist="artist"
        />
      </div>
    </router-link>
    <div class="content">
      <strong>
        <router-link
          class="discrete link"
          :to="{name: 'library.artists.detail', params: {id: artist.id}}"
        >
          {{ truncate(artist.name, 30) }}
        </router-link>
      </strong>

      <TagsList
        label-classes="tiny"
        :truncate-size="20"
        :limit="2"
        :show-more="false"
        :tags="artist.tags"
      />
    </div>
    <div class="extra content">
      <span v-if="artist.content_category === 'music'">
        {{ t('components.audio.artist.Card.meta.tracks', (0 /* TODO: check where artist.tracks_count exists */)) }}
      </span>
      <span v-else>
        {{ t('components.audio.artist.Card.meta.episodes', (0 /* TODO: check where artist.tracks_count exists */)) }}
      </span>
      <play-button
        class="right floated basic icon"
        :dropdown-only="true"
        :is-playable="true /* TODO: check if is_playable can be derived from the data */"
        :dropdown-icon-classes="['ellipsis', 'horizontal', 'large really discrete']"
        :artist="artist"
      />
    </div>
  </div>
</template>
