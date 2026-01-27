<script setup lang="ts">
import type { Track, Library } from '~/types'
import type { operations, components } from '~/generated/types'

import { momentFormat } from '~/utils/filters'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter, useRoute } from 'vue-router'
import { getDomain } from '~/utils'
import { useStore } from '~/store'

import axios from 'axios'

import ActorLink from '~/components/common/ActorLink.vue'
import ArtistCreditLabel from '~/components/audio/ArtistCreditLabel.vue'
import TrackFavoriteIcon from '~/components/favorites/TrackFavoriteIcon.vue'
import TrackPlaylistIcon from '~/components/playlists/TrackPlaylistIcon.vue'
import EmbedWizard from '~/components/audio/EmbedWizard.vue'
import HumanDuration from '~/components/common/HumanDuration.vue'
import Layout from '~/components/ui/Layout.vue'
import Header from '~/components/ui/Header.vue'
import Loader from '~/components/ui/Loader.vue'
import Modal from '~/components/ui/Modal.vue'
import PlayButton from '~/components/audio/PlayButton.vue'
import Button from '~/components/ui/Button.vue'
import OptionsButton from '~/components/ui/button/Options.vue'
import Popover from '~/components/ui/Popover.vue'
import PopoverItem from '~/components/ui/popover/PopoverItem.vue'
import Alert from '~/components/ui/Alert.vue'
import Spacer from '~/components/ui/Spacer.vue'

import updateQueryString from '~/composables/updateQueryString'
import useErrorHandler from '~/composables/useErrorHandler'
import useReport from '~/composables/moderation/useReport'
import useLogger from '~/composables/useLogger'

interface Events {
  (e: 'deleted'): void
}

interface Props {
  id: number
}

const emit = defineEmits<Events>()
const props = defineProps<Props>()

const { report, getReportableObjects } = useReport()

const track = ref<Track | null>(null)
const artist = ref<components['schemas']['ArtistWithAlbums'] | null>(null)
const showEmbedModal = ref(false)
const showDeleteModal = ref(false)
const libraries = ref([] as Library[])

const logger = useLogger()
const router = useRouter()
const route = useRoute()
const store = useStore()

const domain = computed(() => getDomain(track.value?.fid ?? ''))

// TODO: Why is nobody using the public libraries?
// const publicLibraries = computed(() => libraries.value?.filter(library => library.privacy_level === 'everyone') ?? [])

// TODO: Make it make sense:
// const isEmbedable = computed(() => artist.value?.channel?.actor || publicLibraries.value.length)

const isEmbedable = computed(() => false)

const upload = computed(() => track.value?.uploads?.[0] ?? null)
const wikipediaUrl = computed(() => `https://en.wikipedia.org/w/index.php?search=${encodeURI(`${track.value?.title ?? ''} ${track.value?.artist_credit[0]?.artist.name ?? ''}`)}`)
const discogsUrl = computed(() => `https://discogs.com/search/?type=release&title=${encodeURI(track.value?.album?.title ?? '')}&artist=${encodeURI(track.value?.artist_credit[0]?.artist.name ?? '')}&title=${encodeURI(track.value?.title ?? '')}`)
const downloadUrl = computed(() => {
  const url = store.getters['instance/absoluteUrl'](upload.value?.listen_url ?? '')
  return store.state.auth.authenticated
    ? updateQueryString(url, 'token', encodeURI(store.state.auth.scopedTokens.listen ?? ''))
    : url
})

// TODO: Still needed?:

// const attributedToUrl = computed(() => router.resolve({
//   name: 'profile.full.content',
//   params: {
//     username: track.value?.attributed_to?.preferred_username,
//     domain: track.value?.attributed_to?.domain
//   }
// })?.href)

// const artistCredit = track.value?.artist_credit

const totalDuration = computed(() => track.value?.uploads?.[0]?.duration ?? 0)

const { t } = useI18n()
const labels = computed(() => ({
  title: t('components.library.TrackBase.title'),
  download: t('components.library.TrackBase.button.download'),
  more: t('components.library.TrackBase.button.more')
}))

// Note: Mind the singular!

type TrackResponse = operations['get_track']['responses']['200']['content']['application/json']
type ArtistResponse = operations['get_artist']['responses']['200']['content']['application/json']

/* Too bad the following is just wrong now:
const params: TrackParams = {
  refresh: 'true'
  // TypeScript will now show all available parameters with their types
}
  */

const isLoading = ref(false)
const fetchData = async () => {
  isLoading.value = true
  logger.debug(`Fetching track "${props.id}"`)
  try {
    const trackResponse = await axios.get<TrackResponse>(`tracks/${props.id}/`, { params: { refresh: 'true' } })
    track.value = trackResponse.data
    const artistResponse = await axios.get<ArtistResponse>(
      `artists/${trackResponse.data.artist_credit[0]?.artist.id}/`
    )
    artist.value = artistResponse.data
  } catch (error) {
    useErrorHandler(error as Error)
  }
  isLoading.value = false
}

watch(() => props.id, fetchData, { immediate: true })

const remove = async () => {
  isLoading.value = true
  try {
    await axios.delete(`tracks/${track.value?.id}`)
    emit('deleted')
    router.push({ name: 'library.artists.detail', params: { id: artist.value?.id } })
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

const open = ref(false)

watch(showDeleteModal, (newValue) => {
  if (newValue) {
    // NOTE: Explicitly close the popover when delete modal opens
    open.value = false
  }
})
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
      v-if="track"
      :h1="track.title"
      :action="{
        text: labels.download,
        // @ts-ignore
        to: downloadUrl,
        // @ts-ignore
        solid: true,
        // @ts-ignore
        primary: true,
        // @ts-ignore
        icon: 'bi-download',
        // @ts-ignore
        lowHeight: true
      }"
      page-heading
    >
      <template #image>
        <img
          v-if="track.cover"
          v-lazy="store.getters['instance/absoluteUrl'](track.cover.urls.large_square_crop)"
          alt=""
          class="channel-image"
        >
        <img
          v-if="track.album && track.album.cover"
          v-lazy="store.getters['instance/absoluteUrl'](track.album.cover.urls.large_square_crop)"
          alt=""
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
        :artist-credit="track.artist_credit"
      />
      <div class="meta">
        <span>{{ t('components.library.TrackBase.title') }}</span>
        <i class="bi bi-dot" />
        <span>{{ track.album?.title }}</span>
        <i
          v-if="totalDuration > 0"
          class="bi bi-dot"
        />
        <human-duration
          v-if="totalDuration > 0"
          :duration="totalDuration"
        />
      </div>

      <Layout flex>
        <PlayButton
          :is-playable="track.is_playable"
          class="vibrant"
          split
          :track="track"
          low-height
        />

        <Spacer
          h
          grow
        />

        <TrackFavoriteIcon
          v-if="store.state.auth.authenticated"
          :track="track"
          square-small
          raised
        />
        <TrackPlaylistIcon
          v-if="store.state.auth.authenticated"
          :track="track"
          square-small
          raised
        />
        <Popover v-model="open">
          <template #default="{ toggleOpen }">
            <OptionsButton
              is-square-small
              raised
              @click="toggleOpen"
            />
          </template>
          <template #items>
            <PopoverItem
              v-if="domain != store.getters['instance/domain']"
              :to="track.fid"
              target="_blank"
              icon="bi-box-arrow-up-right"
            >
              {{ t('components.library.TrackBase.link.domain', { domain }) }}
            </PopoverItem>

            <PopoverItem
              v-if="isEmbedable"
              icon="bi-code-slash"
              @click="showEmbedModal = !showEmbedModal"
            >
              {{ t('components.library.TrackBase.button.embed') }}
            </PopoverItem>

            <PopoverItem
              :to="wikipediaUrl"
              target="_blank"
              rel="noreferrer noopener"
              icon="bi-wikipedia"
            >
              {{ t('components.library.TrackBase.link.wikipedia') }}
            </PopoverItem>

            <PopoverItem
              v-if="discogsUrl"
              :to="discogsUrl"
              target="_blank"
              rel="noreferrer noopener"
              icon="bi-box-arrow-up-right"
            >
              {{ t('components.library.TrackBase.link.discogs') }}
            </PopoverItem>

            <PopoverItem
              v-if="track.is_local"
              icon="bi-pencil-fill"
              :to="{ name: 'library.tracks.edit', params: { id: track.id } }"
            >
              {{ t('components.library.TrackBase.button.edit') }}
            </PopoverItem>

            <PopoverItem
              v-if="
                store.state.auth.authenticated &&
                  track.attributed_to?.full_username === store.state.auth.fullUsername"
              icon="bi-trash"
              destructive
              @click="showDeleteModal = true"
            >
              {{ t('components.library.TrackBase.button.delete') }}
            </PopoverItem>

            <hr>

            <PopoverItem
              v-for="obj in getReportableObjects({ track })"
              :key="obj.target.type + obj.target.id"
              icon="bi-flag"
              @click="report(obj)"
            >
              {{ obj.label }}
            </PopoverItem>

            <hr>

            <PopoverItem
              v-if="store.state.auth.availablePermissions['library']"
              :to="{
                name: 'manage.library.tracks.detail',
                params: { id: track.id }
              }"
              icon="bi-wrench"
            >
              {{ t('components.library.TrackBase.link.moderation') }}
            </PopoverItem>

            <PopoverItem
              v-if="store.state.auth.profile?.is_superuser"
              :to="store.getters['instance/absoluteUrl'](`/api/admin/music/track/${track.id}`)"
              target="_blank"
              rel="noopener noreferrer"
              icon="bi-wrench"
            >
              {{ t('components.library.TrackBase.link.django') }}
            </PopoverItem>
          </template>
        </Popover>
      </Layout>
    </Header>
    <hr>
    <Layout
      flex
      gap-8
    >
      <span v-if="track?.attributed_to">
        {{ t('components.library.TrackBase.subtitle.with-uploader') }}
      </span>
      <span v-else>
        {{ t('components.library.TrackBase.subtitle.without-uploader') }}
      </span>
      <ActorLink
        v-if="track?.attributed_to"
        :actor="track?.attributed_to"
        :avatar="false"
      />
      <time
        :title="track?.creation_date"
        :datetime="track?.creation_date"
      >
        {{ track?.creation_date ? momentFormat(new Date(track.creation_date), 'LL') : '' }}
      </time>
    </Layout>
    <Spacer :size="64" />

    <Modal
      v-if="isEmbedable"
      v-model="showEmbedModal"
      :title="t('components.library.TrackBase.modal.embed.header')"
    >
      <embed-wizard
        :id="track?.id ?? 0"
        type="track"
      />

      <template #actions>
        <Button
          secondary
          @click="showEmbedModal = false"
        >
          {{ t('components.library.TrackBase.button.cancel') }}
        </Button>
      </template>
    </Modal>
    <Modal
      v-model="showDeleteModal"
      :title="t('components.library.TrackBase.modal.delete.header')"
      is-destructive
    >
      <template #alert>
        <Alert red>
          {{ t('components.library.TrackBase.modal.delete.content.warning') }}
        </Alert>
      </template>

      <template #actions>
        <Button
          secondary
          @click="showDeleteModal = false"
        >
          {{ t('components.library.TrackBase.button.cancel') }}
        </Button>
        <Button
          destructive
          :is-loading="isLoading"
          @click="remove()"
        >
          {{ t('components.library.TrackBase.button.delete') }}
        </Button>
      </template>
    </Modal>
    <router-view
      v-if="track"
      :key="route.fullPath"
      :track="track"
      :object="track"
      object-type="track"
      @libraries-loaded="libraries = $event"
    />
  </Layout>
</template>

<style lang="scss" scoped>
@use '~/style/funkwhale.scss';

.meta {
  font-size: 15px;
  line-height: 32px;
  @include funkwhale.light-theme {
    color: var(--fw-gray-700);
  }
  @include funkwhale.dark-theme {
    color: var(--fw-gray-500);
  }
}
</style>
