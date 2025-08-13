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
import * as RStore from '~/rstore'
import { idsPerParams } from '~/rstore/plugin.ts'

import ArtistCard from '~/components/artist/Card.vue'
import PlaylistCard from '~/components/playlists/Card.vue'
import ChannelCard from '~/components/audio/ChannelCard.vue'
import ActorLink from '~/components/common/ActorLink.vue'
import TrackTable from '~/components/audio/track/Table.vue'
import AlbumCard from '~/components/album/Card.vue'
import RadioCard from '~/components/radios/Card.vue'
import RadioButton from '~/components/radios/Button.vue'
import TagsList from '~/components/tags/List.vue'
import EmptyState from '~/components/common/EmptyState.vue'

import Modal from '~/components/ui/Modal.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Input from '~/components/ui/Input.vue'
import Section from '~/components/ui/Section.vue'
import Link from '~/components/ui/Link.vue'
import Loader from '~/components/ui/Loader.vue'
import Alert from '~/components/ui/Alert.vue'

/*

Strategy

I think the `search` endpoint is for when you want all results at once.
It's not really useful because it has less functionality than the other things.

- Like v1.4, we don't use the `/search` endpoint. Instead,
   we query each type with `q=...` and `page_size=3`
- We stagger the requests by 200ms

- Open question: How do we build filters for cached files?
  (a) Re-implement the server logic -> This is the correct way because
        it enables offline-first
        Token search -- this is so far hard to implement.
        Open for v2+!
  (b) Make global `inCurrentSearch: { albums: [1, 3, 4], tags: [], }` lists.
        Update value any time the parameter `q` is in a search.

        Design for global filter-cache:
        const filterCache : Map<JSON.stringify({ name: Name, params: params }), Id[] }

        - Each time we run a search query in `plugin.ts`, we say:
              resultIds.set(
                JSON.stringify({ name: payload.model.name, key: payload.findOptions?.params }),
                results.map(item=>item.id)
              )

        - Each time we use params, we can then already use the cached by finding the correct filter:
            filter = (query) => (item) =>
              resultIds.get(JSON.stringify({ name: query.name, params: query.params })).includes(getId(item))

        I think this is particularly nice for paged navigation, where going back and forth can now leverage the cache.

        We still need to find out how to tell rstore to invalidate the results.

        It's a different thing than saying `artist` has n invalidation timeout of 5 minutes.

        We are basically invalidating the parameters!



        It's very important we implement the naive filter (param identity).

        It's also very important that we
        - refresh

*/

const myPageSize = ref(2);

// Marker needs to be set!

const { t } = useI18n()
const rStore = RStore.useStore()

const { data: album, refresh: _refreshAlbum, loading: _loadingAlbum } = rStore.albums.queryMany(() => ({
  filter: {
    page: 1,
    page_size: myPageSize.value
  }
}))

// const { data: channel } = rStore.channels.queryMany(()=>({
//   filter: {
//     page: 1,
//     page_size: 1
//   }
// }))

// We can add `refresh` and `loading` indicators to all running queries!
//
//
/*

To summarize

- For the search interface, we simply implement a list of sections where each section
has `data`, `loading`, `refresh`, `error` (and `more` link in case `count` is larger than the local count)

- These refs are generated with `queryMany`

- In a query, we have to keep `filter` and `params` in sync:
   - `params` is our source of truth. Every time the server responds,
      we store { count, ids, timestamp } under JSON.stringify({ name, params }).
      `filter` looks up `ids` under JSON.stringify({ name, params }) and then
      filters by id.

- We display the number of hits, and we calculate the total, and display all on little badges :-)


- Instead of summary/details, we could use tabs that jump to the place.
   Each tab would be synced with the `type` query in the url (like in krasses.berlin).



   - For Search and Pagination, the idea is that the `params` are keys to the inclusion&order list.

   - I wonder if rstore preserves the ordering... If not, we simply store the order in the item
      at receive-time with an Array.map.

   - https://rstore.dev/guide/plugin/hooks.html#custom-cache-filtering
       Custom filter:
         1. Type the `params`
         2. We create additional hooks.
              Before: queryFirst -> [fetchFirst, __internal_key_compare_filter__]
              After: queryFirst -> [fetchFirst, cacheFilterFirst]
          3. We implement the additional hooks:
              hook('cacheFilterFirst', (payload) => {
                const { key, findOptions } = payload
                const item = payload.readItemsFromCache().find((item) =>
                    ...
              hook('cacheFilterMany', (payload) => {
                const { findOptions } = payload
                const { params } = findOptions
                const items = payload.getResult().filter(item=>
                  item.visibleWithParams.includes(createHash([payload.model.name, params]))
                payload.setResult(items)

              hook('fetchMany', async (payload) => {
                const { params } = payload.findOptions
                const paginatedResult = await axios.get(`/api/${payload.model.name}`,
                  params, etc.
                )
                const hash = createHash([payload.model.name, params])
                const cached = payload.readItemsFromCache()
                payload.setResult(paginatedResponse.data.results.map(item=>({
                  ...item,
                  // Associate each item with all queries that match it
                  // TODO: Mirror the backend logic here to enable offline-first
                  visibleWithParams: [
                    // Preserve associations with other queries, if any
                    ...(cached.find(citem=>citem.id===item.id)?.visibleWithParams ?? []),
                    hash
                  ]
                  // Finally, if after a refresh the server no longer associates an item
                  // already in the cache with the given params, then remove the association:
                  store.$cache.writeItem (etc.)

                  // This seems very complicated, and it pollutes the model.
                  // Better: We just create a ref<Map<[hash, name], [id]>>([]) for storing and
                  // invalidating the association `params=>filter`.
                });



                //https://mojoauth.com/hashing/fast-hash-in-javascript-in-browser/
                const createHash = object => {
                  let hash = 0;
                  let t = JSON.stringify(object);
                  for (let i=0; i<t.length; i++)
                    hash = ((hash << 5) - hash + t.charCodeAt(i)) | 0
                  return hash >>> 0;
                }


  Future:
    - For now, we will use fetch-then-cache, and not support features such as search in
      offline-first.
    - Later, we can add a UI indication for stale params, with the timestamp being old,
        and an automatic trigger: while user is still browsing the app, refresh content periodically.
        When tab gets focus, try to re-fetch.
    - Thought: `Tracks` and `Tags` have no global pages in the sidebar. So when we search, we may want all?
       (a) Button `load more` increases items-per-page
       (b) Show pagination in non-global types (but don't link it to url)
       I think pagination is straightforward because we have pagination component.
       So we have a lot of local variables.


Can we do it all in template instead of script?

const artistsPage = ref(2);
const q = useQueryParameter('q') // It's also the ref for the input box

//MAYBE: const debouncedQ = ... // Delay and throttle the search query change response just a bit

const sections =
  { artists:
      rStore.artists.queryMany(()=>({
        filter: () => rStore.,
        params: {
          page: artistsPage.value,
          page_size: 2,
          q: q.value
        }
      }),
    albums:
    ...

  }

OR

const { artists, albums, tracks, playlists, radios, tags, podcasts, series } = RStore.useStore()

<Section :h2="t('artists')">

</Section>


*/


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

/* TODO: Refactor */
// 1. Move fetching logic to `data.ts` (useDataStore)
//     - Use caching
//     - Debounce from input by 500ms
//     - Load modal on keydown; show empty state while fetching
// 2. Debug content loading logic
// 3. Make colors subtler
//      -
// 4. Make layout nicer
//     - Sections fill the modal
//     - Optimize space use
//     - Disable opening empty sections; deemphasize them (disable attribute)
//     - Make the headers transparent by default (ghost: only show background on hover)
//     - When Modal closes, delete customly closed categories (open them again as they appear in search results)
//
// Only show `View More` if there are actually more

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
    <input
      v-model="myPageSize"
      type="number"
      step="1"
      max="3"
      value="1"
    >
    <pre>{{ album?.length }} should be {{ myPageSize }}</pre>
    <hr>
    <pre>
        {{ idsPerParams }}
    </pre>
    <pre>{{ rStore.$cache.getState() }}</pre>
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

    <Loader v-if="isLoading" />

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
            :artist="resultsPerCategory(category)[index]!"
          />

          <AlbumCard
            v-else-if="category.type === 'albums' || category.type === 'series'"
            :album="resultsPerCategory(category)[index]!"
          />

          <PlaylistCard
            v-else-if="category.type === 'playlists'"
            :playlist="resultsPerCategory(category)[index]!"
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
