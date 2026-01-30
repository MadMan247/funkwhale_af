<script setup lang="ts">
import type { paths, components } from '~/generated/types.ts'
// import type { RadioConfig } from '~/store/radios'

import axios from 'axios'
import { ref, computed, type ShallowRef, useTemplateRef, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { refDebounced, watchDebounced } from '@vueuse/core'
import { trim } from 'lodash-es'
import { vElementBounding } from '@vueuse/components'
import { useRouter } from 'vue-router'

import useErrorHandler from '~/composables/useErrorHandler'
import { useI18n } from 'vue-i18n'
import { useModal } from '~/ui/composables/useModal.ts'
import { useStore } from '~/store'
import { useDataStore, getKey } from '~/ui/stores/data'

import ArtistCard from '~/components/artist/Card.vue'
import PlaylistCard from '~/components/playlists/Card.vue'
import ChannelCard from '~/components/audio/ChannelCard.vue'
import ActorCard from '~/components/federation/ActorCard.vue'
import TrackTable from '~/components/audio/track/Table.vue'
import AlbumCard from '~/components/album/Card.vue'
import RadioCard from '~/components/radios/Card.vue'
import Button from '~/components/ui/Button.vue'
// import RadioButton from '~/components/radios/Button.vue'
import onKeyboardShortcut from '~/composables/onKeyboardShortcut'

import TagsList from '~/components/tags/List.vue'
import EmptyState from '~/components/common/EmptyState.vue'

import Modal from '~/components/ui/Modal.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Input from '~/components/ui/Input.vue'
import Card from '~/components/ui/Card.vue'
import Section from '~/components/ui/Section.vue'
import Loader from '~/components/ui/Loader.vue'
import Alert from '~/components/ui/Alert.vue'
import Pagination from '~/components/ui/Pagination.vue'

const { t } = useI18n()

const router = useRouter()

/*
  Future:
    - For now, we will use fetch-then-cache, and not support features such as search in
      offline-first. Later, we can add a UI indication for stale params, with the timestamp being old,
        and an automatic trigger: while user is still browsing the app, refresh content periodically.
        When tab gets focus, try to re-fetch.
*/
const dataStore = useDataStore()

// Search input sizing
const style = ref<{ inner: string, outer: string }>({ inner: '', outer: '' })

const setBoundingBox = (placeholder: 'inner' | 'outer') => ({ left, width, top }: { left: ShallowRef<number>, width: ShallowRef<number>, top: ShallowRef<number> }) => {
  style.value[placeholder] = `left: ${left.value}px; top: ${top.value}px; width: ${width.value}px;`
  }


const globalSearchInput = useTemplateRef('globalSearchInput')

const focusSearch = () => {
  globalSearchInput.value?.focus();
}

onKeyboardShortcut(['shift', 'f'], focusSearch, true)
onKeyboardShortcut(['ctrl', 'k'], focusSearch, true)
onKeyboardShortcut(['/'], focusSearch, true)

const { isOpen, value: query } = useModal(
  'search', {
    on: () => '',
    isOn: (value) => value !== undefined && value !== ''
})

// Search query

const queryDebounced = refDebounced(query, 400)
const trimmedQuery = computed(() => trim(trim(queryDebounced.value), '@'))
const isFetch = computed(() => ((trimmedQuery.value.startsWith('http://') || trimmedQuery.value.startsWith('https://')) || trimmedQuery.value.includes('@')) && !isRss.value)
const isRss = computed(() => trimmedQuery.value.includes('.rss') || trimmedQuery.value.includes('.xml'))

const isLoading = ref(false)

// RSS and Federation (remote object) search

type Category = 'rss' | 'federation'

type Response = {
  rss: paths['/api/v2/channels/rss-subscribe/']['post']['responses']['200']['content']['application/json'],
  federation: paths['/api/v2/federation/fetches/']['post']['responses']['201']['content']['application/json']
}

/** Note that `federation` is a singleton list so that each result is a list */
type Results = {
  rss: [Response['rss']],
  federation: [Response['federation']],
  type: Category
}

const responses = ref<Partial<Response>>({})
const results = ref<Partial<Results>>({})

const categories = computed(() => [
  {
    type: 'rss',
    label: t('views.Search.header.rss'),
    endpoint: '/channels/rss-subscribe/',
    post: true,
    params: {
      url: trimmedQuery.value
    }
  },
  {
    type: 'federation',
    label: t('views.Search.header.remote'),
    endpoint: '/federation/fetches/',
    post: true,
    params: {
      object_uri: trimmedQuery.value
    }
  }
] as const satisfies {
  type: Category
  label: string
  post?: true
  params?: {
    [key: string]: string | number
  }
  endpoint: `/${string}`
}[])

// Limit the available categories based on the search query
// Show fetch if the query is a URL; show RSS if the query is an email address; show all other cateories otherwise
const availableCategories = computed(() =>
  categories.value.filter(({ type }) =>
    isFetch.value ? type === 'federation'
      : isRss.value ? type === 'rss'
        : type !== 'federation' && type !== 'rss'
  ))

/**
 * Get a list of the loaded results for a given category (max. 4)
 * @param category The category to get the results for
 * @returns The results for the given category, in the form of an Array; `[]` if the category has not yet been queried
 */
const resultsPerCategory = <C extends Category>(category: { type: C }) =>
  results.value[category.type] || []

/**
 * Get the total number of results
 * @param category The category to get the results for
 * @returns The number of results for the given category according to the backend; `0` if the category has not yet been queried
 */
const count = <C extends Category>(category: { type: C }) => (
  response => response && 'count' in response ? response.count : resultsPerCategory(category).length
)(responses.value[category.type])

// Subscribe to an RSS feed

const store = useStore()

const rssError = ref()

/**
 * Subscribe to an RSS feed and return the route for the subscribed channel
 * @param url The RSS feed URL
 * @returns The route object for the subscribed channel
 */
const rssSubscribe = async (url: string) => {
  try {
    const response = await axios.post('channels/rss-subscribe/', { url })
    store.commit('channels/subscriptions', { uuid: response.data.channel.uuid, value: true })
    return response.data.channel
  } catch (error) {
    //@ts-expect-error TODO: type this correctly
    rssError.value=[error.message, ...error.backendErrors].join(' – ')
    useErrorHandler(error as Error)
    return null
  }
}

// Federated Search

const federationError = ref()

const search = async () => {
  // We are searching for RSS or for federated objects only. Fetches for other objects are handled by rstore.
  // TODO: Now that we use imperative axios calls only for the POST operations, the abstraction
  // into a list makes no sense any more. We'll see how the backend develops (GET for rss and fetches),
  // and the rstore plugin will support POST, PATCH etc. at some point
  if (availableCategories.value.length == 0) return;

  // Close if query is empty
  if (trimmedQuery.value.length < 1) {
    isOpen.value = false
    return
  }

  // Only query category that are open / available. Omit duplicate queries (`uniqBy`).

  isLoading.value = true

  for (const category of availableCategories.value) {
    try {
        // TODO: add (@)type key to Response type
        if (category.type === 'rss') {
          const channel = await rssSubscribe(trimmedQuery.value)
          if (channel) {
            results.value.rss = [channel] // Store the subscribed channel
          }
        } else if (category.type === 'federation') {
          const response = await axios.post<Response['federation']>(
            category.endpoint,
            { object_uri: trimmedQuery.value }
          )
          results.value.type = category.type
          results.value.federation = [response.data]
          responses.value[category.type] = response.data

          // Interesting: If a federation url is empty, the request returns the local user, but with status errored.

          if (response.data.status === 'errored') {
            //@ts-expect-error TODO: type this correctly
            federationError.value=response?.data?.detail?.message
          }
        }
    } catch (error) {
      //@ts-expect-error TODO: type this correctly
      federationError.value=[error?.message, ...(error?.backendErrors || [])].join(' – ')
      useErrorHandler(error as Error)
    }

  }
  isLoading.value = false
}

// Global loading that includes federated/rss search and store-level fetches
const globalLoading = computed(() => {
  const storeLoading = (dataStore as any).isLoading?.value ?? (dataStore as any).isLoading
  const activeFetches = (dataStore as any).activeFetches?.value ?? (dataStore as any).activeFetches
  return isLoading.value || Boolean(storeLoading) || Boolean(activeFetches?.length > 0)
})

// Count visible sections by observing rendered DOM nodes with the `search-section` class.
const visibleSections = ref(0)
let sectionObserver: MutationObserver | null = null

const updateVisibleSections = async () => {
  await nextTick()
  try {
    const nodes = Array.from(document.querySelectorAll('.search-section')) as HTMLElement[]
    const visible = nodes.filter(n => n.offsetParent !== null || n.getClientRects().length > 0).length
    visibleSections.value = visible
  } catch (e) {
    // ignore
  }
}

onMounted(() => {
  updateVisibleSections()
  sectionObserver = new MutationObserver(() => updateVisibleSections())
  sectionObserver.observe(document.body, { childList: true, subtree: true })
})

onUnmounted(() => {
  sectionObserver?.disconnect()
  sectionObserver = null
})

// also update when the search query or global loading changes
watch([queryDebounced], () => updateVisibleSections())
watch([() => globalLoading.value], () => updateVisibleSections())

// Configure the radio

// TODO: Re-activate radio (but for all types at the same time) after #2467 (radio builder) is done

// const radioConfig = computed<RadioConfig | null>(() =>
//   count({ type: 'tags' }) > 0
//     ? ({
//       type: 'tag',
//       names: resultsPerCategory({ type: 'tags' })
//         .map((({ name }) => name))
//     })
//     : count({ type: 'playlists' }) > 0
//       ? ({
//           type: 'playlist',
//           ids: resultsPerCategory({ type: 'playlists' }).map(({ uuid }) => uuid.toString())
//         })
//       : count({ type: 'artists' }) > 0
//         ? ({
//           type: 'artist',
//           ids: resultsPerCategory({ type: 'artists' }).map(({ id }) => id.toString())
//         })
//         : null
// )

// Start the search

watchDebounced(queryDebounced, search, {
  debounce: 1000, maxWait: 10000, immediate: true
})

// Pagination
const artistsPage = ref(1)
const albumsPage = ref(1)
const tracksPage = ref(1)
const tagsPage = ref(1)
const playlistsPage = ref(1)
const radiosPage = ref(1)
const podcastsPage = ref(1)
const seriesPage = ref(1)

// Reset all pagination pages to 1 when the trimmed query changes
watchDebounced(trimmedQuery, () => {
  artistsPage.value = 1
  albumsPage.value = 1
  tracksPage.value = 1
  tagsPage.value = 1
  playlistsPage.value = 1
  radiosPage.value = 1
  podcastsPage.value = 1
  seriesPage.value = 1
}, { debounce: 50 })
</script>

<template>
  <div
    v-element-bounding="[setBoundingBox('outer'), { updateTiming: 'sync', immediate: true }]"
    :class="[$style.placeholder, 'secondary raised interactive solid']"
  />
  <Modal
    v-model="isOpen"
    autofocus="off"
    title=""
    maximize-size
    :priority="12"
  >
    <template #topleft>
      <!-- The following is a placeholder for the original input element and contributes only its position and dimensions -->
      <div
        v-element-bounding="[setBoundingBox('inner'), { updateTiming: 'sync', immediate: true }]"
        :class="[$style.placeholder, 'secondary raised interactive solid']"
        style="opacity: 0; position: relative; top: -4px;"
      />
      <!-- Radio button placeholder (disabled for now) -->
      <!-- <RadioButton
        v-if="radioConfig"
        class="ui right floated medium button"
        type="custom_multiple"
        :radio-config="radioConfig"
      /> -->
    </template>

    <template
      v-if="isFetch"
      #default
    >
      <Spacer size-32 />
      <Section
        class="search-section"
        :columns-per-item="3"
        align-left
      >
        <Card
          full
          red
          :title="t('views.Search.header.remote')"
        >
          <template
            v-if="federationError"
            #alert
          >
            {{ federationError }}
          </template>
          <Loader v-if="isLoading" />
          <EmptyState
            v-else-if="count({type: 'federation'}) === 0"
            :refresh="true"
            @refresh="search"
          />
        </Card>
        <template
          v-for="result in resultsPerCategory({type: 'federation'})"
          :key="result.id"
        >
          <!-- TODO: use a different endpoint for remote user search with FullActor to get user avatars -->
          <ActorCard
            v-if="result.object && result.type === 'account'"
            :actor="result.object as components['schemas']['Actor']"
          />
          <ChannelCard
            v-else-if="result.object && result.type === 'channel'"
            :object="result.object as components['schemas']['Channel']"
          />
          <ArtistCard
            v-else-if="result.object && result.type === 'artist'"
            :artist="result.object as components['schemas']['Artist']"
          />
          <AlbumCard
            v-else-if="result.object && result.type === 'album'"
            :album="result.object as components['schemas']['Album']"
          />
          <PlaylistCard
            v-else-if="result.object && result.type === 'playlist'"
            :playlist="result.object as components['schemas']['Playlist']"
          />
          <TrackTable
            v-else-if="result.object && result.type === 'track'"
            :tracks="[result.object] as components['schemas']['Track'][]"
          />
        </template>
      </Section>
    </template>
    <template
      v-else-if="isRss"
      #default
    >
      <channel-card
        v-if="results.rss && results.rss[0]"
        :key="results.rss[0].uuid"
        :object="results.rss[0]"
      />
      <Card
        v-if="rssError"
        full
        red
        :title="t('views.Search.header.rss')"
      >
        <template #alert>
          {{ rssError }}
        </template>
      </Card>
    </template>
    <template
      v-else
      #default="{ columns, cardsPerRow }"
    >
      <Spacer size-32 />

      <!-- DEBUG: CACHE -->

      <!-- <pre :key="allCaches.map(m=>Array.from(m).join('')).join('')">
      {{ allCaches[0] }}
      </pre> -->


      <!-- Artists -->

      <template
        v-for="{ value: { status, data, error, key } } in [dataStore.artists({
          q: query,
          page: 1,
          page_size: cardsPerRow() * 2 - 2,
        })]"
        :key
      >
        <Section
          v-if="(data?.results.length ?? 0) > 0"
          class="search-section"
          icon="bi-person"
          :h1="t('artists', data?.results.length || 0)"
          :columns-per-item="3"
          align-left
        >
          <Loader
            v-if="status === 'loading'"
          />

          <Alert
            v-if="status === 'error'"
            red
            style="grid-column: 1 / -1;"
          >
            {{ error }}
          </Alert>

          <ArtistCard
            v-for="(artist) in data?.results"
            :key="getKey(artist)"
            :artist
          />

          <Button
            secondary
            icon="bi-search"
            @click="router.push({ name: 'library.artists.browse', query: { query } })"
          >
            {{ t('views.Search.label.artists') }}
          </Button>

          <Pagination
            v-if="(data?.results.length ?? 0) > (cardsPerRow() * 2 - 2)"
            v-model:page="artistsPage"
            style="grid-column: 1 / -1;"
            :pages="Math.ceil((data?.results.length ?? 0) / (cardsPerRow() * 2 - 2))"
          />
        </Section>
        <Spacer
          v-if="(data?.results.length ?? 0) > 0"
          size-64
        />
      </template>

      <!-- Albums -->

      <template
        v-for="{ value: { status, data, error, key } } in [dataStore.albums({
          q: query,
          page: 1,
          page_size: cardsPerRow() * 2 - 2,
          include_tracks: false
        })]"
        :key
      >
        <Section
          v-if="(data?.results.length ?? 0) > 0"
          class="search-section"
          icon="bi-disc"
          :h1="t('albums', data?.results.length || 0)"
          :columns-per-item="3"
          align-left
        >
          <Alert
            v-if="status === 'error'"
            red
            style="grid-column: 1 / -1;"
          >
            {{ error }}
          </Alert>
          <Loader v-if="status === 'loading'" />

          <AlbumCard
            v-for="(album) in data?.results"
            :key="getKey(album)"
            :album
          />

          <Button
            secondary
            icon="bi-search"
            @click="router.push({ name: 'library.albums.browse', query: { query } })"
          >
            {{ t('views.Search.label.albums') }}
          </Button>

          <Pagination
            v-if="(data?.results.length ?? 0) > (cardsPerRow() * 2 - 2)"
            v-model:page="albumsPage"
            style="grid-column: 1 / -1;"
            :pages="Math.ceil((data?.results.length ?? 0) / (cardsPerRow() * 2 - 2))"
          />
        </Section>
        <Spacer
          v-if="(data?.results.length ?? 0) > 0"
          size-64
        />
      </template>



      <!-- Tracks -->

      <template
        v-for="{ value: { status, data, error, key } } in [dataStore.tracks({
          q: query,
          page: 1,
          page_size: cardsPerRow() * 2 - 2,
        })]"
        :key
      >
        <Section
          v-if="(data?.results.length ?? 0) > 0"
          class="search-section"
          icon="bi-music-note-beamed"
          :h1="t('tracks', data?.results.length || 0)"
          :columns-per-item="3"
          align-left
        >
          <Alert
            v-if="status =='error'"
            red
            style="grid-column: 1 / -1;"
          >
            {{ error }}
          </Alert>
          <Loader
            v-if="status === 'loading'"
            :container="false"
          />

          <TrackTable
            :tracks="data?.results"
            :style="`grid-column: 1 / -1`"
          />

          <Pagination
            v-if="(data?.results.length ?? 0) > (cardsPerRow() * 2 - 2)"
            v-model:page="tracksPage"
            style="grid-column: 1 / -1;"
            :pages="Math.ceil((data?.results.length ?? 0) / (cardsPerRow() * 2 - 2))"
          />
        </Section>
        <Spacer
          v-if="(data?.results.length ?? 0) > 0"
          size-64
        />
      </template>


      <!-- Tags -->

      <template
        v-for="{ value: { status, data, error, key } } in [dataStore.tags_({
          q: query,
          page: 1,
          page_size: 20,
        })]"
        :key
      >
        <Section
          v-if="(data?.results.length ?? 0) > 0"
          class="search-section"
          icon="bi-tags"
          :h1="t('tags', data?.results.length || 0)"
          :columns-per-item="3"
          align-left
        >
          <Alert
            v-if="status === 'error'"
            red
            style="grid-column: 1 / -1;"
          >
            {{ error }}
          </Alert>
          <Loader v-if="status === 'loading'" />

          <TagsList
            :style="`grid-column: ${columns > 3 ? 4 : 1} / -1`"
            :truncate-size="200"
            :limit="20"
            :tags="data?.results?.map(t => t.name) || []"
          />

          <Button
            secondary
            icon="bi-search"
            @click="router.push({ name: 'library.tags.browse', query: { query } })"
          >
            {{ t('views.Search.label.tags') }}
          </Button>

          <Pagination
            v-if="(data?.results.length ?? 0) > (cardsPerRow() * 2 - 2)"
            v-model:page="tagsPage"
            style="grid-column: 1 / -1;"
            :pages="Math.ceil((data?.results.length ?? 0) / (cardsPerRow() * 2 - 2))"
          />
        </Section>
        <Spacer
          v-if="(data?.results.length ?? 0) > 0"
          size-64
        />
      </template>

      <!-- Playlists -->

      <template
        v-for="{ value: { status, data, error, key } } in [dataStore.playlists({
          q: query,
          page: 1,
          page_size: cardsPerRow() * 2 - 2,
        })]"
        :key
      >
        <Section
          v-if="(data?.results.length ?? 0) > 0"
          class="search-section"
          icon="bi-music-note-list"
          :h1="t('playlists', data?.results.length || 0)"
          :columns-per-item="3"
          align-left
        >
          <Alert
            v-if="error"
            red
            style="grid-column: 1 / -1;"
          >
            {{ error }}
          </Alert>
          <Loader v-if="status === 'loading'" />
          <PlaylistCard
            v-for="(playlist) in data?.results || []"
            :key="getKey(playlist)"
            :playlist
          />

          <Button
            secondary
            icon="bi-search"
            @click="router.push({ name: 'library.playlists.browse', query: { query } })"
          >
            {{ t('views.Search.label.playlists') }}
          </Button>

          <Pagination
            v-if="(data?.results.length ?? 0) > (cardsPerRow() * 2 - 2)"
            v-model:page="playlistsPage"
            style="grid-column: 1 / -1;"
            :pages="Math.ceil((data?.results.length ?? 0) / (cardsPerRow() * 2 - 2))"
          />
        </Section>
        <Spacer
          v-if="(data?.results.length ?? 0) > 0"
          size-64
        />
      </template>

      <!-- Radios -->

      <template
        v-for="{ value: { status, data, error, key } } in [dataStore.radios({
          q: query,
          page: 1,
          page_size: cardsPerRow() * 2 - 2,
        })]"
        :key
      >
        <Section
          v-if="(data?.results.length ?? 0) > 0"
          class="search-section"
          icon="bi-boombox-fill"
          :h1="t('radios', data?.results.length || 0)"
          :columns-per-item="3"
          align-left
        >
          <Alert
            v-if="error"
            red
            style="grid-column: 1 / -1;"
          >
            {{ error }}
          </Alert>
          <Loader v-if="status === 'loading'" />

          <RadioCard
            v-for="(radio) in data?.results || []"
            :key="getKey(radio)"
            type="custom"
            :custom-radio="radio"
          />

          <Pagination
            v-if="(data?.results.length ?? 0) > (cardsPerRow() * 2 - 2)"
            v-model:page="radiosPage"
            style="grid-column: 1 / -1;"
            :pages="Math.ceil((data?.results.length ?? 0) / (cardsPerRow() * 2 - 2))"
          />

          <Button
            secondary
            icon="bi-search"
            @click="router.push({ name: 'library.radios.browse', query: { query } })"
          >
            {{ t('views.Search.label.radios') }}
          </Button>
        </Section>
        <Spacer
          v-if="(data?.results.length ?? 0) > 0"
          size-64
        />
      </template>

      <!-- Podcasts -->

      <template
        v-for="{ value: { status, data, error, key } } in [dataStore.artists({
          q: query,
          content_category: 'podcast',
          include_channels: true,
          page: 1,
          page_size: cardsPerRow() * 2 - 2,
        })]"
        :key
      >
        <Section
          v-if="(data?.results.length ?? 0) > 0"
          class="search-section"
          icon="bi-boombox-fill"
          :h1="t('podcasts', data?.results.length || 0)"
          :columns-per-item="3"
          align-left
        >
          <Alert
            v-if="error"
            red
            style="grid-column: 1 / -1;"
          >
            {{ error }}
          </Alert>
          <Loader v-if="status === 'loading'" />

          <ArtistCard
            v-for="(artist) in data?.results"
            :key="getKey(artist)"
            :artist
          />

          <Button
            secondary
            icon="bi-search"
            @click="router.push({ name: 'library.podcasts.browse', query: { query } })"
          >
            {{ t('views.Search.label.podcasts') }}
          </Button>

          <Pagination
            v-if="(data?.results.length ?? 0) > (cardsPerRow() * 2 - 2)"
            v-model:page="podcastsPage"
            style="grid-column: 1 / -1;"
            :pages="Math.ceil((data?.results.length ?? 0) / (cardsPerRow() * 2 - 2))"
          />
        </Section>
        <Spacer
          v-if="(data?.results.length ?? 0) > 0"
          size-64
        />
      </template>

      <!-- Series -->

      <template
        v-for="{ value: { status, data, error, key } } in [dataStore.albums({
          q: query,
          content_category: 'podcast',
          include_channels: true,
          page: 1,
          page_size: cardsPerRow() * 2 - 2,
        })]"
        :key
      >
        <Section
          v-if="(data?.results.length ?? 0) > 0"
          class="search-section"
          :h1="t('podcast series', data?.results.length || 0)"
          icon="bi-collection-play"
          :columns-per-item="3"
          align-left
        >
          <Alert
            v-if="error"
            red
            style="grid-column: 1 / -1;"
          >
            {{ error }}
          </Alert>
          <Loader v-if="status === 'loading'" />

          <AlbumCard
            v-for="(album) in data?.results"
            :key="getKey(album)"
            :album
          />

          <Pagination
            v-if="(data?.results.length ?? 0) > (cardsPerRow() * 2 - 2)"
            v-model:page="seriesPage"
            style="grid-column: 1 / -1;"
            :pages="Math.ceil((data?.results.length ?? 0) / (cardsPerRow() * 2 - 2))"
          />
        </Section>
        <Spacer
          v-if="(data?.results.length ?? 0) > 0"
          size-64
        />
      </template>
      <template v-if="globalLoading">
        <Spacer size-64 />
        <Loader :container="false" />
      </template>
      <template v-if="visibleSections === 0">
        <EmptyState
          :refresh="true"
          @refresh="search"
        />
      </template>
    </template>
  </Modal>

  <Teleport to="body">
    <div
      :style="isOpen ? style.inner : style.outer"
      :class="[$style.input, 'solid secondary']"
    >
      <Input
        ref="globalSearchInput"
        v-model="query"
        raised
        autocomplete="search"
        type="search"
        icon="bi-search"
        :placeholder="t('components.audio.SearchBar.placeholder.search')"
        :autofocus="isOpen || undefined"
      />
    </div>
  </Teleport>
</template>

<style module>
.placeholder {
    position: relative;
    top: 0;
    flex-grow: 1;
    border: none;
    border-radius: 8px;
    height: 48px;
    flex-shrink: 0;
    opacity: .2;
    transition: all .2s;
}
.input.input.input {
    height: 48px;
    z-index: v-bind("isOpen ? 99999 : 0");
    position: fixed;
    &> * {
        z-index: 99999;
    }
    transition: width .2s, top .3s, left .4s;
}
</style>
