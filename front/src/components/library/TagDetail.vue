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
        solid
        secondary
        :to="{name: 'manage.library.tags.detail', params: {id: id}}"
      >
        {{ t('components.library.TagDetail.link.moderation') }}
      </Link>
    </Layout>
    <Spacer :size="64" />
    <ArtistWidget
      :key="'artist' + id"
      :title="t('components.library.TagDetail.header.artists')"
      :action="{
        text: t('components.library.TagDetail.link.artists'),
        to: {name: 'library.artists.browse', query: {tag: id}},
        // secondary: true,
        // solid: true
      }"
      :query="{
        playable: true,
        tag: [id],
        ordering: ['-creation_date'],
        include_channels: false
      }"
      :controls="false /*TODO: Check where this is coming from - it's not part of any API I see*/"
    />
    <Spacer size-64 />
    <ChannelsWidget
      :key="'channels' + id"
      :title="t('components.library.TagDetail.header.channels')"
      :action="{
        text: t('components.library.TagDetail.link.channels'),
        to: { name: 'library.channels.browse', query: { tag: id } },
        // secondary: true,
        // solid: true
      }"
      :query="{
        page_size: 12,
        tag: [id],
        ordering: ['-creation_date']
      }"
      show-modification-date
    />
    <Spacer size-64 />
    <AlbumWidget
      :key="`album${id}`"
      :title="t('components.library.TagDetail.header.albums')"
      :action="{
        text: t('components.library.TagDetail.link.albums'),
        to: {name: 'library.albums.browse', query: {tag: id}},
        // secondary: true,
        // solid: true
      }"
      :query="{
        playable: true,
        tag: [id],
        ordering: ['-creation_date']
      }"
      show-count
      :controls="false /*TODO: Check where this is coming from - it's not part of any API I see*/"
    />
    <Spacer :size="64" />
    <!-- TODO: What was show-count doing? -->
    <TrackWidget
      :key="`track${id}`"
      :title="t('components.library.TagDetail.header.tracks')"
      url="tracks"
      :query="{
        playable: true,
        tag: [id],
        ordering: ['-creation_date'],
        page_size: 12
      }"
      item-classes="track-item inline"
      :is-activity="false"
      show-count
    />
  </Layout>
</template>

<style scoped>
/* TODO: Add this variant into the props/classes accepted by pill */
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
