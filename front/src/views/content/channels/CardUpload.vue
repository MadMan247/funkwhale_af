<script setup lang="ts">
import type { Channel } from '~/types'

import { momentFormat } from '~/utils/filters'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'
import { computed } from 'vue'

import TagsList from '~/components/tags/List.vue'

interface Props {
  channel: Channel
  callback: (object:Channel)=>void
}

const props = defineProps<Props>()
const store = useStore()

const fallbackImageUrl = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAzODQgNTEyIj48IS0tIUZvbnQgQXdlc29tZSBGcmVlIDYuNi4wIGJ5IEBmb250YXdlc29tZSAtIGh0dHBzOi8vZm9udGF3ZXNvbWUuY29tIExpY2Vuc2UgLSBodHRwczovL2ZvbnRhd2Vzb21lLmNvbS9saWNlbnNlL2ZyZWUgQ29weXJpZ2h0IDIwMjQgRm9udGljb25zLCBJbmMuLS0+PHBhdGggZD0iTTM4MS45IDM4OC4yYy02LjQgMjcuNC0yNy4yIDQyLjgtNTUuMSA0OC0yNC41IDQuNS00NC45IDUuNi02NC41LTEwLjItMjMuOS0yMC4xLTI0LjItNTMuNC0yLjctNzQuNCAxNy0xNi4yIDQwLjktMTkuNSA3Ni44LTI1LjggNi0xLjEgMTEuMi0yLjUgMTUuNi03LjQgNi40LTcuMiA0LjQtNC4xIDQuNC0xNjMuMiAwLTExLjItNS41LTE0LjMtMTctMTIuMy04LjIgMS40LTE4NS43IDM0LjYtMTg1LjcgMzQuNi0xMC4yIDIuMi0xMy40IDUuMi0xMy40IDE2LjcgMCAyMzQuNyAxLjEgMjIzLjktMi41IDIzOS41LTQuMiAxOC4yLTE1LjQgMzEuOS0zMC4yIDM5LjUtMTYuOCA5LjMtNDcuMiAxMy40LTYzLjQgMTAuNC00My4yLTguMS01OC40LTU4LTI5LjEtODYuNiAxNy0xNi4yIDQwLjktMTkuNSA3Ni44LTI1LjggNi0xLjEgMTEuMi0yLjUgMTUuNi03LjQgMTAuMS0xMS41IDEuOC0yNTYuNiA1LjItMjcwLjIgLjgtNS4yIDMtOS42IDcuMS0xMi45IDQuMi0zLjUgMTEuOC01LjUgMTMuNC01LjUgMjA0LTM4LjIgMjI4LjktNDMuMSAyMzIuNC00My4xIDExLjUtLjggMTguMSA2IDE4LjEgMTcuNiAuMiAzNDQuNSAxLjEgMzI2LTEuOCAzMzguNXoiLz48L3N2Zz4='

/* TODO: Replace with actual target: */
const imageUrl = computed(() => props.channel.artist?.cover
  ? store.getters['instance/absoluteUrl'](props.channel.artist?.cover.urls.medium_square_crop)
  : fallbackImageUrl
)

// TODO: Find out if still useful:
// const urlId = computed(() => props.channel.actor?.is_local
//   ? props.channel.actor.preferred_username
//   : props.channel.actor
//     ? props.channel.actor.full_username
//     : props.channel.uuid
// )

const { t } = useI18n()
const updatedTitle = computed(() => {
  const date = momentFormat(new Date(props.channel.artist?.modification_date ?? '1970-01-01'))
  return t('components.audio.ChannelCard.title', { date })
})
</script>

<template>
  <fw-button
    style="border:transparent; background:transparent;"
    @click="callback(channel)"
  >
    <fw-card
      :title="channel.artist?.name"
      :image="imageUrl"
    >
      <div
        class="description"
        style="display:flex; justify-content:space-between; min-height:32px; align-items: baseline;"
        :title="updatedTitle"
      >
        <!-- <p>
        {{ channel.artist?.description.text }}
      </p> -->
        <span
          class="meta ellipsis"
        >
          {{ t('components.audio.ChannelCard.meta.tracks', channel.artist?.tracks_count ?? 0) }}
        </span>
        <TagsList
          style="pointer-events:none;"
          label-classes="tiny"
          :truncate-size="20"
          :limit="2"
          :show-more="false"
          :tags="channel.artist?.tags ?? []"
        />
      </div>
    <!-- <div class="extra content">
      <time
        class="meta ellipsis"
        :datetime="channel.artist?.modification_date"
        :title="updatedTitle"
      >
        {{ updatedAgo }}
      </time>
    </div> -->
    </fw-card>
  </fw-button>
</template>
