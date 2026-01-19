<script setup lang="ts">
import type { Track, Listening } from '~/types'

import { ref, reactive, watch, onMounted } from 'vue'
import { useStore } from '~/store'
import { clone } from 'lodash-es'
import { useI18n } from 'vue-i18n'
import { getArtistCoverUrl } from '~/utils/utils'

import axios from 'axios'
import useWebSocketHandler from '~/composables/useWebSocketHandler'

import PlayButton from '~/components/audio/PlayButton.vue'
import TagsList from '~/components/tags/List.vue'
import Section from '~/components/ui/Section.vue'
import Alert from '~/components/ui/Alert.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Loader from '~/components/ui/Loader.vue'
import Heading from '~/components/ui/Heading.vue'
import Pagination from '~/components/ui/Pagination.vue'

import useErrorHandler from '~/composables/useErrorHandler'

interface Events {
  (e: 'count', count: number): void
}

interface Props {
  filters: Record<string, string | boolean>
  url: string
  isActivity?: boolean
  limit?: number
  itemClasses?: string
  websocketHandlers?: string[]
  title?: string
}

const emit = defineEmits<Events>()
const props = withDefaults(defineProps<Props>(), {
  isActivity: true,
  limit: 9,
  itemClasses: '',
  websocketHandlers: () => [],
  title: undefined
})

const store = useStore()
const { t } = useI18n()

const objects = reactive([] as Listening[])
const count = ref(0)
const page = ref(1)

const isLoading = ref(false)

const fetchData = async (url = props.url) => {
  isLoading.value = true

  const params = {
    ...clone(props.filters),
    page: page.value,
    page_size: props.limit ?? 9
  }

  try {
    const response = await axios.get(url, { params })
    count.value = response.data.count

    const newObjects = !props.isActivity
      ? response.data.results.map((track: Track) => ({ track }))
      : response.data.results

    objects.splice(0, objects.length, ...newObjects)
  } catch (error) {
    useErrorHandler(error as Error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  setTimeout(fetchData, 1000)
})

watch(
  () => [store.state.moderation.lastUpdate, props.filters, page.value],
  () => fetchData(),
  { immediate: true }
)

watch(count, (to) => emit('count', to))

watch(() => props.websocketHandlers.includes('Listen'), (to) => {
  if (to) {
    useWebSocketHandler('Listen', (event: unknown) => {
      // Handle WebSocket events for "Listen"

      // Add the event to `objects` reactively
      objects.unshift(event as Listening)

      // Keep the array size within limits (e.g., remove the last item if needed)
      if (objects.length > props.limit) {
        objects.pop()
      }
    })
  }
}, { immediate: true })
</script>

<template>
  <Section
    align-left
    :h2="title"
    :columns-per-item="4"
  >
    <Loader
      v-if="isLoading"
      style="grid-column: 1 / -1;"
    />
    <Alert
      v-if="!isLoading && count === 0"
      style="grid-column: 1 / -1;"
      blue
      align-items="center"
    >
      <h4>
        <i class="bi bi-search" />
        {{ t('components.audio.track.Widget.empty.noResults') }}
      </h4>
    </Alert>
    <!-- TODO: Use activity.vue -->
    <div
      v-for="object in (count > 0 ? objects : [])"
      :key="object.id"
      class="funkwhale activity"
      :class="['item', itemClasses]"
    >
      <div class="activity-image">
        <img
          v-if="object.track?.album && object.track?.album.cover"
          v-lazy="store.getters['instance/absoluteUrl'](object.track.album.cover.urls.small_square_crop)"
          alt=""
        >
        <img
          v-else-if="object.track?.cover"
          v-lazy="store.getters['instance/absoluteUrl'](object.track.cover.urls.small_square_crop)"
          alt=""
        >
        <img
          v-else-if="object.track?.artist_credit && object.track.artist_credit.length > 1"
          v-lazy="getArtistCoverUrl(object.track.artist_credit)"
          alt=""
        >
        <i
          v-else
          class="bi bi-vinyl-fill"
        />
        <!-- TODO: Add Playbutton overlay -->
      </div>
      <div class="activity-content">
        <router-link
          class="funkwhale link artist"
          :to="{ name: 'library.tracks.detail', params: { id: object.track.id } }"
        >
          <Heading
            :h3="object.track.title"
            title
          />
        </router-link>
        <Spacer :size="2" />
        <div
          v-if="object.track.artist_credit"
          class="funkwhale link artist"
        >
          <span
            v-for="ac in object.track.artist_credit"
            :key="ac.artist.id"
          >
            <router-link
              class="discrete link"
              :to="{ name: 'library.artists.detail', params: { id: ac.artist.id } }"
            >
              {{ ac.credit }}
            </router-link>
            <span v-if="ac.joinphrase">{{ ac.joinphrase }}</span>
          </span>
        </div>
        <Spacer :size="8" />
        <TagsList
          label-classes="tiny"
          :truncate-size="20"
          :limit="2"
          :show-more="false"
          :tags="object.track.tags"
        />
        <Spacer :size="4" />
        <div
          v-if="isActivity"
          class="extra"
        >
          <router-link
            class="funkwhale link user"
            :to="{ name: 'profile.content', params: { username: object.actor.name } }"
          >
            <span class="at symbol" />{{ object.actor.name }}
          </router-link>
          <span class="right floated"><human-date :date="object.creation_date" /></span>
        </div>
      </div>
      <play-button
        :account="object.actor"
        :dropdown-only="true"
        :track="object.track"
        square-small
      />
    </div>
    <Pagination
      v-if="page && count > props.limit"
      v-model:page="page"
      :pages="Math.ceil((count || 0) / props.limit)"
      style="grid-column: 1 / -1;"
    />
  </Section>
</template>

<style lang="scss" scoped>
@use '~/style/funkwhale.scss';

.funkwhale {
  &.activity {
    padding-top: 14px;
    border-top: 1px solid;
    margin: -11px 0;

    @include funkwhale.light-theme {
      border-color: var(--fw-gray-300);
    }

    @include funkwhale.dark-theme {
      border-color: var(--fw-gray-800);
    }

    display: grid;
    grid-template-columns: auto 1fr auto;
    gap: 12px;
    grid-column: span 4;

    &:last-child {
      border-bottom: 1px solid;
    }

    >.activity-image {

      width: 40px;
      aspect-ratio: 1;
      overflow: hidden;
      border-radius: var(--fw-border-radius);

      >img {
        width: 100%;
        aspect-ratio: 1;
        object-fit: cover;
      }

      >i {
        font-size: 40px;
        line-height: 36px;
      }

      >.play-button {
        position: absolute;
        top: 0;
        left: 0;
        padding: 0 !important;
        width: 100%;
        aspect-ratio: 1;
        margin: 0;
        border: 0 !important;
        opacity: 0;
      }
    }

    &:hover {
      .play-button {
        opacity: 1;
      }
    }

    >.activity-content {

      a {
        text-decoration: none;
        color: var(--color);

        &:hover {
          text-decoration: underline;
        }
      }

      >.track-title {
        font-weight: 700;
        line-height: 1.5em;

        @include funkwhale.dark-theme {
          color: var(--fw-gray-300);
        }
      }

      .artist {
        font-size: 15px;
      }

      .user,
      time {
        line-height: 1.5em;
        font-size: 0.8125rem;
        color: var(--fw-gray-500);
      }
    }
  }
}

@include funkwhale.light-theme {

  .play-button {
    background: rgba(255, 255, 255, .5);

    &:hover {
      --fw-text-color: var(--fw-gray-800) !important;
    }
  }
}

@include funkwhale.dark-theme {

  .play-button {
    background: rgba(0, 0, 0, .2);

    &:hover {
      background: rgba(0, 0, 0, .8);
      --fw-text-color: var(--fw-gray-200) !important;
    }
  }
}
</style>
