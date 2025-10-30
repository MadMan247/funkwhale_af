<script setup lang="ts">
import type { Track, Album, Artist, Library, Cover } from '~/types'

import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter, useRoute } from 'vue-router'
import { sum } from 'lodash-es'
import { getDomain } from '~/utils'
import { useStore } from '~/store'

import axios from 'axios'
import useReport from '~/composables/moderation/useReport'
import useLogger from '~/composables/useLogger'
import { useModal } from '~/ui/composables/useModal.ts'

import HumanDuration from '~/components/common/HumanDuration.vue'
import EmbedWizard from '~/components/audio/EmbedWizard.vue'
import Loader from '~/components/ui/Loader.vue'
import Header from '~/components/ui/Header.vue'
import Button from '~/components/ui/Button.vue'
import Link from '~/components/ui/Link.vue'
import OptionsButton from '~/components/ui/button/Options.vue'
import PlayButton from '~/components/audio/PlayButton.vue'
import RadioButton from '~/components/radios/Button.vue'
import Popover from '~/components/ui/Popover.vue'
import PopoverItem from '~/components/ui/popover/PopoverItem.vue'
import Layout from '~/components/ui/Layout.vue'
import Modal from '~/components/ui/Modal.vue'
import Spacer from '~/components/ui/Spacer.vue'
import RenderedDescription from '../common/RenderedDescription.vue'

interface Props {
  id: number | string
}

const props = defineProps<Props>()
const { report, getReportableObjects } = useReport()

const object = ref<Artist | null>(null)
const libraries = ref([] as Library[])
const albums = ref([] as Album[])
const tracks = ref([] as Track[])
const showEmbedModal = ref(false)

const nextAlbumsUrl = ref(null)
const nextTracksUrl = ref(null)
const totalAlbums = ref(0)
const totalTracks = ref(0)

const logger = useLogger()
const store = useStore()
const router = useRouter()
const route = useRoute()

const domain = computed(() => getDomain(object.value?.fid ?? ''))

// TODO: Re-implement `!!object.value?.albums.some(album => album.is_playable)` instead of `true`
const isPlayable = computed(() => true)
const wikipediaUrl = computed(() => `https://en.wikipedia.org/w/index.php?search=${encodeURI(object.value?.name ?? '')}`)
const musicbrainzUrl = computed(() => object.value?.mbid ? `https://musicbrainz.org/artist/${object.value.mbid}` : null)
const discogsUrl = computed(() => `https://discogs.com/search/?type=artist&title=${encodeURI(object.value?.name ?? '')}`)
const publicLibraries = computed(() => libraries.value?.filter(library => library.privacy_level === 'everyone') ?? [])

// TODO: This is cover logic. We use it a lot. Should all go into a single, smart, parametrised function.
// Something like `useCover.ts`!
const cover = computed(() => {
  const artistCover = object.value?.cover

  // const albumCover: Cover | null = object.value?.albums
  //   .find(album => album.cover?.urls.large_square_crop)?.cover

  const trackCover = tracks.value?.find(
    (track: Track) => track.cover
  )?.cover

  const fallback : Cover = {
    uuid: '',
    mimetype: 'jpeg',
    creation_date: '',
    size: 0,
    urls: {
      original: `${import.meta.env.BASE_URL}embed-default-cover.jpeg`,
      small_square_crop: `${import.meta.env.BASE_URL}embed-default-cover.jpeg`,
      medium_square_crop: `${import.meta.env.BASE_URL}embed-default-cover.jpeg`,
      large_square_crop: `${import.meta.env.BASE_URL}embed-default-cover.jpeg`
    }
  }

  return artistCover
  // || albumCover
  || trackCover
  || fallback
})

const { t } = useI18n()
const labels = computed(() => ({
  title: t('components.library.ArtistBase.title')
}))

const isLoading = ref(false)
const fetchData = async () => {
  isLoading.value = true
  logger.debug(`Fetching artist "${props.id}"`)

  const artistsResponse = await axios.get(`artists/${props.id}/`, { params: { refresh: 'true' } })
  if (artistsResponse.data.channel) {
    return router.replace({ name: 'channels.detail', params: { id: artistsResponse.data.channel.uuid } })
  }

  object.value = artistsResponse.data

  const [tracksResponse, albumsResponse] = await Promise.all([
    axios.get('tracks/', { params: { artist: props.id, hidden: '', ordering: '-creation_date' } }),
    axios.get('albums/', { params: { artist: props.id, hidden: '', ordering: '-release_date' } })
  ])

  tracks.value = tracksResponse.data.results
  nextTracksUrl.value = tracksResponse.data.next
  totalTracks.value = tracksResponse.data.count

  nextAlbumsUrl.value = albumsResponse.data.next
  totalAlbums.value = albumsResponse.data.count

  albums.value = albumsResponse.data.results

  isLoading.value = false
}

const totalDuration = computed(() => sum((tracks.value ?? []).map(track => track.uploads[0]?.duration ?? 0)))

watch(() => props.id, fetchData, { immediate: true })

const isOpen = useModal('artist-description').isOpen
</script>

<template>
  <Layout
    stack
    main
  >
    <Loader v-if="isLoading" />
    <Header
      v-if="object && !isLoading"
      v-title="labels.title"
      :h1="object.name"
      page-heading
    >
      <template #image>
        <img
          v-lazy="cover.urls.large_square_crop"
          :alt="object.name"
          class="channel-image"
        >
      </template>
      <Layout
        flex
        class="meta"
        no-gap
      >
        <div
          v-if="albums"
        >
          {{ t('components.library.ArtistBase.meta.tracks', totalTracks) }}
          {{ t('components.library.ArtistBase.meta.albums', totalAlbums) }}
        </div>
        <div v-if="totalDuration > 0">
          <i class="bi bi-dot" />
          <human-duration
            v-if="totalDuration > 0"
            :duration="totalDuration"
          />
        </div>
      </Layout>
      <Layout
        flex
        gap-4
      >
        <RenderedDescription
          v-if="object.description"
          class="description"
          :content="{ ...object.description, text: object.description.text ?? undefined }"
          :truncate-length="100"
        />
        <Spacer grow />
        <Link
          v-if="object.description"
          :to="useModal('artist-description').to"
          style="color: var(--fw-primary); text-decoration: underline;"
          thin-font
          force-underline
        >
          {{ t('components.common.RenderedDescription.button.more') }}
        </Link>
      </Layout>
      <Modal
        v-if="object.description"
        v-model="isOpen"
        :title="object.name"
      >
        <img
          v-if="object.cover"
          v-lazy="object.cover.urls.original"
          :alt="object.name"
          style="object-fit: cover; width: 100%; height: 100%;"
        >
        <sanitized-html
          v-if="object.description"
          :html="object.description.html"
        />
      </Modal>

      <Layout flex>
        <PlayButton
          :is-playable="isPlayable"
          split
          :artist="object"
          low-height
        >
          {{ t('components.library.ArtistBase.button.play') }}
        </PlayButton>
        <radio-button
          type="artist"
          :object-id="object.id"
          low-height
        />
        <Spacer grow />
        <Popover>
          <template #default="{ toggleOpen }">
            <OptionsButton
              default
              raised
              is-square-small
              @click="toggleOpen"
            />
          </template>

          <template #items>
            <PopoverItem
              v-if="object.fid && domain != store.getters['instance/domain']"
              :to="object.fid"
              target="_blank"
              icon="bi-box-arrow-up-right"
            >
              {{ t('components.library.ArtistBase.link.domain', {domain: domain}) }}
            </PopoverItem>

            <PopoverItem
              v-if="publicLibraries.length > 0"
              icon="bi-code-square"
              @click="showEmbedModal = true"
            >
              {{ t('components.library.ArtistBase.button.embed') }}
            </PopoverItem>

            <PopoverItem
              :to="wikipediaUrl"
              target="_blank"
              rel="noreferrer noopener"
              icon="bi-wikipedia"
            >
              {{ t('components.library.ArtistBase.link.wikipedia') }}
            </PopoverItem>

            <PopoverItem
              v-if="musicbrainzUrl"
              :to="musicbrainzUrl"
              target="_blank"
              rel="noreferrer noopener"
              icon="bi-box-arrow-up-right"
            >
              {{ t('components.library.ArtistBase.link.musicbrainz') }}
            </PopoverItem>

            <PopoverItem
              :to="discogsUrl"
              target="_blank"
              rel="noreferrer noopener"
              icon="bi-box-arrow-up-right"
            >
              {{ t('components.library.ArtistBase.link.discogs') }}
            </PopoverItem>

            <PopoverItem
              v-if="object.is_local"
              :to="{name: 'library.artists.edit', params: {id: object.id }}"
              icon="bi-pencil-fill"
            >
              {{ t('components.library.ArtistBase.button.edit') }}
            </PopoverItem>

            <hr v-if="getReportableObjects({artist: object}).length>0">

            <PopoverItem
              v-for="obj in getReportableObjects({artist: object})"
              :key="obj.target.type + obj.target.id"
              icon="bi-share-fill"
              @click="report(obj)"
            >
              {{ obj.label }}
            </PopoverItem>

            <hr v-if="getReportableObjects({artist: object}).length>0">

            <PopoverItem
              v-if="store.state.auth.availablePermissions['library']"
              :to="{name: 'manage.library.artists.detail', params: {id: object.id}}"
              icon="bi-wrench"
            >
              {{ t('components.library.ArtistBase.link.moderation') }}
            </PopoverItem>

            <PopoverItem
              v-if="store.state.auth.profile && store.state.auth.profile.is_superuser"
              :to="store.getters['instance/absoluteUrl'](`/api/admin/music/artist/${object.id}`)"
              target="_blank"
              rel="noopener noreferrer"
              icon="bi-wrench"
            >
              {{ t('components.library.ArtistBase.link.django') }}
            </PopoverItem>
          </template>
        </Popover>
      </Layout>

      <Modal
        v-if="publicLibraries.length > 0"
        v-model="showEmbedModal"
        :title="t('components.library.ArtistBase.modal.embed.header')"
      >
        <embed-wizard
          :id="object.id"
          type="artist"
        />
        <template #actions>
          <Button secondary>
            {{ t('components.library.ArtistBase.button.cancel') }}
          </Button>
        </template>
      </Modal>
    </Header>
    <router-view
      :key="route.fullPath"
      :tracks="tracks"
      :next-tracks-url="nextTracksUrl"
      :next-albums-url="nextAlbumsUrl"
      :albums="albums"
      :is-loading-albums="isLoading"
      :object="object"
      object-type="artist"
      @libraries-loaded="libraries = $event"
    />
    <Spacer grow />
  </Layout>
</template>

<style scoped lang="scss">
@use '~/style/funkwhale.scss';

  .channel-image {
    border-radius: 50%;
  }

  .meta {
    font-size: 15px;
    @include funkwhale.light-theme {
      color: var(--fw-gray-700);
    }
    @include funkwhale.dark-theme {
      color: var(--fw-gray-500);
    }
  }

  .description {
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    white-space: normal;
    -webkit-line-clamp: 1; /* Number of lines to show */
    line-clamp: 1;
  }
</style>
