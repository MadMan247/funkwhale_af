import { defineStore } from 'pinia'
import { ref, computed, type Ref } from 'vue'

import axios from 'axios'
import hash from 'stable-hash'

import type { paths, components } from '~/generated/types'
import type { Split } from 'type-fest'

import useLogger from '~/composables/useLogger'
import { useRateLimiter, isRateLimiterError } from '~/ui/composables/useRateLimiter'

import type { Album, Artist, Tag, Track } from '~/types'

const logger = useLogger()

/** @returns the most unique identifier available per item, assuming every item has at least one key field */
export const getKey = (item: { fid: string } | { artist: { fid: string } } | { id: number } | { name: string }) =>
  'fid' in item ? item.fid : 'artist' in item ? item.artist.fid : 'id' in item ? item.id.toString() : item.name


// ======================================================================
// Object names
const names = [
  'artists',
  'albums',
  'playlists',
  'tracks',
  'channels',
  'radios/radios',
  'tags'] as const satisfies (Exclude<Split<keyof paths, '/'>[3], 'search'> | 'radios/radios')[]
type Name = typeof names[number]

// Paginated lists
type PathMany<N extends Name> = `/api/v2/${N}/` // Has trailing slash in API
type GetPaginatedResponses<N extends Name> = paths[PathMany<N>]['get']['responses'][200]['content']['application/json']
type Params<N extends Name> = paths[PathMany<N>]['get']['parameters']['query']

// Single items by key
type KeyType<N extends Name> =
  { 'artists': 'artists/{id}',
    'albums': 'albums/{id}',
    'playlists': 'playlists/{uuid}',
    'tracks': 'tracks/{id}',
    'channels': 'channels/{composite}',
    'radios/radios': 'radios/radios/{id}',
    'tags': 'tags/{name}'
    }[N]

type PathFirst<N extends Name> = `/api/v2/${KeyType<N>}/` // Has trailing slash in API
export type GetFirstResponse<N extends Name> = paths[PathFirst<N>]['get']['responses'][200]['content']['application/json']



// ======================================================================
// Remote data
type Data<T> =
  | { status: 'notAsked', error?: null, data?: T }
  | { status: 'pending', error?: null, data?: T, lastUpdated: number }
  | { status: 'loading', error?: null, data?: T, lastUpdated: number }
  | { status: 'success',  error?: null, data: T , lastUpdated: number }
  | { status: 'error', error: Error, data?: T, lastUpdated: number }

const notAsked = () => ({ status: 'notAsked' } as const)

const setPending = <T>(remoteData: Data<T>):Data<T> & {status: 'pending'} => ({
  ...remoteData, status: 'pending', error: null, lastUpdated: Date.now()
} as const)

const setLoading = <T>(remoteData: Data<T> & { status: 'pending' | 'success' | 'error' }):Data<T> & {status: 'loading'}  => ({
    ...remoteData, status: 'loading', error: null, lastUpdated: Date.now()
} as const)

const setSuccess = <T>(remoteData: Data<T> & { status: 'loading' }, data: T):Data<T> & {status: 'success'} => ({
   ...remoteData, status: 'success', data, error: null, lastUpdated: Date.now()
} as const)

const setError = <T>(remoteData: Data<T> & { status: 'loading' }, error: Error):Data<T> & {status: 'error'} => ({
  ...remoteData, status: 'error', error, lastUpdated: Date.now()
} as const)

// ======================================================================
// Search results

type Key = string

/**
 * searchCategory returns the content_category of the given filter if there is one, or undefined otherwise. A search
 * shouldn't preempt another search for a different content category (e.g. podcasts or albums).
 */
const searchCategory = <N extends Name>(params: NonNullable<Params<Name>>) =>
  (params as { content_category?: string }).content_category

/**Global rate limiting for any Api call */
const rateLimiter = useRateLimiter<[Name, Params<Name>]>({
  cooldown: 50, // max. 20 requests per second

  // While the user is typing in a search field, only send the last call generated during a cooldown period
  supersedeWhen: ([newName, newFilter], [oldName, oldFilter]) =>
    newName === oldName
    && newFilter != null
    && oldFilter != null
    && searchCategory(newFilter) == searchCategory(oldFilter),

  // Use `hash` can normalize and compare objects deeply.
  equalWhen: (newTask, oldTask) => hash(newTask) === hash(oldTask)
})


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
export const useDataStore
  = defineStore('data', () => {

    // Type map that associates cache keys with their corresponding types
    type ItemType = {
      artist: Artist
      album: Album
      track: Track
      // Add new types here (channel: Channel...)
    }

    type Items<I extends keyof ItemType> = Record<number | string, {
      result: Ref<ItemType[I] | undefined>;
      timestamp: number;
    }>;

    type Cache = {
      [I in keyof ItemType]: Items<I>
    }

    const cache: Cache = {
      artist: {},
      album: {},
      track: {}
    }

  // ------------- Loading tracking --------------- //
  // Track number of active fetches so UI can show a global loader when > 0
  const activeFetches = ref(0)
  const isLoading = computed(() => activeFetches.value > 0)

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
          tagsTimestamp.value = Date.now();
          tagsCache.value = data.results;
        });
      }
      return tagsCache;
    }

    // ------------- Query one --------------- //
    // TODO: Errors and Loading states (`undefined` can mean an error occurred, or the request is still pending)

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
      if (!items[id])
        items[id] = { result: ref(undefined) as Ref<ItemType[I] | undefined>, timestamp: 0 } // born in 1970

      // Re-fetch if immediate is true or the item is not cached (= born in 1970) or older than 1 second
      if (options?.immediate || items[id].timestamp < Date.now() - 1000)
        axios.get<ItemType[I]>(`${type}s/${id}/`, { params: { refresh: 'true' } }).then(({ data }) => {
          items[id]!.result.value = data;
          items[id]!.timestamp = Date.now();
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
      tags: new Map<Key, Data<GetPaginatedResponses<'tags'>>>()
    } as const )

    const maxAge = 5*60000 // Invalidate searches every 5 minutes

    const createResource = <N extends Name>( name: N) => ( params: Params<N>) => {
      const key = hash(params)
      const cached = computed<Data<GetPaginatedResponses<N>>>({
        get: () => searches.value[name].get(key) || notAsked(),
        set: (value) => (searches.value[name] as Map<Key, Data<GetPaginatedResponses<N>>>).set(key, value)
      })

      const isStale
        = () => cached.value.status === 'notAsked'
        || cached.value.lastUpdated < Date.now() - maxAge

      const fetch = async () => {
            // track active fetches for global loading state
            activeFetches.value = activeFetches.value + 1
            try {
              cached.value = setPending(cached.value)
              await rateLimiter.greenlight([name, params])
              cached.value = setLoading(cached.value as Data<GetPaginatedResponses<N>> & {status: 'pending'})
              const { data } = await axios.get<GetPaginatedResponses<N>>(name, { params })
              cached.value = setSuccess(cached.value as Data<GetPaginatedResponses<N>> & {status: 'loading'}, data)
            } catch (error) {
              if (isRateLimiterError(error as Error)) {
                logger.info(error)
              } else {
                logger.error(`Error fetching multiple ${name} with filter/params ${JSON.stringify(params)}:`, error);
                if (cached.value.status === 'loading')
                  cached.value = setError(cached.value, error as Error)
              }
            } finally {
              // ensure we never go negative
              activeFetches.value = Math.max(0, activeFetches.value - 1)
            }
          }

      if (isStale()) fetch()

      // Add `key` and `refetch` to the reactive object
      return computed(()=> ({
        ...searches.value[name].get(key) as Data<GetPaginatedResponses<N>>,
        key: hash(cached.value),
        refetch: fetch
      }))
    }

    /**
     * @param params - filter to find the artists
     * @returns a reactive object with fields `status` (`error`, `success` or `pending`) and nullable fields `data` and `error`
     * as well as a `refetch` method (skipping the rate limiter) and a unique `key` (for use with v-for)
     */
    const artists = createResource('artists')

    /**
     * @param params - filter to find the albums
     * @returns a reactive object with fields `status` (`error`, `success` or `pending`) and nullable fields `data` and `error`
     * as well as a `refetch` method (skipping the rate limiter) and a unique `key` (for use with v-for)
     */
    const albums = createResource('albums')

    /**
     * @param params - filter to find the tracks
     * @returns a reactive object with fields `status` (`error`, `success` or `pending`) and nullable fields `data` and `error`
     * as well as a `refetch` method (skipping the rate limiter) and a unique `key` (for use with v-for)
     */
    const tracks = createResource('tracks')

    /**
     * @param params - filter to find the channels
     * @returns a reactive object with fields `status` (`error`, `success` or `pending`) and nullable fields `data` and `error`
     * as well as a `refetch` method (skipping the rate limiter) and a unique `key` (for use with v-for)
     */
    const channels = createResource('channels')

    /**
     * @param params - filter to find the radios
     * @returns a reactive object with fields `status` (`error`, `success` or `pending`) and nullable fields `data` and `error`
     * as well as a `refetch` method (skipping the rate limiter) and a unique `key` (for use with v-for)
     */
    const radios = createResource('radios/radios')

    /**
     * @param params - filter to find the tags
     * @returns a reactive object with fields `status` (`error`, `success` or `pending`) and nullable fields `data` and `error`
     * as well as a `refetch` method (skipping the rate limiter) and a unique `key` (for use with v-for)
     */
    const tags_ = createResource('tags')

    /**
     * @param params - filter to find the playlists
     * @returns a reactive object with fields `status` (`error`, `success` or `pending`) and nullable fields `data` and `error`
     * as well as a `refetch` method (skipping the rate limiter) and a unique `key` (for use with v-for)
     */
    const playlists = createResource('playlists')

    return {
      data,
      get,
      tagsCache,
      tags,
      artists,
      albums,
      tracks,
      channels,
      radios,
      tags_,
      playlists,
      searches,
      // Loading state
      activeFetches,
      isLoading
    }
  })
