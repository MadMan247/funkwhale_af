<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import { useI18n } from 'vue-i18n'
import PlayButton from '~/components/audio/PlayButton.vue'
import TagsList from '~/components/tags/List.vue'
import useWebSocketHandler from '~/composables/useWebSocketHandler'
import type { operations } from '~/generated/types'
import { useStore } from '~/store'
import type { Listening } from '~/types'
import { useDataStore } from '~/ui/stores/data'
import { getArtistCoverUrl } from '~/utils/utils'

import Alert from '~/components/ui/Alert.vue'
import Heading from '~/components/ui/Heading.vue'
import Loader from '~/components/ui/Loader.vue'
import Pagination from '~/components/ui/Pagination.vue'
import Section from '~/components/ui/Section.vue'
import Spacer from '~/components/ui/Spacer.vue'

const store = useStore()
const { t } = useI18n()

// TODO: @count is only used once. Consider simplifying the logic.
const emit = defineEmits<{
  (e: 'count', count: number): void
}>()

// TODO: Make type stricter (exclusive over TUrl) once Vue supports full typing of props
const { title, isActivity=true, url, websocketHandlers = [], itemClasses, query } = defineProps<{
  isActivity?: boolean,
  itemClasses?: string,
  websocketHandlers?: string[]
  url: 'favorites/tracks' | 'history/listenings'
  title?: string
  query: Required<(operations['get_history_listenings' | 'get_favorite_tracks']['parameters'])>['query']
} >()

const page = ref(1)

const listenings = ref<Listening[]>([]);

const tracks = computed(() => useDataStore()[url]({
  page_size: 9,
  page: page.value,
  ...query
}, {
  refetchSignal: store.state.moderation.lastUpdate
}).value)

// Emit updates to `count`
watch(tracks, ({ data }) => {
  if (data) emit('count', data.count)
})

watch(() => websocketHandlers.includes('Listen'), isIncluded => {
  if (isIncluded)
    useWebSocketHandler('Listen', (event: unknown) => {
      // Add the event to `listenings` reactively
      // TODO: Replace `as Listening` with type-safe event parser
      // Fields in Listening: { id, actor, track }
      listenings.value.unshift(event as Listening)
    })
}, { immediate: true })

// Combine listenings into a single array, limited to length `page_size`
const objects = computed(() => [
  ...listenings.value,
  ...(tracks.value.data?.results ?? [])
].slice(0, query.page_size ?? 9))
</script>

<template>
  <Section
    align-left
    :h2="title"
    :columns-per-item="4"
  >
    <Loader
      v-if="tracks.status === 'loading'"
      style="grid-column: 1 / -1;"
    />
    <!-- TODO: When counting, do we want to include the listenings inserted by the websocketHandler? -->
    <Alert
      v-else-if="tracks.data?.count === 0"
      style="grid-column: 1 / -1;"
      blue
      align-items="center"
    >
      <h4>
        <i class="bi bi-search" />
        {{ t('components.audio.track.Widget.empty.noResults') }}
      </h4>
    </Alert>

    <!-- TODO: Use Activity.vue -->
    <template v-if="objects">
      <div
        v-for="{ fid, track, creation_date, actor } in objects"
        :key="fid"
        class="funkwhale activity"
        :class="['item', itemClasses]"
      >
        <div class="activity-image">
          <img
            v-if="track.album && track.album.cover"
            v-lazy="store.getters['instance/absoluteUrl'](track.album.cover.urls.small_square_crop)"
            alt=""
          >
          <img
            v-else-if="track.cover"
            v-lazy="store.getters['instance/absoluteUrl'](track.cover.urls.small_square_crop)"
            alt=""
          >
          <img
            v-else-if="track.artist_credit && track.artist_credit.length > 1"
            v-lazy="getArtistCoverUrl(track.artist_credit)"
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
            :to="{ name: 'library.tracks.detail', params: { id: track.id } }"
          >
            <Heading
              :h3="track.title"
              title
            />
          </router-link>
          <Spacer :size="2" />
          <div
            v-if="track.artist_credit"
            class="funkwhale link artist"
          >
            <span
              v-for="ac in track.artist_credit"
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
            :tags="track.tags"
          />
          <Spacer :size="4" />
          <div
            v-if="isActivity"
            class="extra"
          >
            <router-link
              v-if="actor"
              class="funkwhale link user"
              :to="{ name: 'profile.content', params: { username: actor.name } }"
            >
              <span class="at symbol" />{{ actor.name }}
            </router-link>
            <span class="right floated"><human-date :date="creation_date" /></span>
          </div>
        </div>
        <play-button
          :account="actor"
          :dropdown-only="true"
          :track="track"
          square-small
        />
      </div>
      <template v-if="tracks.data">
        <Pagination
          v-if="tracks.data.count > (query.page_size ?? 9)"
          v-model:page="page"
          :pages="Math.ceil(tracks.data.count / (query.page_size ?? 9))"
          style="grid-column: 1 / -1;"
        />
      </template>
    </template>
  </Section>
</template>

<style lang="scss" scoped>
@use '~/style/funkwhale.scss';

// TODO: Remove style once we use the Activity UI component

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
