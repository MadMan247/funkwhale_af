<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'

import ChannelsWidget from '~/components/audio/ChannelsWidget.vue'
import TrackWidget from '~/components/audio/track/Widget.vue'
import AlbumWidget from '~/components/album/Widget.vue'
import ArtistWidget from '~/components/artist/Widget.vue'
import RadioButton from '~/components/radios/Button.vue'
import Layout from '~/components/ui/Layout.vue'
import Link from '~/components/ui/Link.vue'
import Spacer from '~/components/ui/Spacer.vue'

interface Props {
  id: string
}

const store = useStore()
const { t } = useI18n()

const props = defineProps<Props>()

const labels = computed(() => ({
  title: `#${props.id}`
}))
</script>

<template>
  <Layout
    raised
    main
  >
    <h1 class="ui header">
      <span class="funkwhale solid raised secondary pill">
        <span class="pill-content">
          {{ labels.title }}
        </span>
      </span>
    </h1>
    <Layout
      flex
      class="buttons"
    >
      <radio-button
        type="tag"
        :object-id="id"
      />
      <Link
        v-if="store.state.auth.availablePermissions['library']"
        icon="bi-wrench"
        secondary
        :to="{name: 'manage.library.tags.detail', params: {id: id}}"
      >
        {{ t('components.library.TagDetail.link.moderation') }}
      </Link>
    </Layout>
    <Spacer :size="64" />
    <artist-widget
      :key="'artist' + id"
      :controls="false"
      :title="t('components.library.TagDetail.header.artists')"
      :action="{
        text: t('components.library.TagDetail.link.artists'),
        to: {name: 'library.artists.browse', query: {tag: id}},
        // secondary: true,
        // solid: true
      }"
      :filters="{playable: true, ordering: '-creation_date', tag: id, include_channels: 'false'}"
    />
    <Spacer :size="64" />
    <channels-widget
      :key="'channels' + id"
      :show-modification-date="true"
      :limit="12"
      :title="t('components.library.TagDetail.header.channels')"
      :action="{
        text: t('components.library.TagDetail.link.channels'),
        to: {name: 'library.channels.browse', query: {tag: id}},
        // secondary: true,
        // solid: true
      }"
      :filters="{tag: id, ordering: '-creation_date'}"
    />
    <Spacer :size="64" />
    <album-widget
      :key="'album' + id"
      :show-count="true"
      :controls="false"
      :filters="{playable: true, ordering: '-creation_date', tag: id}"
      :title="t('components.library.TagDetail.header.albums')"
      :action="{
        text: t('components.library.TagDetail.link.albums'),
        to: {name: 'library.albums.browse', query: {tag: id}},
        // secondary: true,
        // solid: true
      }"
    />
    <Spacer :size="64" />
    <track-widget
      :key="'track' + id"
      :show-count="true"
      :limit="12"
      item-classes="track-item inline"
      :url="'/tracks/'"
      :is-activity="false"
      :filters="{playable: true, ordering: '-creation_date', tag: id}"
      :title="t('components.library.TagDetail.header.tracks')"
    />
  </Layout>
</template>

<style lang="scss" scoped>
h1 > .pill {
  border-radius: 100vh;
  display: inline-block;
  padding: 10px;

  > .pill-content {
    font-size: 48px;
    line-height: 48px;
    padding: 20px 30px;
  }
}
</style>
