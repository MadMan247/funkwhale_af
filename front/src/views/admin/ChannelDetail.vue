<script setup lang="ts">
import { humanSize, truncate } from '~/utils/filters'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { computed, ref } from 'vue'
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

const store = useStore()
const { t } = useI18n()
const router = useRouter()

const channel = ref()
const isLoading = ref(false)
const stats = ref()
const isLoadingStats = ref(false)
const open = ref(false)

const labels = computed(() => ({
  statsWarning: t('views.admin.ChannelDetail.warning.stats')
}))

const fetchData = async () => {
  isLoading.value = true

  try {
    const response = await axios.get(`manage/channels/${props.id}/`)
    channel.value = response.data
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

const fetchStats = async () => {
  isLoadingStats.value = true

  try {
    const response = await axios.get(`manage/channels/${props.id}/stats/`)
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
    await axios.delete(`manage/channels/${props.id}/`)
    router.push({ name: 'manage.channels' })
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
    v-if="channel"
    v-title="channel?.artist?.name"
    :h1="truncate(channel?.artist?.name)"
    page-heading
  >
    <template #image>
      <img
        v-if="channel?.artist?.cover?.urls.medium_square_crop"
        v-lazy="store.getters['instance/absoluteUrl'](channel?.artist?.cover?.urls.medium_square_crop)"
        alt=""
      >
      <img
        v-else
        alt=""
        src="../../assets/audio/default-cover.png"
      >
    </template>
    <div class="sub header">
      <template v-if="channel?.artist?.is_local">
        <Pill>
          <i class="bi bi-house-fill" />
          {{ t('views.admin.ChannelDetail.label.local') }}
        </Pill>
      </template>
      <template v-else>
        <Pill>
          <i class="bi bi-box-arrow-up-right" />
          {{ t('views.admin.ChannelDetail.label.federated') }}
        </Pill>
      </template>
    </div>

    <TagsList
      v-if="channel?.artist?.tags && channel?.artist?.tags.length > 0"
      :limit="5"
      detail-route="manage.library.tags.detail"
      :tags="channel?.artist?.tags"
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
        :to="{ name: 'channels.detail', params: { id: channel?.uuid } }"
      >
        {{ t('views.admin.ChannelDetail.link.localProfile') }}
      </Link>
      <fetch-button
        v-if="!channel?.actor?.is_local"
        class="basic item"
        :url="`federation/fetches/${channel?.id}/`"
        @refresh="fetchData"
      >
        <i class="refresh icon" />&nbsp;
        {{ t('views.admin.ChannelDetail.button.refresh') }}
      </fetch-button>
      <dangerous-button
        :is-loading="isLoading"
        low-height
        icon="bi-trash"
        :action="remove"
        :title="t('views.admin.ChannelDetail.modal.delete.header')"
      >
        {{ t('views.admin.ChannelDetail.button.delete') }}
        <template #content>
          {{ t('views.admin.ChannelDetail.modal.delete.content.warning') }}
        </template>
        <template #confirm>
          {{ t('views.admin.ChannelDetail.button.delete') }}
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
            :to="store.getters['instance/absoluteUrl'](`/api/admin/audio/channel/${channel?.id}`)"
            icon="bi-wrench"
            target="_blank"
          >
            {{ t('views.admin.ChannelDetail.link.django') }}
          </PopoverItem>
          <PopoverItem
            v-if="channel?.rss_url"
            :to="channel?.rss_url"
            icon="bi-box-arrow-up-right"
            target="_blank"
          >
            {{ t('views.admin.ChannelDetail.link.rss') }}
          </PopoverItem>
          <PopoverItem
            v-if="!channel?.artist?.is_local"
            :to="channel?.actor?.url || channel?.actor?.fid"
            icon="bi-box-arrow-up-right"
            target="_blank"
          >
            {{ t('views.admin.ChannelDetail.button.openRemote') }}
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
        :h3="t('views.admin.ChannelDetail.header.channelData')"
        class="category"
      />
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.ChannelDetail.table.channelData.name') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ channel?.artist?.name }}</span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <Link
          class="label"
          :to="{ name: 'manage.channels', query: { q: getQuery('category', channel?.artist?.content_category) } }"
        >
          {{ t('views.admin.ChannelDetail.table.channelData.category') }}
        </Link>
        <Spacer
          h
          grow
        />
        <span class="value">{{ channel?.artist?.content_category }}</span>
      </Layout>
      <Layout
        v-if="!channel?.actor?.is_local"
        flex
        class="details"
      >
        <Link
          class="label"
          :to="{ name: 'manage.moderation.domains.detail', params: { id: channel?.actor?.domain } }"
        >
          {{ t('views.admin.ChannelDetail.table.channelData.domain') }}
        </Link>
        <Spacer
          h
          grow
        />
        <span class="value">{{ channel?.actor?.domain }}</span>
      </Layout>
      <Layout
        v-if="channel?.artist?.description"
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.ChannelDetail.table.channelData.description') }}
        </span>
        <Spacer
          h
          grow
        />
        <sanitized-html
          tag="span"
          class="value"
          :html="channel?.artist?.description?.html"
        />
      </Layout>
    </Layout>
    <Layout
      stack
      style="flex: 1; gap: 0;"
    >
      <!-- TODO: Fix tooltips and replace Heading with Header -->
      <Heading
        :h3="t('views.admin.ChannelDetail.header.activity')"
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
          {{ t('views.admin.ChannelDetail.table.activity.firstSeen') }}
        </span>
        <Spacer
          h
          grow
        />
        <human-date :date="channel?.creation_date" />
      </Layout>
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.ChannelDetail.table.activity.listenings') }}
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
          {{ t('views.admin.ChannelDetail.table.activity.favorited') }}
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
        <Link
          class="label"
          :to="{ name: 'manage.moderation.reports.list', query: { q: getQuery('target', `channel:${channel?.uuid}`) } }"
        >
          {{ t('views.admin.ChannelDetail.table.activity.linkedReports') }}
        </Link>
        <Spacer
          h
          grow
        />
        <span class="value">{{ stats?.reports }}</span>
      </Layout>
    </Layout>
    <Layout
      stack
      style="flex: 1; gap: 0;"
    >
      <Heading
        :h3="t('views.admin.ChannelDetail.header.audioContent')"
        class="category"
      />
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.ChannelDetail.table.audioContent.cachedSize') }}
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
          {{ t('views.admin.ChannelDetail.table.audioContent.totalSize') }}
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
          :to="{ name: 'manage.library.uploads', query: { q: getQuery('channel_id', channel?.uuid) } }"
        >
          {{ t('views.admin.ChannelDetail.table.audioContent.uploads') }}
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
          :to="{ name: 'manage.library.albums', query: { q: getQuery('channel_id', channel?.uuid) } }"
        >
          {{ t('views.admin.ChannelDetail.table.audioContent.albums') }}
        </Link>
        <Spacer
          h
          grow
        />
        <span class="value">{{ channel?.artist?.albums_count }}</span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <Link
          class="label"
          :to="{ name: 'manage.library.tracks', query: { q: getQuery('channel_id', channel?.uuid) } }"
        >
          {{ t('views.admin.ChannelDetail.table.audioContent.tracks') }}
        </Link>
        <Spacer
          h
          grow
        />
        <span class="value">{{ channel?.artist?.tracks_count }}</span>
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
