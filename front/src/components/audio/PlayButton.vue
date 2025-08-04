<script setup lang="ts">
import type { Track, Artist, Album, Playlist, Library, Channel, Actor } from '~/types'
import type { components } from '~/generated/types'
import type { PlayOptionsProps } from '~/composables/audio/usePlayOptions'

import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import usePlayOptions from '~/composables/audio/usePlayOptions'
import useReport from '~/composables/moderation/useReport'
import { useStore } from '~/store'
import { useRouter, useRoute } from 'vue-router'

import Button from '~/components/ui/Button.vue'
import OptionsButton from '~/components/ui/button/Options.vue'
import Popover from '~/components/ui/Popover.vue'
import PopoverItem from '~/components/ui/popover/PopoverItem.vue'

interface Props extends PlayOptionsProps {
  split?: boolean
  dropdownIconClasses?: string[]
  playIconClass?: string
  buttonClasses?: string[]
  discrete?: true
  dropdownOnly?: boolean
  iconOnly?: boolean
  playing?: boolean
  paused?: boolean
  lowHeight?: boolean

  // TODO(wvffle): Remove after https://github.com/vuejs/core/pull/4512 is merged
  isPlayable?: boolean
  tracks?: Track[]
  track?: Track | null
  artist?: Artist | components["schemas"]["SimpleChannelArtist"] | components['schemas']['ArtistWithAlbums'] | null
  album?: Album | null
  playlist?: Playlist | null
  library?: Library | null
  channel?: Channel | null
  account?: Actor | components['schemas']['APIActor'] | null
}

const props = withDefaults(defineProps<Props>(), {
  split: false,
  tracks: () => [],
  track: null,
  artist: null,
  playlist: null,
  album: null,
  library: null,
  channel: null,
  account: null,
  dropdownIconClasses: () => ['bi-caret-down-fill'],
  playIconClass: () => 'bi-play-fill',
  buttonClasses: () => ['button'],
  dropdownOnly: () => false,
  iconOnly: () => false,
  isPlayable: () => false,
  playing: () => false,
  paused: () => false,
  lowHeight: () => false
})

// (1) Create a PlayButton
//     Some of the props are meant for `usePlayOptions`!
//     UsePlayOptions accepts the props from this component and returns the following things:

const {
  playable,
  filterableArtist,
  filterArtist,
  enqueue,
  enqueueNext,
  replacePlay,
  isLoading,
  requestPlaylistUploadsAccess
} = usePlayOptions(props)

const { report, getReportableObjects } = useReport()

const { t } = useI18n()
const store = useStore()
const router = useRouter()
const route = useRoute()

const labels = computed(() => ({
  playNow: t('components.audio.PlayButton.button.playNow'),
  addToQueue: t('components.audio.PlayButton.button.addToQueue'),
  playNext: t('components.audio.PlayButton.button.playNext'),
  startRadio: t('components.audio.PlayButton.button.startRadio'),
  report: t('components.audio.PlayButton.button.report'),
  addToPlaylist: t('components.audio.PlayButton.button.addToPlaylist'),
  hideArtist: t('components.audio.PlayButton.button.hideArtist'),
  replacePlay: props.track
    ? t('components.audio.PlayButton.button.playTrack')
    : props.album
      ? t('components.audio.PlayButton.button.playAlbum')
      : props.artist
        ? t('components.audio.PlayButton.button.playArtist')
        : props.playlist
          ? t('components.audio.PlayButton.button.playPlaylist')
          : t('components.audio.PlayButton.button.playTracks'),
  PlaylistUploadGranted: t('components.audio.PlayButton.button.PlaylistUploadGranted'),
  PlaylistUploadPending:t('components.audio.PlayButton.button.PlaylistUploadPending'),
  PlaylistUploadNotRequest: t('components.audio.PlayButton.button.PlaylistUploadNotRequest'),
  PlaylistUploadTooltip: t('components.audio.PlayButton.button.PlaylistUploadTooltip')
  }))

const isOpen = ref(false)

const playlistLibraryFollowInfo = computed(() => {
  const playlist = props.playlist;
  if (!playlist) return null;

  const followed = playlist.library_followed;

  if (followed === true) {
    return {
      label: labels.value.PlaylistUploadGranted,
      tooltip: labels.value.PlaylistUploadTooltip,
      icon: 'bi-check-circle',
      disabled: true
    };
  }

  if (followed === false) {
    return {
      label: labels.value.PlaylistUploadPending,
      tooltip: labels.value.PlaylistUploadTooltip,
      icon: 'bi-hourglass-split',
      disabled: true
    };
  }

  // Assume null/undefined means not yet requested
  return {
    label: labels.value.PlaylistUploadNotRequest,
    tooltip: labels.value.PlaylistUploadTooltip,
    icon: 'bi-eye-slash',
    disabled: false,
    action: requestPlaylistUploadsAccess
  }
});


</script>

<template>
  <Popover
    v-if="split || (!iconOnly && dropdownOnly)"
    v-model="isOpen"
  >
    <OptionsButton
      v-if="dropdownOnly"
      v-bind="$attrs"
      :is-ghost="discrete"
      @click="isOpen = !isOpen"
    />
    <Button
      v-else
      v-bind="{
        disabled: !playable && !filterableArtist,
        primary: playable,
        split: true,
        splitIcon: 'bi-caret-down-fill'
      }"
      :aria-label="labels.replacePlay"
      :class="[...buttonClasses, 'play-button']"
      :isloading="isLoading"
      :dropdown-only="dropdownOnly"
      :low-height="lowHeight || undefined"
      style="align-self: start;"
      @click.stop.prevent="replacePlay()"
      @split-click="isOpen = !isOpen"
    >
      <template #main>
        <i
          v-if="playing"
          class="bi bi-pause-fill"
        />
        <i
          v-else
          :class="['bi', playIconClass]"
        />
        <template v-if="!discrete && !iconOnly">
          &nbsp;<slot>{{ t('components.audio.PlayButton.button.discretePlay') }}</slot>
        </template>
      </template>
    </Button>

    <template #items>
      <PopoverItem
        :disabled="!playable"
        :title="labels.addToQueue"
        icon="bi-plus"
        @click.stop.prevent="enqueue"
      >
        {{ labels.addToQueue }}
      </PopoverItem>

      <PopoverItem
        :disabled="!playable"
        :title="labels.playNext"
        icon="bi-skip-forward-fill"
        @click.stop.prevent="enqueueNext()"
      >
        {{ labels.playNext }}
      </PopoverItem>

      <PopoverItem
        :disabled="!playable"
        :title="labels.playNow"
        icon="bi-play-fill"
        @click.stop.prevent="enqueueNext(true)"
      >
        {{ labels.playNow }}
      </PopoverItem>

      <PopoverItem
        v-if="track"
        :disabled="!playable"
        :title="labels.startRadio"
        icon="bi-broadcast"
        @click.stop.prevent="store.dispatch('radios/start', {type: 'similar', objectId: track?.id})"
      >
        {{ labels.startRadio }}
      </PopoverItem>

      <PopoverItem
        v-if="track"
        :disabled="!playable"
        icon="bi-list"
        @click.stop="store.commit('playlists/chooseTrack', track)"
      >
        {{ labels.addToPlaylist }}
      </PopoverItem>
      <PopoverItem
        v-if="track && route.name !== 'library.tracks.detail'"
        icon="bi-info-circle"
        @click.stop.prevent="router.push(`/library/tracks/${track?.id}/`)"
      >
        <span v-if="track.artist_credit?.some(ac => ac.artist.content_category === 'podcast')">
          {{ t('components.audio.PlayButton.button.episodeDetails') }}
        </span>
        <span v-else>
          {{ t('components.audio.PlayButton.button.trackDetails') }}
        </span>
      </PopoverItem>

      <hr v-if="filterableArtist || Object.keys(getReportableObjects({ track, album, artist, playlist, account, channel })).length > 0">

      <PopoverItem
        v-if="filterableArtist && !props.playlist"
        :disabled="!filterableArtist"
        :title="labels.hideArtist"
        icon="bi-eye-slash"
        @click.stop.prevent="filterArtist"
      >
        {{ labels.hideArtist }}
      </PopoverItem>

      <PopoverItem
        v-for="obj in getReportableObjects({ track, album, artist, playlist, account, channel })"
        :key="obj.target.type + obj.target.id"
        icon="bi-exclamation-triangle-fill"
        @click.stop.prevent="report(obj)"
      >
        {{ obj.label }}
      </PopoverItem>
      <PopoverItem
        v-if="playlist && playlistLibraryFollowInfo && store.state.auth.profile && playlist.actor.full_username != store.state.auth.fullUsername"
        :title="playlistLibraryFollowInfo.tooltip"
        :icon="playlistLibraryFollowInfo.icon"
        :disabled="playlistLibraryFollowInfo.disabled"
        @click.stop.prevent="requestPlaylistUploadsAccess(playlist)"
      >
        {{ playlistLibraryFollowInfo.label }}
      </PopoverItem>
    </template>
  </Popover>
  <Button
    v-else
    v-bind="{
      disabled: !playable,
      primary: playable,
    }"
    :aria-label="labels.replacePlay"
    :class="[...buttonClasses, 'play-button']"
    :isloading="isLoading"
    :square="iconOnly"
    :icon="!playing ? playIconClass : 'bi-pause-fill'"
    :round="iconOnly"
    :primary="iconOnly && !discrete"
    :ghost="discrete"
    :low-height="lowHeight || undefined"
    @click.stop.prevent="replacePlay()"
  >
    <template v-if="!discrete && !iconOnly">
      <span>
        {{ t('components.audio.PlayButton.button.discretePlay') }}
      </span>
    </template>
  </Button>
</template>

<style lang="scss" scoped>
.funkwhale.split-button {
  &.button {
    gap: 0px;
    padding: 0px;
  }
}
</style>
