<script setup lang="ts">
import type { Artist, Track, Album, Actor } from '~/types'
import type { ContentFilter } from '~/store/moderation'

import { ref, computed, reactive } from 'vue'
import { useStore } from '~/store'
import { useI18n } from 'vue-i18n'

import axios from 'axios'

import LibraryWidget from '~/components/federation/LibraryWidget.vue'
import TrackTable from '~/components/audio/track/Table.vue'
import TagsList from '~/components/tags/List.vue'
import AlbumCard from '~/components/album/Card.vue'
import Layout from '~/components/ui/Layout.vue'
import Heading from '~/components/ui/Heading.vue'
import Loader from '~/components/ui/Loader.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Button from '~/components/ui/Button.vue'
import Alert from '~/components/ui/Alert.vue'

import useErrorHandler from '~/composables/useErrorHandler'

interface Events {
  (e: 'actors-loaded', actors: Actor[]): void
}

interface Props {
  object: Artist
  tracks: Track[]
  albums: Album[]
  isLoadingAlbums: boolean
  nextTracksUrl?: string | null
  nextAlbumsUrl?: string | null
}

const { t } = useI18n()

const emit = defineEmits<Events>()
const props = withDefaults(defineProps<Props>(), {
  nextTracksUrl: null,
  nextAlbumsUrl: null
})

const store = useStore()

const additionalAlbums = reactive([] as Album[])
const contentFilter = computed(() => store.getters['moderation/artistFilters']().find((filter: ContentFilter) => filter.target.id === props.object.id))
const allAlbums = computed(() => [...props.albums, ...additionalAlbums])

const isLoadingMoreAlbums = ref(false)
const loadMoreAlbumsUrl = ref(props.nextAlbumsUrl)
const loadMoreAlbums = async () => {
  if (loadMoreAlbumsUrl.value === null) return
  isLoadingMoreAlbums.value = true

  try {
    const response = await axios.get(loadMoreAlbumsUrl.value)
    additionalAlbums.push(...additionalAlbums.concat(response.data.results))
    loadMoreAlbumsUrl.value = response.data.next
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoadingMoreAlbums.value = false
}
</script>

<template>
  <Layout
    v-if="object"
    stack
  >
    <TagsList
      v-if="object.tags && object.tags.length > 0"
      style="margin-top: -16px;"
      :tags="object.tags"
    />
    <Alert
      v-if="contentFilter"
      blue
    >
      <p>
        {{ t('components.library.ArtistDetail.message.filter') }}
      </p>
      <template #actions>
        <Button
          blue
          raised
          small
          :to="{name: 'settings'}"
        >
          {{ t('components.library.ArtistDetail.link.filter') }}
        </Button>
        <Button
          destructive
          small
          @click="store.dispatch('moderation/deleteContentFilter', contentFilter.uuid)"
        >
          {{ t('components.library.ArtistDetail.button.filter') }}
        </Button>
      </template>
    </Alert>
    <Loader v-if="isLoadingAlbums" />
    <template v-else-if="albums && albums.length > 0">
      <Heading
        :h2="t('components.library.ArtistDetail.header.album')"
        section-heading
      />
      <Layout flex>
        <album-card
          v-for="album in allAlbums"
          :key="album.id"
          :album="album"
        />
        <Spacer
          h
          grow
        />
        <Button
          v-if="loadMoreAlbumsUrl !== null"
          primary
          :is-loading="isLoadingMoreAlbums"
          @click="loadMoreAlbums()"
        >
          {{ t('components.library.ArtistDetail.button.more') }}
        </Button>
      </Layout>
    </template>
    <template v-if="tracks.length > 0">
      <Heading
        :h2="t('components.library.ArtistDetail.header.track')"
        section-heading
      />
      <TrackTable
        :is-artist="true"
        :show-position="false"
        :track-only="true"
        :tracks="tracks.slice(0,5)"
      />
    </template>
    <Heading
      :h2="t('components.library.ArtistDetail.header.library')"
      section-heading
    />
    <LibraryWidget
      :url="'artists/' + object.id + '/actors/'"
      @loaded="emit('actors-loaded', $event)"
    >
      {{ t('components.library.ArtistDetail.description.library') }}
    </LibraryWidget>
  </Layout>
</template>
