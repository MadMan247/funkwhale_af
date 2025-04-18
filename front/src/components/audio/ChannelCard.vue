<script setup lang="ts">
import type { Channel } from '~/types'

import { momentFormat } from '~/utils/filters'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'
import { computed } from 'vue'

import moment from 'moment'

import PlayButton from '~/components/audio/PlayButton.vue'
import Card from '~/components/ui/Card.vue'
import Spacer from '~/components/ui/Spacer.vue'
import ActorLink from '~/components/common/ActorLink.vue'

interface Props {
  object: Channel
}

const props = defineProps<Props>()
const store = useStore()

const imageUrl = computed(() => props.object.artist?.cover
  ? store.getters['instance/absoluteUrl'](props.object.artist.cover.urls.medium_square_crop)
  : null
)

const urlId = computed(() => props.object.actor?.is_local
  ? props.object.actor.preferred_username
  : props.object.actor
    ? props.object.actor.full_username
    : props.object.uuid
)

const { t } = useI18n()
const updatedTitle = computed(() => {
  const date = momentFormat(new Date(props.object.artist?.modification_date ?? '1970-01-01'))
  return t('components.audio.ChannelCard.title', { date })
})

// TODO (wvffle): Use time ago
const updatedAgo = computed(() => moment(props.object.artist?.modification_date).fromNow())
</script>

<template>
  <Card
    :title="object.artist?.name"
    :tags="object.artist?.tags ?? []"
    class="artist-card"
    :to="{name: 'channels.detail', params: {id: urlId}}"
    solid
    small
  >
    <template #topright>
      <PlayButton
        icon-only
        :artist="object.artist"
        :is-playable="true"
      />
    </template>

    <template #image>
      <img
        v-if="imageUrl"
        v-lazy="imageUrl"
        :alt="object.artist?.name"
        :class="[object.artist?.content_category === 'podcast' ? 'podcast-image' : 'channel-image']"
      >
      <i
        v-else
        class="bi bi-person-circle"
        style="font-size: 167px; margin: 16px;"
      />
    </template>

    <template #default>
      <Spacer :size="8" />
      <ActorLink
        :actor="object.attributed_to"
        discrete
      />
    </template>

    <template #footer>
      <time
        :datetime="object.artist?.modification_date"
        :title="updatedTitle"
      >
        {{ updatedAgo }}
      </time>
      <i class="bi bi-dot" />
      <span
        v-if="object.artist?.content_category === 'podcast'"
      >
        {{ t('components.audio.ChannelCard.meta.episodes', object.artist.tracks_count) }}
      </span>
      <span v-else>
        {{ t('components.audio.ChannelCard.meta.tracks', object.artist?.tracks_count ?? 0) }}
      </span>
      <Spacer
        h
        grow
      />
      <PlayButton
        :dropdown-only="true"
        :is-playable="true"
        :artist="object.artist"
        :channel="object"
        :account="object.attributed_to"
        discrete
      />
    </template>
  </Card>
</template>

<style lang="scss" scoped>
.channel-image {
  border-radius: 50%;
  width: 168px;
  height: 168px;
  margin: 16px;
}

.podcast-image {
  width: 168px;
  height: 168px;
  margin: 16px;
}

.play-button {
  top: 16px;
  right: 16px;
}
</style>
