import axios, { type CustomParamsSerializer, type ParamsSerializerOptions } from 'axios'
import { defineStore } from 'pinia'
import hash from 'stable-hash'
import type { Split } from 'type-fest'
import { computed, ref, watch, type Ref } from 'vue'

import useLogger from '~/composables/useLogger'
import type { components, paths } from '~/generated/types'
import type { Album, Artist, Tag, Track } from '~/types'
import { isRateLimiterError, useRateLimiterStore } from '~/ui/stores/rateLimiter'

const logger = useLogger()

/** @returns the most unique identifier available per item, assuming every item has at least one key field */
export const getKey = (item: { fid: string } | { artist: { fid: string } } | { id: number } | { name: string }) =>
  'fid' in item ? item.fid : 'artist' in item ? item.artist.fid : 'id' in item ? item.id.toString() : item.name

// ======================================================================
// Object names
const names = ['artists', 'albums', 'playlists', 'tracks', 'channels', 'radios/radios', 'tags', 'favorites/tracks', 'history/listenings'] as const satisfies (
  | Exclude<Split<keyof paths, '/'>[3], 'search'>
  | 'radios/radios'
  | 'favorites/tracks'
  | 'history/listenings'
)[]
type Name = (typeof names)[number]

// Paginated lists
type PathMany<N extends Name> = `/api/v2/${N}/` // Has trailing slash in API
type GetPaginatedResponses<N extends Name> = paths[PathMany<N>]['get']['responses'][200]['content']['application/json']
type Params<N extends Name> = paths[PathMany<N>]['get']['parameters']['query']

// Single items by key
type KeyType<N extends Name> = {
  artists: 'artists/{id}'
  albums: 'albums/{id}'
  playlists: 'playlists/{uuid}'
  tracks: 'tracks/{id}'
  channels: 'channels/{composite}'
  'radios/radios': 'radios/radios/{id}'
  tags: 'tags/{name}'
  'favorites/tracks': 'favorites/tracks/{id}'
  'history/listenings': 'history/listenings/{id}'
}[N]

type PathFirst<N extends Name> = `/api/v2/${KeyType<N>}/` // Has trailing slash in API
export type GetFirstResponse<N extends Name> = paths[PathFirst<N>]['get'] extends {
  responses: {
    200: {
      content: {
        'application/json': infer TData
      }
    }
  }
}
  ? TData
  : never

// ======================================================================
// Remote data
type Metadata = {
  name: Name
  key: string
  lastRequested?: number
  deduplicationKey?: string | unknown
}
type Data<T> = (
  | { status: 'notAsked'; error?: null; data?: T }
  | { status: 'queued'; error?: null; data?: T; lastUpdated: number }
  | { status: 'loading'; error?: null; data?: T; lastUpdated: number }
  | { status: 'success'; error?: null; data: T; lastUpdated: number }
  | { status: 'error'; error: Error; data?: T; lastUpdated: number }
  ) & Metadata

const notAsked = (meta: Metadata) => ({ status: 'notAsked', ...meta }) as const

const setPending = <T>(remoteData: Data<T>): Data<T> & { status: 'queued' } =>
  ({
    ...remoteData,
    status: 'queued',
    error: null,
    lastUpdated: Date.now(),
    // TODO: consider using the rate-limiter-generated timestamp in order to remove two redundant Date.now() calculations.
    lastRequested: Date.now()
  }) as const

const setLoading = <T>(remoteData: Data<T> & { status: 'queued' | 'success' | 'error' }): Data<T> & { status: 'loading' } =>
  ({
    ...remoteData,
    status: 'loading',
    error: null,
    lastUpdated: Date.now()
  }) as const

const setSuccess = <T>(remoteData: Data<T> & { status: 'loading' }, data: T): Data<T> & { status: 'success' } =>
  ({
    ...remoteData,
    status: 'success',
    data,
    error: null,
    lastUpdated: Date.now()
  }) as const

const setError = <T>(remoteData: Data<T> & { status: 'loading' }, error: Error): Data<T> & { status: 'error' } =>
  ({
    ...remoteData,
    status: 'error',
    error,
    lastUpdated: Date.now()
  }) as const

export const invalidate = (remoteData: Data<unknown>) => {
  if ('lastUpdated' in remoteData) remoteData.lastUpdated = 0
}



// ======================================================================
// Search results

type Key = string
type SearchCategory = string

/**
 * **Fetching individual items by key**
 * - Prevent duplicate fetches: Caches the result for 1 second to prevent over-fetching and request duplication (override with { immediate: true})
 * - Share reactive objects across components: Avoid data duplication, and auto-update the Ui whenever an updated version of the data is re-fetched
 *
 * ```ts
 * import { useDataStore } from '~/ui/stores/data'
 *
 * const data = useDataStore()
 *
 * const artist15 = data.get("artist", "15") // Ref<Artist | undefined>
 * const album23 = data.get("album", "23") // Ref<Album | undefined>
 * ```
 *
 * **Fetching paginated search results**
 * - Rate limited (currently 2 requests per seconds)
 *
 * ```ts
 * const albums = data.albums({ query: 'xyz' }) // Ref<{ status, data?, error? }>
 *
 * if (albums.value.status === 'error') albums.refetch();
 *````
 *
 * As soon as data arrives, all references to the same object in all components using this store will be updated.
 *
 * Note: Pinia does not support destructuring.
 * Do not write `{ get } = useDataStore()`
 */
export const useDataStore = defineStore('data', () => {
  /**Global rate limiting queue for any Api call.
   * Tasks are deduplicated using either exact request identity (for use in widgets) or search categories.
   */
  const rateLimiter = useRateLimiterStore()

  // Type map that associates cache keys with their corresponding types
  // TODO: Refactor cache (see queryMany/searches)
  type ItemType = {
    artist: Artist
    album: Album
    track: Track
    // Add new types here (channel: Channel...)
  }

  type Items<I extends keyof ItemType> = Record<
    number | string, {
      result: Ref<ItemType[I] | undefined>
      timestamp: number
    }
  >

  const cache: { [I in keyof ItemType]: Items<I> } = {
    artist: {},
    album: {},
    track: {}
  }

  // ------------- Query tags --------------- //

  const tagsCache = ref<Tag[]>([])
  const tagsTimestamp = ref(0)

  /**
   * @returns an auto-updating reference to all tags or `[]` if either none are loaded yet, or there was an error
   */
  const tags = () => {
    // Re-fetch if immediate is true or the item is not cached or older than 1 second
    if (tagsTimestamp.value < Date.now() - 1000) {
      axios.get<components['schemas']['PaginatedTagList']>('tags/', { params: { page_size: 10000 } }).then(({ data }) => {
        tagsTimestamp.value = Date.now()
        tagsCache.value = data.results
      })
    }
    return tagsCache
  }

  // ------------- Query one --------------- //
  // TODO: Errors and Loading states (`undefined` can mean an error occurred, or the request is still queued)

  /** Inspect the cache with the Vue Devtools (Pinia tab); read-only */
  const data = computed(() => cache)

  /**
   * @param type - either 'artist' or 'album' etc.
   * @param id - The ID of the item to fetch.
   * @param immediate - Whether to re-fetch immediately (default: only re-fetch data older than 1 second)
   * @returns an auto-updating reference to `undefined` if there is an error or the item is not yet loaded, or the actual item once it is loaded.
   *
   * Tip: Re-run after 1 second to refresh the data.
   */
  const get = <I extends keyof ItemType>(type: I, id: number | string, options?: { immediate?: boolean }) => {
    // Override limited typescript inference (Remove assertion once typescript can infer correctly)
    const items = cache[type] as Items<I>

    // Initialize the object if it doesn't exist
    if (!items[id]) items[id] = { result: ref(undefined) as Ref<ItemType[I] | undefined>, timestamp: 0 } // born in 1970

    // Re-fetch if immediate is true or the item is not cached (= born in 1970) or older than 1 second
    if (options?.immediate || items[id].timestamp < Date.now() - 1000)
      axios.get<ItemType[I]>(`${type}s/${id}/`, { params: { refresh: 'true' } }).then(({ data }) => {
        items[id]!.result.value = data
        items[id]!.timestamp = Date.now()
      })
    return items[id].result
  }

  // ------------- Query many --------------- //

  // TODO: Normalize Data. Each time we receive one or many items from the backend, we can
  // update all instances. Or we can change the caches to store keys instead of objects, moving away from the current API design.

  // Initialize items cache
  const searches = ref({
    artists: new Map<Key, Data<GetPaginatedResponses<'artists'>>>(),
    albums: new Map<Key, Data<GetPaginatedResponses<'albums'>>>(),
    playlists: new Map<Key, Data<GetPaginatedResponses<'playlists'>>>(),
    tracks: new Map<Key, Data<GetPaginatedResponses<'tracks'>>>(),
    channels: new Map<Key, Data<GetPaginatedResponses<'channels'>>>(),
    'radios/radios': new Map<Key, Data<GetPaginatedResponses<'radios/radios'>>>(),
    tags: new Map<Key, Data<GetPaginatedResponses<'tags'>>>(),
    'favorites/tracks': new Map<Key, Data<GetPaginatedResponses<'favorites/tracks'>>>(),
    'history/listenings': new Map<Key, Data<GetPaginatedResponses<'history/listenings'>>>()
  } as const)

  const config = ref<{
    maxAge: number
    paramsSerializer: ParamsSerializerOptions | CustomParamsSerializer
  }>({
    /**Invalidate searches every 5 minutes */
   maxAge: 5 * 60000,

    /** Use no bracket when serializing arrays such as `?tags=a&tags=b` instead of `?tags=[a,b]` */
    paramsSerializer: { indexes: false }
  })

  /**
   * @param name - the name of the resource, e.g. 'artists' or 'albums'
   */
  const createResource = <N extends Name>(name: N) =>
    /**
   * Reactive, cached resource for a given name and params. Use in `<template>` or a `<script setup>` block.
   * @param params - the query parameters to fetch the resource with (see API schema)
   * @param config.refetchSignal - a reactive signal (ref, computed, or getter) that will trigger a refetch when it changes
   * @param config.deduplicationKey - a string or array that will be used as the key for deduplicating and debouncing requests in the rate limiter. By default, it's the tuple of name and params.
   * @param config.isDisabled - invalidate the cache on access
   * @returns:
   * - Remote Data object with status, data, error fields
   * - `key` field that represents a unique hash of the current data (to govern UI re-renders)
   * - `refetch` method to manually re-fetch the data (skipping the rate limiter queue)
   *
   * Note that if you construct a resource that has been fetched more than 5 minutes ago, a new fetch job is auto-scheduled.
   * Otherwise, the cached ref is returned and no autofetch is performed.
   */
    (params: Params<N>,
      { refetchSignal, deduplicationKey }: {
        refetchSignal?: Parameters<typeof watch>[0],
        deduplicationKey?: SearchCategory
      } = {}
    ) => {
      const key = hash(params)
      const cached = computed<Data<GetPaginatedResponses<N>>>({
        get: () => searches.value[name].get(key) ?? notAsked({ name, key, deduplicationKey }),
        set: (value) => (searches.value[name] as Map<Key, Data<GetPaginatedResponses<N>>>).set(key, value)
      })

      const scheduleFetch = ( rateLimiterConfig?: Parameters<typeof rateLimiter.greenlight>[1]) => async () => {
        // TODO: Remove type acrobatics for request state transitions
        try {
          cached.value = setPending(cached.value)
          await rateLimiter.greenlight<SearchCategory | [Name, Params<Name>]>(
            deduplicationKey || [name, params],
            rateLimiterConfig
          )
          cached.value = setLoading(cached.value as Data<GetPaginatedResponses<N>> & { status: 'queued' })
          const { data } = await axios.get<GetPaginatedResponses<N>>(name, { params, paramsSerializer: config.value.paramsSerializer })
          cached.value = setSuccess(cached.value as Data<GetPaginatedResponses<N>> & { status: 'loading' }, data)
        } catch (error) {
          if (isRateLimiterError(error as Error)) {
            logger.info(error)
            // TODO: What should be in the resource when a fetch is superseded by a newer one?
          } else {
            logger.error(`Error fetching multiple ${name} with filter/params ${JSON.stringify(params)}:`, error)
            if (cached.value.status === 'loading') cached.value = setError(cached.value, error as Error)
          }
        }
      }

      // Invalidate cache if deduplicationKey has changed or caching is disabled
      if (deduplicationKey && cached.value.deduplicationKey !== deduplicationKey) {
        cached.value = notAsked({ name, key, deduplicationKey })
      }

      // Queue up a request if resource is new or stale or invalidated
      if (cached.value.status === 'notAsked' || cached.value.lastUpdated < Date.now() - config.value.maxAge){
        scheduleFetch()()
      }

      // Listen to external refetch signal
      // TODO: Replace with `activeObservers` reference-counting pattern https://dev.funkwhale.audio/funkwhale/funkwhale/-/issues/2645
      if (refetchSignal) {
        watch(refetchSignal, scheduleFetch())
      }

      // Add `key` and `refetch` for reactive UIs
      return computed(() => ({
        ...(searches.value[name].get(key) as Data<GetPaginatedResponses<N>>),
        key,
        refetch: scheduleFetch({ priority: true })
      }))
    }

  return {
    config,

    // Paginated resources
    artists: createResource('artists'),
    albums: createResource('albums'),
    tracks: createResource('tracks'),
    channels: createResource('channels'),
    radios: createResource('radios/radios'),
    tags_: createResource('tags'),
    playlists: createResource('playlists'),
    'favorites/tracks': createResource('favorites/tracks'),
    'history/listenings': createResource('history/listenings'),
    searches,

    // Other resources
    data,
    get,
    tagsCache,
    tags,

    // Resource observers (global)
    cachedResources: computed(() =>
      Object.values(searches.value).flatMap(entries => [...entries.values()])
    ),
    latestResourcesByDeduplicationKey: (predicate: (deduplicationKey: string) => boolean) =>  computed(() =>
      Object.values(searches.value)
        .flatMap(entries => [...entries.values()])
        // Visible resources are the newest per deduplicationKey
        // TODO: Reimplement with `reduce` (or composed generator functions) to avoid duplicate iterations
        .filter((resource, _, allResources) => {
          if (typeof resource.deduplicationKey !== 'string') return false
          if (!predicate(resource.deduplicationKey)) return false
          const newerResourceWithSameKey = allResources.find(r =>
            r.deduplicationKey === resource.deduplicationKey
            && (r.lastRequested ?? 0) > (resource.lastRequested ?? 0)
          )
          return !newerResourceWithSameKey
        }
    )),
    numberOfCachedResources: computed(() =>
      Object.values(searches.value).reduce((sum, entries) => sum + entries.size, 0)
    ),
    numberOfQueuedResources: computed(() =>
      Object.values(searches.value).reduce((sum, entries) => sum + [...entries].filter(([_, v]) =>
        v.status === 'queued'
      ).length, 0)
    ),
    numberOfLoadingResources: computed(() =>
      Object.values(searches.value).reduce((sum, entries) => sum + [...entries].filter(([_, v]) =>
        v.status === 'loading'
      ).length, 0)
    )
   }
})
