import { defineStore } from 'pinia'
import { ref, computed, type Ref } from 'vue'
import axios from 'axios'

import type { Album, Artist, Tag, Track } from '~/types'
import type { components } from '~/generated/types'

/**
 * Fetch an item from the API.
 * - Rate limiting: Caches the result for 1 second to prevent over-fetching and request duplication (override with { immediate: true})
 * - Sharing reactive objects across components: Avoid data duplication, and auto-update the Ui whenever an updated version of the data is re-fetched
 * - Strongly typed results
 * - TODO: Errors and Loading states (`undefined` can mean an error occurred, or the request is still pending)
 *
 * **Example**
 * ```ts
 * import { useDataStore } from '~/ui/stores/data'
 *
 * const data = useDataStore()
 *
 * artist15 = data.get("artist", "15") // Ref<Artist | undefined>
 * const album23 = data.get("album", "23") // Ref<Album | undefined>
 * ```
 * As soon as you re-fetch data, all references to the same object in all components using this store will be updated.
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
        items[id] = { result: ref(undefined) as Ref<ItemType[I] | undefined>, timestamp: 0 }

      // Re-fetch if immediate is true or the item is not cached or older than 1 second
      if (options?.immediate || items[id].timestamp < Date.now() - 1000)
        axios.get<ItemType[I]>(`${type}s/${id}/`, { params: { refresh: 'true' } }).then(({ data }) => {
          items[id].result.value = data;
          items[id].timestamp = Date.now();
        })
      return items[id].result
    }

    return {
      data,
      get,
      tagsCache,
      tags
    }
  })
