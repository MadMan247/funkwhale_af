<script setup lang="ts">
import type { Track, Actor } from '~/types'

import { humanSize, momentFormat } from '~/utils/filters'
import { computed, ref, watchEffect } from 'vue'
import { useI18n } from 'vue-i18n'

import time from '~/utils/time'
import axios from 'axios'

import LibraryWidget from '~/components/federation/LibraryWidget.vue'
import PlaylistWidget from '~/components/playlists/Widget.vue'
import TagsList from '~/components/tags/List.vue'
import Layout from '~/components/ui/Layout.vue'
import Section from '~/components/ui/Section.vue'
import Link from '~/components/ui/Link.vue'
import Spacer from '~/components/ui/Spacer.vue'

import useErrorHandler from '~/composables/useErrorHandler'

interface Events {
  (e: 'actors-loaded', actors: Actor[]): void
}

interface Props {
  track: Track
}

const { t } = useI18n()

const emit = defineEmits<Events>()
const props = defineProps<Props>()

const musicbrainzUrl = computed(() => props.track.mbid
  ? `https://musicbrainz.org/recording/${props.track.mbid}`
  : null
)

const upload = computed(() => props.track.uploads?.[0] ?? null)

const license = ref()
const fetchLicense = async (licenseId: string) => {
  license.value = undefined

  try {
    const response = await axios.get(`licenses/${licenseId}`)
    license.value = response.data
  } catch (error) {
    useErrorHandler(error as Error)
  }
}

watchEffect(() => {
  if (props.track.license) {
    fetchLicense(props.track.license)
  }
})

const releaseDetails: {
  label: string;
  releaseValue: string;
  link?: { name: string; params: { id: number } };
}[] = [
  {
    label: t('components.library.TrackDetail.table.release.artist'),
    releaseValue: props.track.artist_credit.map(ac => ac.credit).join(', '),
    link: props.track.artist_credit.length > 0
      ? {
          name: 'library.artists.detail',
          params: { id: props.track.artist_credit[0]!.artist.id }
        }
      : undefined
  },
  {
    label:
      props.track.album?.artist_credit[0]?.artist.content_category === 'music'
        ? t('components.library.TrackDetail.table.release.album')
        : t('components.library.TrackDetail.table.release.series'),
    releaseValue: props.track.album?.title || t('components.library.TrackDetail.notApplicable'),
    link: props.track.album
      ? {
          name: 'library.albums.detail',
          params: { id: props.track.album.id }
        }
      : undefined
  },
  {
    label: t('components.library.TrackDetail.table.release.year'),
    releaseValue: props.track.album?.release_date
      ? momentFormat(new Date(props.track.album.release_date), 'Y')
      : t('components.library.TrackDetail.notApplicable')
  },
  {
    label: t('components.library.TrackDetail.table.release.copyright'),
    releaseValue: props.track.copyright || t('components.library.TrackDetail.notApplicable')
  },
  {
    label: t('components.library.TrackDetail.table.release.license'),
    releaseValue: license.value?.name || t('components.library.TrackDetail.notApplicable')
  }
]

const trackDetails: {
  label: string;
  trackValue: string | number;
  link?: { name: string; params: { id: number } };
}[] = [
  {
    label: t('components.library.TrackDetail.table.track.duration'),
    trackValue: upload?.value?.duration ? time.parse(upload.value.duration) : t('components.library.TrackDetail.notApplicable')
  },
  {
    label:
    t('components.library.TrackDetail.table.track.size'),
    trackValue: upload?.value?.size ? humanSize(upload.value.size) : t('components.library.TrackDetail.notApplicable')
  },
  {
    label: t('components.library.TrackDetail.table.track.codec'),
    trackValue: upload?.value?.extension || t('components.library.TrackDetail.notApplicable')
  },
  {
    label:
    t('components.library.TrackDetail.table.track.bitrate.label'),
    trackValue: upload?.value?.bitrate
      ? t('components.library.TrackDetail.table.track.bitrate.value', { bitrate: humanSize(upload.value.bitrate) })
      : t('components.library.TrackDetail.notApplicable')
  },
  {
    label: t('components.library.TrackDetail.table.track.downloads'),
    trackValue: props.track.downloads_count
  }
]
</script>

<template>
  <Layout
    v-if="track"
    stack
  >
    <TagsList
      v-if="track.tags && track.tags.length > 0"
      style="margin-top: -16px;"
      :tags="track.tags"
    />

    <Layout
      flex
      gap-64
    >
      <Layout
        stack
        style="flex: 1; gap: 0;"
      >
        <!-- TODO: Find out why lint:tsc doesn't like `to` while language server does -->
        <!-- @vue-ignore -->
        <Section
          align-left
          h2="Release Details"
          :action="musicbrainzUrl ? {
            text: 'View on MusicBrainz',
            to: musicbrainzUrl
          } : undefined"
          icon="bi-box-arrow-up-right"
        />
        <Layout
          v-for="item in releaseDetails"
          :key="item.label"
          flex
          class="details"
        >
          <span class="label">{{ item.label }}</span>
          <Spacer
            h
            grow
          />
          <Link
            v-if="item.link"
            class="value"
            :to="item.link"
          >
            {{ item.releaseValue }}
          </Link>
          <span
            v-else
            class="value"
          >
            {{ item.releaseValue }}
          </span>
        </Layout>
      </Layout>

      <Layout
        stack
        style="flex: 1; gap: 0;"
      >
        <Section
          align-left
          h2="Track Details"
        />
        <Layout
          v-for="item in trackDetails"
          :key="item.label"
          flex
          class="details"
        >
          <span class="label">{{ item.label }}</span>
          <Spacer
            h
            grow
          />
          <Link
            v-if="item.link"
            class="value"
            :to="item.link"
          >
            {{ item.trackValue }}
          </Link>
          <span
            v-else
            class="value"
          >
            {{ item.trackValue }}
          </span>
        </Layout>
      </Layout>
    </Layout>

    <h2>{{ t('components.library.TrackDetail.header.playlists') }}</h2>
    <playlist-widget
      :url="'playlists/'"
      :filters="{track: track.id, playable: true, ordering: '-modification_date'}"
    />

    <h2>{{ t('components.library.TrackDetail.header.library') }}</h2>
    <library-widget
      :url="`tracks/${track.id}/actors/`"
      @loaded="emit('actors-loaded', $event)"
    >
      {{ t('components.library.TrackDetail.description.library') }}
    </library-widget>
  </Layout>
</template>

<style scoped lang="scss">
@use '~/style/funkwhale.scss';

.channel-image {
  width: 200px;
  height: 200px;
  border: none;
}

.details {
  padding: 0 16px;
  height: 72px;
  align-items: center;
  border-top: 1px solid;
  min-width: 280px;

  @include funkwhale.light-theme {
    border-color: var(--fw-gray-300);
  }
  @include funkwhale.dark-theme {
    border-color: var(--fw-gray-800);
  }

  .label {
    font-weight: 800;

    @include funkwhale.light-theme {
      color: var(--fw-gray-600);
    }

    @include funkwhale.dark-theme {
      color: var(--fw-gray-500);
    }
  }

  a.value {
    text-decoration: underline;
  }

  &:last-child {
    border-bottom: 1px solid;
  }
}
</style>
