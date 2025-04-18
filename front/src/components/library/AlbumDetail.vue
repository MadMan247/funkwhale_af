<script setup lang="ts">
import type { ArtistCredit, Album, Library, Track } from '~/types'

import LibraryWidget from '~/components/federation/LibraryWidget.vue'
import ChannelEntries from '~/components/audio/ChannelEntries.vue'
import TrackTable from '~/components/audio/track/Table.vue'
import PlayButton from '~/components/audio/PlayButton.vue'
import TagsList from '~/components/tags/List.vue'
import Pagination from '~/components/vui/Pagination.vue'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import Loader from '~/components/ui/Loader.vue'
import Spacer from '~/components/ui/Spacer.vue'

interface Events {
  (e: 'libraries-loaded', libraries: Library[]): void
}

interface Props {
  object: Album

  isLoadingTracks: boolean
  isSerie: boolean
  artistCredit: ArtistCredit[]
  paginateBy: number
  totalTracks: number
}

const emit = defineEmits<Events>()
const props = defineProps<Props>()
const { t } = useI18n()

const getDiscKey = (disc: Track[]) => disc?.map(track => track.id).join('|') ?? ''
const page = ref(1)

const discCount = computed(() => props.object?.tracks?.reduce((acc, track) => {
  acc.add(track.disc_number)
  return acc
}, new Set()).size)

const discs = computed(() => props.object?.tracks?.reduce((acc: Track[][], track: Track) => {
  const discNumber = track.disc_number - (props.object?.tracks?.[0]?.disc_number ?? 1)
  acc[discNumber].push(track)
  return acc
}, Array(discCount.value).fill(undefined).map(() => [])))

const paginatedDiscs = computed(() => props.object?.tracks?.slice(props.paginateBy * (page.value - 1), props.paginateBy * page.value)
  .reduce((acc: Track[][], track: Track) => {
    const discNumber = track.disc_number - (props.object?.tracks?.[0]?.disc_number ?? 1)
    acc[discNumber].push(track)
    return acc
  }, Array(discCount.value).fill(undefined).map(() => []))
)

</script>

<template>
  <div
    v-if="!isLoadingTracks"
  >
    <h2 class="ui header">
      <span v-if="isSerie">
        {{ t('components.library.AlbumDetail.header.episodes') }}
      </span>
      <span v-else>
        {{ t('components.library.AlbumDetail.header.tracks') }}
      </span>
    </h2>

    <channel-entries
      v-if="artistCredit && artistCredit[0].artist.channel && isSerie"
      :default-cover="null"
      :is-podcast="isSerie"
      :limit="50"
      :filters="{channel: artistCredit[0].artist.channel, album: object.id, ordering: '-creation_date'}"
    />

    <Loader v-if="isLoadingTracks" />

    <template v-else>
      <TagsList
        v-if="object.tags && object.tags.length > 0"
        style="margin-top: -16px;"
        :tags="object.tags"
      />
      <template v-if="(discCount || 0) > 1">
        <div
          v-for="tracks, index in paginatedDiscs"
          :key="index + getDiscKey(tracks)"
        >
          <template v-if="tracks.length > 0">
            <div class="ui hidden divider" />
            <PlayButton
              class="right floated mini inverted vibrant"
              :tracks="discs ? discs[index] : []"
            />
            <h3>
              {{ t('components.library.AlbumDetail.meta.volume', { number: tracks[0].disc_number }) }}
            </h3>
            <track-table
              :is-album="true"
              :tracks="tracks"
              :show-position="true"
              :show-art="false"
              :show-album="false"
              :show-artist="false"
              :paginate-results="false"
            />
          </template>
        </div>
      </template>
      <template v-else-if="object.tracks">
        <track-table
          :is-album="true"
          :tracks="object.tracks"
          :show-position="true"
          :show-art="false"
          :show-album="false"
          :show-artist="false"
          :paginate-results="false"
        />
      </template>

      <div
        v-if="totalTracks > paginateBy"
        class="ui center aligned basic segment"
      >
        <pagination
          v-model:current="page"
          :paginate-by="paginateBy"
          :total="totalTracks"
        />
      </div>
    </template>

    <template v-if="artistCredit && !artistCredit[0]?.artist.channel && !isSerie">
      <Spacer />
      <library-widget
        :url="'albums/' + object.id + '/libraries/'"
        :title="t('components.library.AlbumDetail.header.libraries')"
        @loaded="emit('libraries-loaded', $event)"
      >
        {{ t('components.library.AlbumDetail.description.libraries') }}
      </library-widget>
    </template>
  </div>
</template>
