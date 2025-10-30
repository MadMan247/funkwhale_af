<script setup lang="ts">
import type { Track, Library } from '~/types'

import { momentFormat } from '~/utils/filters'
import { computed, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter, useRoute } from 'vue-router'
import { sum } from 'lodash-es'
import { useStore } from '~/store'
import { useDataStore } from '~/ui/stores/data'
import { useQueue } from '~/composables/audio/queue'

import axios from 'axios'

import ArtistCreditLabel from '~/components/audio/ArtistCreditLabel.vue'
import TrackFavoriteIcon from '~/components/favorites/TrackFavoriteIcon.vue'
import TrackPlaylistIcon from '~/components/playlists/TrackPlaylistIcon.vue'
import PlayButton from '~/components/audio/PlayButton.vue'
import AlbumDropdown from './AlbumDropdown.vue'
import Layout from '~/components/ui/Layout.vue'
import Header from '~/components/ui/Header.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Loader from '~/components/ui/Loader.vue'
import Button from '~/components/ui/Button.vue'
import HumanDuration from '~/components/common/HumanDuration.vue'

import useErrorHandler from '~/composables/useErrorHandler'
import useLogger from '~/composables/useLogger'

interface Events {
  (e: 'deleted'): void
}

interface Props {
  id: number | string
}

const store = useStore()
const dataStore = useDataStore()

const emit = defineEmits<Events>()
const props = defineProps<Props>()

const object = computed(() => dataStore.get("album", props.id).value)
const artistCredit = computed(() => object.value?.artist_credit ?? [])


const libraries = ref([] as Library[])
const paginateBy = ref(50)

const totalTracks = computed(() => object.value?.tracks_count ?? 0)
const isChannel = computed(() => {
  return artistCredit.value.some(ac => ac.artist.channel)
})
const isAlbum = computed(() => {
  return artistCredit.value.some(ac => ac.artist.content_category === 'music')
})
const isSerie = computed(() => {
  return artistCredit.value.some(ac => ac.artist.content_category === 'podcast')
})

const totalDuration = computed(() => sum((object.value?.tracks ?? []).map(track => track.uploads[0]?.duration ?? 0)))
const publicLibraries = computed(() => libraries.value?.filter(library => library.privacy_level === 'everyone') ?? [])

const logger = useLogger()

const { t } = useI18n()

const labels = computed(() => ({
  title: t('components.library.AlbumBase.title'),
  shuffle: t('components.audio.Player.label.shuffleQueue')
}))

const {
  shuffle
} = useQueue()

const isLoading = ref(false)
const fetchData = async () => {
  isLoading.value = true
  if (!object.value)
    return
  else
    object.value.tracks = []

  fetchTracks()
  isLoading.value = false
}

const tracks = reactive([] as Track[])
watch(tracks, (tracks) => {
  if (object.value) {
    object.value.tracks = tracks
  }
})

const isLoadingTracks = ref(false)
const fetchTracks = async () => {
  if (isLoadingTracks.value) return
  isLoadingTracks.value = true
  tracks.length = 0
  let url = 'tracks/'
  try {
    while (url) {
      const response = await axios.get(url, {
        params: {
          ordering: 'disc_number,position',
          album: props.id,
          page_size: paginateBy.value,
          include_channels: true
        }
      })

      url = response.data.next
      tracks.push(...response.data.results)
    }
  } catch (error) {
    logger.error(error)
  } finally {
    isLoadingTracks.value = false
  }
}

watch(() => [props.id, object.value], fetchData, { immediate: true })

const router = useRouter()
const route = useRoute()

const remove = async () => {
  isLoading.value = true
  try {
    await axios.delete(`albums/${object.value?.id}`)
    emit('deleted')
    if (artistCredit.value)
      router.push({ name: 'library.artists.detail', params: { id: artistCredit.value[0]?.artist.id } })
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}
</script>

<template>
  <Layout
    main
    stack
  >
    <Loader
      v-if="isLoading"
      v-title="labels.title"
    />
    <Header
      v-if="object"
      :key="object.title /*Re-render component when title changes after an update*/"
      :h1="object.title"
      page-heading
    >
      <template #image>
        <img
          v-if="object.cover && object.cover.urls.original"
          v-lazy="store.getters['instance/absoluteUrl'](object.cover.urls.large_square_crop)"
          :alt="object.title"
          class="channel-image"
        >
        <img
          v-else
          alt=""
          class="channel-image"
          src="../../assets/audio/default-cover.png"
        >
      </template>
      <artist-credit-label
        v-if="artistCredit"
        :artist-credit="artistCredit"
      />
      <!-- Metadata: -->
      <Layout
        flex
        gap-4
        style="line-height: 32px; opacity: .6; font-size: 15px;/* TODO: find more consistent way to express this with layout primitives *?"
      >
        <template v-if="object.release_date">
          {{ momentFormat(new Date(object.release_date ?? '1970-01-01'), 'Y') }}
          <i class="bi bi-dot" />
        </template>
        <template v-if="totalTracks > 0">
          <span v-if="isSerie">
            {{ t('components.library.AlbumBase.meta.episodes', totalTracks) }}
          </span>
          <span v-else>
            {{ t('components.library.AlbumBase.meta.tracks', totalTracks) }}
          </span>
        </template>
        <i
          v-if="totalDuration > 0"
          class="bi bi-dot"
        />
        <human-duration
          v-if="totalDuration > 0"
          :duration="totalDuration"
        />
        <!--TODO: License -->
      </Layout>
      <RenderedDescription
        v-if="object.description"
        :content="{ html: object.description.html }"
        :truncate-length="50"
      />
      <Layout flex>
        <PlayButton
          v-if="object.tracks"
          split
          :tracks="object.tracks"
          low-height
          :is-playable="object.is_playable"
        />
        <Button
          v-if="object?.tracks?.length && object?.tracks?.length > 2"
          primary
          icon="bi-shuffle"
          low-height
          :aria-label="labels.shuffle"
          @click.prevent.stop="shuffle()"
        >
          {{ labels.shuffle }}
        </Button>
        <DangerousButton
          v-if="artistCredit[0] &&
            store.state.auth.authenticated &&
            artistCredit[0].artist.channel
          /* TODO: Re-implement once attributed_to is not only a number
              && artistCredit[0].artist.attributed_to?.full_username === store.state.auth.fullUsername
          */"
          :is-loading="isLoading"
          low-height
          icon="bi-trash"
          @confirm="remove()"
        >
          {{ t('components.library.AlbumDropdown.button.delete') }}
        </DangerousButton>
        <Spacer
          h
          grow
        />
        <TrackFavoriteIcon
          v-if="store.state.auth.authenticated"
          default
          raised
          square-small
          :album="object"
        />
        <TrackPlaylistIcon
          v-if="store.state.auth.authenticated"
          default
          raised
          square-small
          :album="object"
        />
        <!-- TODO: Share Button -->
        <album-dropdown
          default
          raised
          :object="object"
          :public-libraries="publicLibraries"
          :is-loading="isLoading"
          :is-album="isAlbum"
          :is-serie="isSerie"
          :is-channel="isChannel"
          :artist-credit="artistCredit"
          @remove="remove"
        />
      </Layout>
    </Header>

    <router-view
      v-if="object"
      :key="route.fullPath"
      :paginate-by="paginateBy"
      :total-tracks="totalTracks"
      :is-serie="isSerie"
      :artist-credit="artistCredit"
      :object="object"
      :is-loading-tracks="isLoadingTracks"
      object-type="album"
      @libraries-loaded="libraries = $event"
    />
    <Spacer grow />
  </Layout>
</template>

<style scoped lang="scss">
@use '~/style/funkwhale.scss';

.meta {
  font-size: 15px;

  @include funkwhale.light-theme {
    color: var(--fw-gray-700);
  }

  @include funkwhale.dark-theme {
    color: var(--fw-gray-500);
  }
}
</style>
