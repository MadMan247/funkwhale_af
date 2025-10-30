<script setup lang="ts">
import { humanSize, truncate } from '~/utils/filters'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { computed, ref } from 'vue'
import { useStore } from '~/store'

import axios from 'axios'

import DangerousButton from '~/components/common/DangerousButton.vue'
import FetchButton from '~/components/federation/FetchButton.vue'
import TagsList from '~/components/tags/List.vue'

import useErrorHandler from '~/composables/useErrorHandler'

import Header from '~/components/ui/Header.vue'
import Layout from '~/components/ui/Layout.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Pill from '~/components/ui/Pill.vue'
import HumanDate from '~/components/common/HumanDate.vue'
import Link from '~/components/ui/Link.vue'
import Heading from '~/components/ui/Heading.vue'
import Popover from '~/components/ui/Popover.vue'
import PopoverItem from '~/components/ui/popover/PopoverItem.vue'
import OptionsButton from '~/components/ui/button/Options.vue'
import Loader from '~/components/ui/Loader.vue'

interface Props {
  id: number
}

const props = defineProps<Props>()

const store = useStore()
const { t } = useI18n()
const router = useRouter()

const labels = computed(() => ({
  statsWarning: t('views.admin.library.ArtistDetail.warning.stats')
}))

const isLoading = ref(false)
const object = ref()
const fetchData = async () => {
  isLoading.value = true

  try {
    const response = await axios.get(`manage/library/artists/${props.id}/`)
    object.value = response.data
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

const isLoadingStats = ref(false)
const stats = ref()
const fetchStats = async () => {
  isLoadingStats.value = true

  try {
    const response = await axios.get(`manage/library/artists/${props.id}/stats/`)
    stats.value = response.data
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoadingStats.value = false
}

fetchStats()
fetchData()

const remove = async () => {
  isLoading.value = true

  try {
    await axios.delete(`manage/library/artists/${props.id}/`)
    router.push({ name: 'manage.library.artists' })
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

const getQuery = (field: string, value: string) => `${field}:"${value}"`

const open = ref(false)
</script>

<template>
  <Loader v-if="isLoading" />
  <Header
    v-if="object"
    v-title="object.name"
    :h1="truncate(object.name)"
    page-heading
  >
    <template #image>
      <img
        v-if="object.cover?.urls.medium_square_crop"
        v-lazy="store.getters['instance/absoluteUrl'](object.cover.urls.medium_square_crop)"
        alt=""
      >
      <img
        v-else
        alt=""
        src="../../../assets/audio/default-cover.png"
      >
    </template>
    <div class="sub header">
      <template v-if="object.is_local">
        <Pill>
          <i class="bi bi-house-fill" />
          {{ t('views.admin.library.ArtistDetail.header.local') }}
        </Pill>
      </template>
      <template v-else>
        <Pill>
          <i class="bi bi-box-arrow-up-right" />
          {{ t('views.admin.library.ArtistDetail.header.federated') }}
        </Pill>
      </template>
    </div>

    <TagsList
      v-if="object.tags && object.tags.length > 0"
      :limit="5"
      detail-route="manage.library.tags.detail"
      :tags="object.tags"
    />
    <Spacer />
    <Layout
      flex
      class="header-buttons"
    >
      <Link
        solid
        primary
        low-height
        icon="bi-info-circle"
        :to="{ name: 'library.artists.detail', params: { id: object.id } }"
      >
        {{ t('views.admin.library.ArtistDetail.link.localProfile') }}
      </Link>
      <fetch-button
        v-if="!object.is_local"
        class="basic item"
        :url="`artists/${object.id}/fetches/`"
        @refresh="fetchData"
      >
        <i class="refresh icon" />&nbsp;
        {{ t('views.admin.library.ArtistDetail.button.remoteRefresh') }}
      </fetch-button>
      <Link
        v-if="object.is_local"
        solid
        primary
        low-height
        icon="bi-pencil-fill"
        :to="{ name: 'library.artists.edit', params: { id: object.id } }"
      >
        {{ t('views.admin.library.ArtistDetail.button.edit') }}
      </Link>
      <dangerous-button
        :is-loading="isLoading"
        low-height
        icon="bi-trash"
        :action="remove"
        :title="t('views.admin.library.ArtistDetail.modal.delete.header')"
      >
        {{ t('views.admin.library.ArtistDetail.button.delete') }}
        <template #content>
          {{ t('views.admin.library.ArtistDetail.modal.delete.content.warning') }}
        </template>
        <template #confirm>
          {{ t('views.admin.library.ArtistDetail.button.delete') }}
        </template>
      </dangerous-button>
      <Spacer grow />
      <Popover v-model="open">
        <template #default="{ toggleOpen }">
          <OptionsButton
            is-square-small
            @click="toggleOpen()"
          />
        </template>

        <template #items>
          <PopoverItem
            v-if="store.state.auth.profile && store.state.auth.profile.is_superuser"
            :to="store.getters['instance/absoluteUrl'](`/api/admin/music/album/${object.id}`)"
            icon="bi-wrench"
            target="_blank"
          >
            {{ t('views.admin.library.AlbumDetail.link.django') }}
          </PopoverItem>
          <PopoverItem
            v-if="!object.is_local"
            :to="`albums/${object.id}/fetches/`"
            icon="bi-arrow-clockwise"
            @click="fetchData()"
          >
            {{ t('views.admin.library.AlbumDetail.button.remoteRefresh') }}
          </PopoverItem>
          <PopoverItem
            v-if="object.mbid"
            :to="`https://musicbrainz.org/release/${object.mbid}`"
            icon="bi-box-arrow-up-right"
            target="_blank"
          >
            {{ t('views.admin.library.AlbumDetail.link.musicbrainz') }}
          </PopoverItem>
          <PopoverItem
            :to="object.url || object.fid"
            icon="bi-box-arrow-up-right"
            target="_blank"
          >
            {{ t('views.admin.library.AlbumDetail.link.remoteProfile') }}
          </PopoverItem>
        </template>
      </Popover>
    </Layout>
  </Header>

  <Layout
    flex
    gap-64
  >
    <Layout
      stack
      style="flex: 1; gap: 0;"
    >
      <Heading
        :h3="t('views.admin.library.ArtistDetail.header.artistData')"
        class="category"
      />
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.library.ArtistDetail.table.artist.name') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ object?.name }}</span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <Link
          class="label"
          :to="{ name: 'manage.library.artists', query: { q: getQuery('category', object?.content_category) } }"
        >
          {{ t('views.admin.library.ArtistDetail.link.category') }}
        </Link>
        <Spacer
          h
          grow
        />
        <span class="value">{{ object?.content_category }}</span>
      </Layout>
      <Layout
        v-if="!object?.is_local"
        flex
        class="details"
      >
        <Link
          class="label"
          :to="{ name: 'manage.moderation.domains.detail', params: { id: object?.domain } }"
        >
          {{ t('views.admin.library.ArtistDetail.link.domain') }}
        </Link>
        <Spacer
          h
          grow
        />
        <span class="value">{{ object?.domain }}</span>
      </Layout>
      <Layout
        v-if="object?.description"
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.library.ArtistDetail.table.artist.description') }}
        </span>
        <Spacer
          h
          grow
        />
        <sanitized-html
          tag="span"
          class="value"
          :html="object.description.html"
        />
      </Layout>
    </Layout>
    <Layout
      stack
      style="flex: 1; gap: 0;"
    >
      <!-- TODO: Fix tooltip and replace headings with headers. -->
      <Heading
        :h3="t('views.admin.library.ArtistDetail.header.activity')"
        class="category"
      >
        <template #action>
          <tooltip :content="labels.statsWarning" />
        </template>
      </Heading>

      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.library.ArtistDetail.table.activity.firstSeen') }}
        </span>
        <Spacer
          h
          grow
        />
        <human-date :date="object?.creation_date" />
      </Layout>
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.library.ArtistDetail.table.activity.listenings') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ stats?.listenings }}</span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.library.ArtistDetail.table.activity.favorited') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ stats?.track_favorites }}</span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.library.ArtistDetail.table.activity.playlists') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ stats?.playlists }}</span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <Link
          class="label"
          :to="{ name: 'manage.moderation.reports.list', query: { q: getQuery('target', `artist:${object?.id}`) } }"
        >
          {{ t('views.admin.library.ArtistDetail.link.reports') }}
        </Link>
        <Spacer
          h
          grow
        />
        <span class="value">{{ stats?.reports }}</span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <Link
          class="label"
          :to="{ name: 'manage.library.edits', query: { q: getQuery('target', 'artist ' + object?.id) } }"
        >
          {{ t('views.admin.library.ArtistDetail.link.edits') }}
        </Link>
        <Spacer
          h
          grow
        />
        <span class="value">{{ stats?.mutations }}</span>
      </Layout>
    </Layout>
    <Layout
      stack
      style="flex: 1; gap: 0;"
    >
      <Heading
        :h3="t('views.admin.library.ArtistDetail.header.audioContent')"
        class="category"
      />
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.library.ArtistDetail.table.audioContent.cachedSize') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ humanSize(stats?.media_downloaded_size) }}</span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.library.ArtistDetail.table.audioContent.totalSize') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ humanSize(stats?.media_total_size) }}</span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <Link
          class="label"
          :to="{ name: 'manage.library.libraries', query: { q: getQuery('artist_id', object?.id) } }"
        >
          {{ t('views.admin.library.ArtistDetail.link.libraries') }}
        </Link>
        <Spacer
          h
          grow
        />
        <span class="value">{{ stats?.libraries }}</span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <Link
          class="label"
          :to="{ name: 'manage.library.uploads', query: { q: getQuery('artist_id', object?.id) } }"
        >
          {{ t('views.admin.library.ArtistDetail.link.uploads') }}
        </Link>
        <Spacer
          h
          grow
        />
        <span class="value">{{ stats?.uploads }}</span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <Link
          class="label"
          :to="{ name: 'manage.library.albums', query: { q: getQuery('artist_id', object?.id) } }"
        >
          {{ t('views.admin.library.ArtistDetail.link.albums') }}
        </Link>
        <Spacer
          h
          grow
        />
        <span class="value">{{ object?.albums_count }}</span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <Link
          class="label"
          :to="{ name: 'manage.library.tracks', query: { q: getQuery('artist_id', object?.id) } }"
        >
          {{ t('views.admin.library.ArtistDetail.link.tracks') }}
        </Link>
        <Spacer
          h
          grow
        />
        <span class="value">{{ object?.tracks_count }}</span>
      </Layout>
    </Layout>
  </Layout>
</template>

<style scoped lang="scss">
@use '~/style/funkwhale.scss';

.channel-image {
  width: 200px;
  height: 200px;
  border: none;
}

h3.category {
  margin-bottom: 16px;
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

  a.label,
  a.value {
    text-decoration: underline;
  }

  &:last-child {
    border-bottom: 1px solid;
  }
}
</style>
