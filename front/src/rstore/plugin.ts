import type { paths } from '~/generated/types'

import { ref } from 'vue'
import { definePlugin } from '@rstore/vue'

import axios from 'axios'
import hash from 'stable-hash'

import useLogger from '~/composables/useLogger'

const logger = useLogger()

import { type Name, type Item, getKey } from './model.ts'

/** Debouncing (Rate limiting) for individual query parameters such as
search term, pagination and ordering.
This is the time the cache retains a specific query before re-fetching if.
For example, if the user clicks "refresh" three times within this period,
the fetch will happen twice: once at the start of the period and once at the end.
*/
const waitTimeBetweenFetches = 1000;

// Paginated lists
type PathMany<N extends Name> = `/api/v2/${N}/` // Has trailing slash in API
type GetPaginatedResponses<N extends Name> = paths[PathMany<N>]['get']['responses'][200]['content']['application/json']

// First match
type KeyType<N extends Name> = N extends 'albums' ? 'albums/{id}' : N extends 'channels' ? 'channels/{composite}' : never
type PathFirst<N extends Name> = `/api/v2/${KeyType<N>}/` // Has trailing slash in API
type GetFirstResponse<N extends Name> = paths[PathFirst<N>]['get']['responses'][200]['content']['application/json']

/** Stores the latest sorted search/pagination results for each request.
Note that paths are compressed to names, and items to id,
mirroring the equality rules in the normalized _rstore_.
In addition, we normalize and hash the params to remove variations in
field order and to make JS compare them by value
*/
export const idsPerParams = ref<Map<string, { keys: string[], lastUpdated: number, scheduledForUpdate: boolean }>>(new Map())

/** No ids, never updated */
const initialValue = { keys: [], lastUpdated: 0, scheduledForUpdate: false }

/** @returns true if item of `type` with `key` has been found by backend given `params` */
const isAssociated = (type: Name, params: object = {}) =>
  (key: string) =>
    idsPerParams.value.get(hash([type, params]))?.keys?.includes(key)

/** @returns backend-sorted index  of item of `type` with `key` given `params` */
export const index = (type: Name, params: object = {}) =>
  (key: string) =>
    idsPerParams.value.get(hash([type, params]))?.keys?.indexOf(key)

/** Associate a search/pagination request with its sorted results list and remove the `scheduledForUpdate` lock */
const update = (type: Name, params: object = {}) =>
  (results: Item[]) => {
    idsPerParams.value.set(hash([type, params]), { keys: results.map(getKey), lastUpdated: Date.now(), scheduledForUpdate: false })
  }

/** Mark the call as scheduled, for example to debounce or throttle fetches*/
const markAsScheduledForUpdate = (type: Name, params: object = {}) => {
  const lookupKey = hash([type, params]);
  const currentValue = idsPerParams.value.get(lookupKey) ?? initialValue
  idsPerParams.value.set(lookupKey, { ...currentValue, scheduledForUpdate: true })
}

/** @returns 'stale' if older than maxAge, 'scheduledForUpdate' if an update will happen soon, or the milliseconds until maxAge will be reached if fresh */
const freshness = (type: Name, params: object = {}) =>
  (maxAge: number) => {
    const { lastUpdated, scheduledForUpdate } = idsPerParams.value.get(hash([type, params])) ?? { lastUpdated: 0, scheduledForUpdate: false }
    // console.log("        DO  scheduledForUpdate? ", scheduledForUpdate)
    // console.log("        DO  stale? ", lastUpdated + maxAge, '<', Date.now(), lastUpdated + maxAge < Date.now())
    // console.log("        DO  fresh? ", lastUpdated + maxAge - Date.now(), 'of remaining ms; <', maxAge)
    return scheduledForUpdate
      ? 'scheduledForUpdate'
      : lastUpdated + maxAge < Date.now()
        ? 'stale'
        : lastUpdated + maxAge - Date.now()
  }

const sleep = (ms: number) =>
  new Promise(resolve => setTimeout(resolve, ms));

export default definePlugin({
  name: 'funkwhale',

  setup({ hook }) {

    /** Ask the cache for the first match for a given query/key per modelName */
    hook('cacheFilterFirst', ({ key, findOptions, model, readItemsFromCache, setResult }) => {
      console.log('DO cacheFilterFirst', model.name, "🔍", JSON.stringify(findOptions?.filter))

      const matchingKey = (item: Item) =>
        key
          ? key === getKey(item)
          : true

      const matchingParams = (item: Item) =>
        findOptions
          ? isAssociated(model.name as Name, findOptions?.filter)(getKey(item))
          : true

      const itemsInCache = readItemsFromCache()

      if (itemsInCache) {
        const foundItem = itemsInCache.find(
          item => matchingKey(item) && matchingParams(item)
        )
        if (foundItem) {
          setResult(foundItem)
        }
      }
    })

    /** Ask the server for the first match for a given query/key per modelName

    TODO: Implement debouncing (rate-limiting) for first-match fetches
    */
    hook('fetchFirst', async ({ key, findOptions, setResult, model }) => {
      try {
        const response = await axios.get<GetFirstResponse<Name>>(
          `${model.name}/${key}`,
          { params: findOptions?.filter }
        )
        // Overrides the entry in the model cache
        if (response.data) {
          setResult(response.data);
        }
      } catch (error) {
        logger.error(`Error fetching single ${model.name} with filter/params ${JSON.stringify(findOptions?.filter)}:`, error);
      }
    })

    /** Ask the cache for the ordered matches for a given query per modelName */
    hook('cacheFilterMany', ({ findOptions, getResult, setResult, model }) => {
      const matchingParams = (item: Item) =>
        findOptions
          ? isAssociated(model.name as Name, findOptions.filter)(getKey(item))
          : true

      const cachedItems = getResult()

      if (cachedItems) {
        setResult(cachedItems.filter(matchingParams))
      }
    })

    /** Ask the server for the ordered matches for a given query per modelName, and associate the name/params tuple with the response

    Note that fetches are debounced (rate-limited), so manual refreshes may be delayed
    */
    hook('fetchMany', async ({ findOptions, setResult, model }) => {

      // Debounce
      const freshness_ = freshness(model.name as Name, findOptions?.filter)(waitTimeBetweenFetches);

      const fetchNow = async () => {
        try {
          const paginatedResponse = await axios.get<GetPaginatedResponses<Name>>(
            model.name,
            { params: findOptions?.filter }
          );
          update(model.name as Name, findOptions?.filter)(paginatedResponse.data.results)
          if (paginatedResponse.data.results) {
            setResult(paginatedResponse.data.results);
          }
        } catch (error) {
          logger.error(`Error fetching multiple ${model.name} with filter/params ${JSON.stringify(findOptions?.filter)}:`, error);
        }
      }

      switch (freshness_) {
        case 'scheduledForUpdate':
          break;
        case 'stale':
          markAsScheduledForUpdate(model.name as Name, findOptions?.filter);
          await fetchNow();
          break;
        default:
          markAsScheduledForUpdate(model.name as Name, findOptions?.filter)
          await sleep(freshness_);
          await fetchNow();
      }
    })

    // TODO: Implement!
    hook('createItem', async (payload) => {
      const result = await fetch(`${payload.model.name}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload.item)
      }).then(r => r.json())
      if (result) {
        payload.setResult(result)
      }
    })

    // TODO: Implement!
    hook('updateItem', async (payload) => {
      const result = await fetch(`${payload.model.name}/${payload.key}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload.item)
      }).then(r => r.json())
      if (result) {
        payload.setResult(result)
      }
    })

    // TODO: Implement!
    hook('deleteItem', async (payload) => {
      await fetch(`${payload.model.name}/${payload.key}`, {
        method: 'DELETE'
      })
    })
  }
})
