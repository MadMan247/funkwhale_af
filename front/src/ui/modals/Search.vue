<script setup lang="ts">
import type { paths, components } from '~/generated/types.ts'
import type { RadioConfig } from '~/store/radios'
import axios from 'axios'
import { ref, watch, computed } from 'vue'
import { refDebounced } from '@vueuse/core'
import { trim, uniqBy } from 'lodash-es'

import useErrorHandler from '~/composables/useErrorHandler'
import { useI18n } from 'vue-i18n'
import { useModal } from '~/ui/composables/useModal.ts'
import { useStore } from '~/store'

import ArtistCard from '~/components/artist/Card.vue'
import PlaylistCard from '~/components/playlists/Card.vue'
import ChannelCard from '~/components/audio/ChannelCard.vue'
import ActorLink from '~/components/common/ActorLink.vue'
import TrackTable from '~/components/audio/track/Table.vue'
import AlbumCard from '~/components/album/Card.vue'
import RadioCard from '~/components/radios/Card.vue'
import RadioButton from '~/components/radios/Button.vue'
import TagsList from '~/components/tags/List.vue'

import Modal from '~/components/ui/Modal.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Input from '~/components/ui/Input.vue'
import Section from '~/components/ui/Section.vue'
import Link from '~/components/ui/Link.vue'
import Loader from '~/components/ui/Loader.vue'
import Alert from '~/components/ui/Alert.vue'
import EmptyState from '~/components/common/EmptyState.vue'

const { t } = useI18n()

const { isOpen, value: query } = useModal(
  'search', {
    on: () => '',
    isOn: (value) => value !== undefined && value !== ''
})

// TODO:
// - Limit search results to 4
// - Add Link to specific search pages in each section where it applies
// - Read out the count from `result` (instead of the max. 4 visible results)

/*

- Categories (an Array of all categories) <- static configuration
  |
  | filter according to search query
  v
- Available Categories (also an Array of category configs)
  |
  | make sure that `open sections` is a
  | subset of available category types
  |
* Open Sections (a Set of category types)    <- user can expand/collapse sections
  |                                          <- new results can also open a category:
  |                                             if all were closed or none had results
  v
- Open Categories (this value is just computed, based on open sections)

*/

// Search query

const queryDebounced = refDebounced(query, 500)
const trimmedQuery = computed(() => trim(trim(queryDebounced.value), '@'))
const isFetch = computed(() => ((trimmedQuery.value.startsWith('http://') || trimmedQuery.value.startsWith('https://')) || trimmedQuery.value.includes('@')) && !isRss.value)
const isRss = computed(() => trimmedQuery.value.includes('.rss') || trimmedQuery.value.includes('.xml'))

const isLoading = ref(false)

// Filter

type Category = 'artists' | 'albums' | 'tracks' | 'playlists' | 'tags' | 'radios' | 'podcasts' | 'series' | 'rss' | 'federation'

type SearchResponse = paths['/api/v2/search']['get']['responses']['200']['content']['application/json']

type Response = {
  artists: SearchResponse,
  albums: SearchResponse,
  tracks: SearchResponse,
  tags: SearchResponse,
  playlists: paths['/api/v2/playlists/']['get']['responses']['200']['content']['application/json'],
  radios: paths['/api/v2/radios/radios/']['get']['responses']['200']['content']['application/json'],
  podcasts: paths['/api/v2/artists/']['get']['responses']['200']['content']['application/json'],
  series: paths['/api/v2/albums/']['get']['responses']['200']['content']['application/json'],
  rss: paths['/api/v2/channels/rss-subscribe/']['post']['responses']['200']['content']['application/json'],
  federation: paths['/api/v2/federation/fetches/']['post']['responses']['201']['content']['application/json']
}

/** Note that `federation` is a singleton list so that each result is a list */
type Results = {
  artists: SearchResponse['artists'],
  albums: SearchResponse['albums'],
  tracks: SearchResponse['tracks'],
  tags: SearchResponse['tags'],
  playlists: Response['playlists']['results'],
  radios: Response['radios']['results'],
  podcasts: Response['podcasts']['results'],
  series: Response['series']['results'],
  rss: [Response['rss']],
  federation: [Response['federation']],
  type: Category
}

const responses = ref<Partial<Response>>({})
const results = ref<Partial<Results>>({})

const categories = computed(() => [
  {
    type: 'artists',
    label: t('views.Search.label.artists'),
    more: '/library/artists',
    endpoint: '/search',
    params: {
      contentCategory: 'music',
      includeChannels: 'true',
      page: 1,
      page_size: 4
    }
  },
  {
    type: 'albums',
    label: t('views.Search.label.albums'),
    more: '/library/albums',
    endpoint: '/search',
    params: {
      contentCategory: 'music',
      includeChannels: 'true',
      page: 1,
      page_size: 4
    }
  },
  {
    type: 'tracks',
    label: t('views.Search.label.tracks'),
    endpoint: '/search',
    params: {
      page: 1,
      page_size: 24
    }
  },
  {
    type: 'tags',
    label: t('views.Search.label.tags'),
    endpoint: '/search',
    params: {
      page: 1,
      page_size: 24
    }
  },
  {
    type: 'playlists',
    label: t('views.Search.label.playlists'),
    more: '/library/playlists/',
    endpoint: '/playlists'
  },
  {
    type: 'radios',
    label: t('views.Search.label.radios'),
    more: '/library/radios',
    endpoint: '/radios/radios/',
    params: {
      page: 1,
      page_size: 4
    }
  },
  {
    type: 'podcasts',
    label: t('views.Search.label.podcasts'),
    more: '/library/podcasts',
    endpoint: '/artists/',
    params: {
      contentCategory: 'podcast',
      includeChannels: 'true',
      page: 1,
      page_size: 4
    }
  },
  {
    type: 'series',
    label: t('views.Search.label.series'),
    endpoint: '/albums/',
    params: {
      contentCategory: 'podcast',
      includeChannels: 'true',
      page: 1,
      page_size: 4
    }
  },
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
  more?: string
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
  )
)

// Whenever available categories change, if there is exactly one, open it
watch(availableCategories, () => {
  if (availableCategories.value.length === 1)
    openSections.value = new Set(availableCategories.value.map(category => category.type))
})

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

/**
 * Find out whether a category has been queried before
 * @param category The category to which may have been queried
 */
const isCategoryQueried = <C extends Category>(category: { type: C }) =>
  results.value[category.type] ? true : false

// Display

const openCategories = computed(() =>
  categories.value.filter(({ type }) => openSections.value.has(type))
)

// Sections can be manually or automatically toggled

const openSections = ref<Set<Category>>(new Set())

/**
 * If no results are in currently expanded categories but some collapsed have results, show those
*/
watch(results, () => {
  if (openCategories.value.some(category => count(category) > 0)) return

  const categoriesWithResults
    = availableCategories.value.filter(category => count(category) > 0)

  if (categoriesWithResults.length === 0) return

  openSections.value = new Set(categoriesWithResults.map(({ type }) => type))
})

// Subscribe to an RSS feed

const store = useStore()

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
    useErrorHandler(error as Error)
    return null
  }
}

// Search

const search = async () => {

  // Close if query is empty
  if (trimmedQuery.value.length < 1) {
    isOpen.value = false
    return
  }

  const params = new URLSearchParams({
    q: queryDebounced.value,
    ...(openCategories.value && 'params' in openCategories.value && openCategories.value.params
      ? openCategories.value.params
      : {}
    )
  })

  // Only query category that are open / available. Omit duplicate queries (`uniqBy`).
  const categories
    = uniqBy(
      openCategories.value.length > 0
        ? openCategories.value
        : availableCategories.value,
      (category => category.endpoint + ('params' in category && JSON.stringify(category.params)))
    )

  isLoading.value = true

  for (const category of categories) {
    try {
      if (category.endpoint === '/search') {
        const response = await axios.get<Response[typeof category.type]>(
          category.endpoint,
          { params }
        )
        // Store the four search results
        results.value = {
          ...results.value,
          ...response.data
        }
        responses.value[category.type] = response.data
      } else {
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
        } else if (category.type === 'playlists') {
          const response = await axios.get<Response['playlists']>(
            category.endpoint,
            { params }
          )
          results.value.type = category.type
          results.value.playlists = response.data.results
          responses.value[category.type] = response.data
        } else if (category.type === 'podcasts') {
          const response = await axios.get<Response['podcasts']>(
            category.endpoint,
            { params }
          )
          results.value.type = category.type
          results.value.podcasts = response.data.results
          responses.value[category.type] = response.data
        } else if (category.type === 'radios') {
          const response = await axios.get<Response['radios']>(
            category.endpoint,
            { params }
          )
          results.value.type = category.type
          results.value.radios = response.data.results
          responses.value[category.type] = response.data
        } else if (category.type === 'series') {
          const response = await axios.get<Response['series']>(
            category.endpoint,
            { params }
          )
          results.value.type = category.type
          results.value.series = response.data.results
          responses.value[category.type] = response.data
        }
      }
    } catch (error) {
      useErrorHandler(error as Error)
    }

  }
  isLoading.value = false
}

// Configure the radio

const radioConfig = computed<RadioConfig | null>(() =>
  count({ type: 'tags' }) > 0
    ? ({
      type: 'tag',
      names: resultsPerCategory({ type: 'tags' })
        .map((({ name }) => name))
    })
    : count({ type: 'playlists' }) > 0
      ? ({
          type: 'playlist',
          ids: resultsPerCategory({ type: 'playlists' }).map(({ uuid }) => uuid.toString())
        })
      : count({ type: 'artists' }) > 0
        ? ({
          type: 'artist',
          ids: resultsPerCategory({ type: 'artists' }).map(({ id }) => id.toString())
        })
        : null
)

// Start the search

watch(queryDebounced, search, { immediate: true })
</script>

<template>
  <Modal
    v-model="isOpen"
    over-popover
    autofocus="off"
    title=""
  >
    <template #topleft>
      <Input
        v-model="query"
        raised
        :autofocus="openCategories.length===0"
        icon="bi-search"
      />
      <RadioButton
        v-if="radioConfig"
        class="ui right floated medium button"
        type="custom_multiple"
        :radio-config="radioConfig"
      />
    </template>
    <Spacer />

    <Loader
      v-if="isLoading"
    />

    <template
      v-for="category in availableCategories"
      :key="category.type + isCategoryQueried(category)"
    >
      <Section
        align-left
        :columns-per-item="1"
        :h3="`${
          !isCategoryQueried(category)
            ? '...'
            : count(category) > 0
              ? `${count(category)} `
              : ''
        }${category.label}`"
        v-bind="
          openSections.has(category.type)
            ? ({ collapse: () => openSections.delete(category.type) })
            : ({ expand: () => openSections.add(category.type) })
        "
      >
        <!-- Categories that have one list-style item -->

        <TrackTable
          v-if="category.type === 'tracks'"
          style="grid-column: 1 / -1"
          :tracks="resultsPerCategory(category)"
        />
        <TagsList
          v-else-if="category.type === 'tags'"
          style="grid-column: 1 / -1"
          :truncate-size="200"
          :limit="category.params.page_size"
          :tags="(resultsPerCategory(category)).map(t => t.name)"
        />

        <!-- Categories that show individual cards -->
        <template
          v-for="(_, index) in (resultsPerCategory(category))"
          :key="category.type + index"
        >
          <ArtistCard
            v-if="(category.type === 'artists' || category.type === 'podcasts')"
            :artist="resultsPerCategory(category)[index]"
          />

          <AlbumCard
            v-else-if="category.type === 'albums' || category.type === 'series'"
            :album="resultsPerCategory(category)[index]"
          />

          <PlaylistCard
            v-else-if="category.type === 'playlists'"
            :playlist="resultsPerCategory(category)[index]"
          />

          <RadioCard
            v-else-if="category.type === 'radios'"
            type="custom"
            :custom-radio="resultsPerCategory(category)[index]"
          />
        </template>

        <template v-if="category.type === 'rss' && count(category) > 0">
          <Alert
            blue
            style="grid-column: 1 / -1"
          >
            {{ t('modals.search.tryAgain') }}
          </Alert>
          <channel-card
            v-if="results.rss && results.rss[0]"
            :key="results.rss[0].uuid"
            :object="results.rss[0]"
          />
        </template>

        <span v-else-if="category.type === 'federation' && count(category) > 0">
          <template
            v-for="result in resultsPerCategory(category)"
            :key="result.id"
          >
            <ActorLink
              v-if="result.object && result.type === 'account'"
              :actor="result.object as components['schemas']['APIActor']"
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
        </span>

        <EmptyState
          v-if="count(category) === 0"
          style="grid-column: 1 / -1"
          :refresh="true"
          @refresh="search"
        />
        <Link
          v-else-if="'more' in category"
          solid
          secondary
          :to="category.more"
        >
          {{ t('components.Home.link.viewMore') }}
        </Link>
      </Section>
    </template>
  </Modal>
</template>
