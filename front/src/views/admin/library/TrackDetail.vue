<script setup lang="ts">
import { humanSize, truncate } from '~/utils/filters'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { ref, computed } from 'vue'
import { useStore } from '~/store'

import axios from 'axios'

import FetchButton from '~/components/federation/FetchButton.vue'
import TagsList from '~/components/tags/List.vue'
import DangerousButton from '~/components/common/DangerousButton.vue'
import Header from '~/components/ui/Header.vue'
import Layout from '~/components/ui/Layout.vue'
import Spacer from '~/components/ui/Spacer.vue'
import HumanDate from '~/components/common/HumanDate.vue'
import Link from '~/components/ui/Link.vue'
import Heading from '~/components/ui/Heading.vue'
import OptionsButton from '~/components/ui/button/Options.vue'
import Popover from '~/components/ui/Popover.vue'
import PopoverItem from '~/components/ui/popover/PopoverItem.vue'
import Loader from '~/components/ui/Loader.vue'

import useErrorHandler from '~/composables/useErrorHandler'

interface Props {
  id: number
}

const props = defineProps<Props>()

const { t } = useI18n()
const router = useRouter()
const store = useStore()

const track = ref()
const isLoading = ref(false)
const stats = ref()
const isLoadingStats = ref(false)
const open = ref(false)

const labels = computed(() => ({
  statsWarning: t('views.admin.library.TrackDetail.warning.stats')
}))

const fetchData = async () => {
  isLoading.value = true

  try {
    const response = await axios.get(`manage/library/tracks/${props.id}/`)
    track.value = response.data
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

const fetchStats = async () => {
  isLoadingStats.value = true

  try {
    const response = await axios.get(`manage/library/tracks/${props.id}/stats/`)
    stats.value = response.data
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoadingStats.value = false
}

fetchData()
fetchStats()

const remove = async () => {
  isLoading.value = true

  try {
    await axios.delete(`manage/library/tracks/${props.id}/`)
    await router.push({ name: 'manage.library.tracks' })
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

const getQuery = (field: string, value: string) => `${field}:"${value}"`
</script>

<template>
  <Loader v-if="isLoading" />
  <Header
    v-if="track"
    v-title="track?.title"
    :h1="truncate(track?.title)"
    page-heading
  >
    <template #image>
      <img
        v-if="track?.cover?.urls.medium_square_crop"
        v-lazy="store.getters['instance/absoluteUrl'](track?.cover?.urls.medium_square_crop)"
        alt=""
      >
      <img
        v-else
        alt=""
        src="../../../assets/audio/default-cover.png"
      >
    </template>
    <div class="sub header">
      <template v-if="track?.is_local">
        <Pill>
          <i class="bi bi-house-fill" />
          {{ t('views.admin.library.TrackDetail.header.local') }}
        </Pill>
      </template>
      <template v-else>
        <Pill>
          <i class="bi bi-box-arrow-up-right" />
          {{ t('views.admin.library.TrackDetail.header.federated') }}
        </Pill>
      </template>
    </div>

    <TagsList
      v-if="track?.tags && track?.tags.length > 0"
      :limit="5"
      detail-route="manage.library.tags.detail"
      :tags="track?.tags"
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
        :to="{ name: 'library.tracks.detail', params: { id: track?.id } }"
      >
        {{ t('views.admin.library.TrackDetail.link.localProfile') }}
      </Link>
      <fetch-button
        v-if="!track?.is_local"
        class="basic item"
        :url="`tracks/${track?.id}/fetches/`"
        @refresh="fetchData"
      >
        <i class="refresh icon" />&nbsp;
        {{ t('views.admin.library.TrackDetail.button.remoteRefresh') }}
      </fetch-button>
      <Link
        v-if="track?.is_local"
        solid
        primary
        low-height
        icon="bi-pencil-fill"
        :to="{ name: 'library.tracks.edit', params: { id: track?.id } }"
      >
        {{ t('views.admin.library.TrackDetail.button.edit') }}
      </Link>
      <dangerous-button
        :is-loading="isLoading"
        low-height
        icon="bi-trash"
        :action="remove"
        :title="t('views.admin.library.TrackDetail.modal.delete.header')"
      >
        {{ t('views.admin.library.TrackDetail.button.delete') }}
        <template #modal-content>
          {{ t('views.admin.library.TrackDetail.modal.delete.content.warning') }}
        </template>
        <template #modal-confirm>
          {{ t('views.admin.library.TrackDetail.button.delete') }}
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
            v-if="store.state.auth.profile?.is_superuser"
            :to="store.getters['instance/absoluteUrl'](`/api/admin/music/track/${track?.id}`)"
            icon="bi-wrench"
            target="_blank"
          >
            {{ t('views.admin.library.TrackDetail.link.django') }}
          </PopoverItem>
          <PopoverItem
            v-if="track?.mbid"
            :to="`https://musicbrainz.org/recording/${track?.mbid}`"
            icon="bi-box-arrow-up-right"
            target="_blank"
          >
            {{ t('views.admin.library.TrackDetail.link.musicbrainz') }}
          </PopoverItem>
          <PopoverItem
            :to="track?.url || track?.fid"
            icon="bi-box-arrow-up-right"
            target="_blank"
          >
            {{ t('views.admin.library.TrackDetail.link.remoteProfile') }}
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
        :h3="t('views.admin.library.TrackDetail.header.trackData')"
        class="category"
      />
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.library.TrackDetail.table.track.title') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ track?.title }}</span>
      </Layout>
      <Layout
        v-if="track?.album"
        flex
        class="details"
      >
        <Link
          class="label"
          :to="{ name: 'manage.library.albums.detail', params: { id: track?.album?.id } }"
        >
          {{ t('views.admin.library.TrackDetail.link.album') }}
        </Link>
        <Spacer
          h
          grow
        />
        <span class="value">{{ track?.album?.title }}</span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <Link
          class="label"
          :to="{ name: 'manage.library.artists.detail', params: { id: track?.artist_credit[0]?.artist?.id } }"
        >
          {{ t('views.admin.library.TrackDetail.link.artist') }}
        </Link>
        <Spacer
          h
          grow
        />
        <span class="value">{{ track?.artist_credit[0]?.artist?.name }}</span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.library.TrackDetail.table.track.position') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ track?.position }}</span>
      </Layout>
      <Layout
        v-if="track?.disc_number"
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.library.TrackDetail.table.track.discNumber') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ track?.disc_number }}</span>
      </Layout>
      <Layout
        v-if="track?.copyright"
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.library.TrackDetail.table.track.copyright') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ track?.copyright }}</span>
      </Layout>
      <Layout
        v-if="track?.license"
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.library.TrackDetail.table.track.license') }}
        </span>
        <Spacer
          h
          grow
        />
        <router-link
          class="value"
          :to="{
            name: 'manage.library.tracks',
            query: { q: getQuery('license', track?.license) }
          }"
        >
          {{ track.license }}
        </router-link>
      </Layout>
      <Layout
        v-if="!track?.is_local"
        flex
        class="details"
      >
        <router-link
          class="label"
          :to="{
            name: 'manage.moderation.domains.detail',
            params: { id: track?.domain }
          }"
        >
          {{ t('views.admin.library.TrackDetail.link.domain') }}
        </router-link>
        <Spacer
          h
          grow
        />
        <span class="value">{{ track?.domain }}</span>
      </Layout>
      <Layout
        v-if="track?.description"
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.library.TrackDetail.table.track.description') }}
        </span>
        <Spacer
          h
          grow
        />
        <sanitized-html
          tag="span"
          class="value"
          :html="track?.description?.html"
        />
      </Layout>
    </Layout>
    <Layout
      stack
      style="flex: 1; gap: 0;"
    >
      <!-- TODO: fix tooltips and replace heading with header -->
      <Heading
        :h3="t('views.admin.library.TrackDetail.header.activity')"
        class="category"
      >
        <template #action>
          <span :data-tooltip="labels.statsWarning"><i class="question circle icon" /></span>
        </template>
      </Heading>
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.library.TrackDetail.table.activity.firstSeen') }}
        </span>
        <Spacer
          h
          grow
        />
        <human-date :date="track?.creation_date" />
      </Layout>
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.library.TrackDetail.table.activity.listenings') }}
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
          {{ t('views.admin.library.TrackDetail.table.activity.favorited') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ stats?.track_favorites }}</span>
      </Layout>
    </Layout>
    <Layout
      stack
      style="flex: 1; gap: 0;"
    >
      <Heading
        :h3="t('views.admin.library.TrackDetail.header.trackData')"
        class="category"
      />
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.library.TrackDetail.table.trackData.cachedSize') }}
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
          {{ t('views.admin.library.TrackDetail.table.trackData.totalSize') }}
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
          :to="{ name: 'manage.library.libraries', query: { q: getQuery('track_id', track?.id) } }"
        >
          {{ t('views.admin.library.TrackDetail.link.libraries') }}
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
          :to="{ name: 'manage.library.uploads', query: { q: getQuery('track_id', track?.id) } }"
        >
          {{ t('views.admin.library.TrackDetail.link.uploads') }}
        </Link>
        <Spacer
          h
          grow
        />
        <span class="value">{{ stats?.uploads }}</span>
      </Layout>
    </Layout>
  </Layout>
</template>

<style scoped lang="scss">
@import '~/style/funkwhale.scss';

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

  @include light-theme {
    border-color: var(--fw-gray-300);
  }

  @include dark-theme {
    border-color: var(--fw-gray-800);
  }

  .label {
    font-weight: 800;

    @include light-theme {
      color: var(--fw-gray-600);
    }

    @include dark-theme {
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
