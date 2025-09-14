import type { paths } from '~/generated/types'

import { definePlugin } from '@rstore/vue'

import axios from 'axios'
import hash from 'stable-hash'

import useLogger from '~/composables/useLogger'
import { useRateLimiter, isRateLimiterError } from './useRateLimiter'
import { useCache } from './useCache'

// TODO: Do not return an empty list from the cache if query has not yet been fetched (then we get no loading state)

const logger = useLogger()

import { type Name, type Item, getKey } from './model.ts'

// Paginated lists
type PathMany<N extends Name> = `/api/v2/${N}/` // Has trailing slash in API
type GetPaginatedResponses<N extends Name> = paths[PathMany<N>]['get']['responses'][200]['content']['application/json']

// First match
type KeyType<N extends Name> = N extends 'albums' ? 'albums/{id}' : N extends 'channels' ? 'channels/{composite}' : never
type PathFirst<N extends Name> = `/api/v2/${KeyType<N>}/` // Has trailing slash in API
type GetFirstResponse<N extends Name> = paths[PathFirst<N>]['get']['responses'][200]['content']['application/json']

// API request rate is limited and stale requests are skipped

/**Global rate limiting for any Api call */
const rateLimiter = useRateLimiter<[Name, object | undefined]>({
  // Minimum waiting time between consecutive calls
  cooldown: 500,

  // While the user is typing in a search field, only send the last call generated during a cooldown period
  supersedeWhen: ([newName, newFilter], [oldName, oldFilter]) =>
    newName === oldName && newFilter !== undefined && oldFilter !== undefined,

  // Use `hash` can normalize and compare objects deeply.
  equalWhen: (newTask, oldTask) =>
    hash(newTask) === hash(oldTask)
})

// Search requests are cached and expire after 1 minute

/** Stores the latest sorted search/pagination results for each request.
 * This is necessary because we only model final types in rstore (TODO: model search results)
Note that paths are compressed to names, and items to id,
mirroring the equality rules in the normalized _rstore_.
In addition, we normalize and hash the params to remove variations in
field order and to make JS compare them by value.
*/

/** We have to cache search results (as lists of item keys) because we cannot reproduce search locally (yet) */
const cache = useCache<string, string[]>({
  retention: 60000
});

/**
 * @param name: The model name (Artist, Album, ...)
 * @param filter: The search filter object used to reproduce search results locally
 * @returns the keys of the items returned by the API
 */
const keysFor = (name: Name | string, filter: object | undefined) =>
  cache(hash([name, filter]))

export default definePlugin({
  name: 'funkwhale',

  setup({ hook }) {

    /** Ask the cache for the first match for a given query/key per modelName */
    hook('cacheFilterFirst', ({ key, findOptions, model, readItemsFromCache, setResult }) => {

      const matchingKey = (item: Item) => key
        ? key === getKey(item)
        : true

      const matchingParams = (item: Item) =>
        keysFor(model.name, findOptions?.filter)?.value?.includes(getKey(item))
        || true
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

    /** Ask the server for the first match for a given query/key per modelName */
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
      console.log("cacheFilterMany ----------", model.name, "---------------")
      const cachedItems = getResult() // List of items

      const keys = keysFor(model.name, findOptions?.filter)?.value

      console.log("cacheFilterMany XXX", model.name, findOptions?.filter)
      console.log("cacheFilterMany XXX cached items", model.name, cachedItems)
      console.log("cacheFilterMany XXX keys in cache", model.name, keys)

      if (keys && cachedItems) {
        const filteredCachedItems = cachedItems.filter(
          item => keys.includes(getKey(item))
        )

        console.log("cacheFilterMany XXX setResult(filteredCachedItems):", model.name, filteredCachedItems)
        setResult(filteredCachedItems)
      } else {

        console.log("cacheFilterMany XXX failed", model.name)

      }
    })

    /** Ask the server for the ordered matches for a given query per modelName,
     * and associate the name/params tuple with the response */
    hook('fetchMany', async ({ findOptions, setResult, model, getResult }) => {
      console.log("fetchMany ----------", model.name, "---------------")
      console.log("fetchMany XXX...", model.name, findOptions?.filter)

      try {
        await rateLimiter.greenlight([model.name as Name, findOptions?.filter])

        console.log("fetchMany XXX...greenlit", model.name, findOptions?.filter)

        const paginatedResponse = await axios.get<GetPaginatedResponses<Name>>(
          model.name,
          { params: findOptions?.filter }
        )

        console.log("fetchMany XXX...fetched", model.name, findOptions?.filter)

        const { results, count } = paginatedResponse.data

        console.log("fetchMany XXX results", model.name, results)
        console.log("fetchManyXXX count", model.name, count)

        setResult(results.map(r => ({
          ...r,
          totalResults: count
        })));

        console.log("fetchMany XXX result is set", model.name)

        // Update the cache of filters

        keysFor(model.name, findOptions?.filter).value = results.map(getKey)

        console.log("cache updated with", model.name, findOptions?.filter, "=>",  results.map(getKey))

      } catch (error) {

        console.log("fetchMany XXX...fetch errored", model.name, error)

        if (isRateLimiterError(error as Error)) logger.info(error)
        else logger.error(`Error fetching multiple ${model.name} with filter/params ${JSON.stringify(findOptions?.filter)}:`, error);

        console.log("fetchMany XXX getResults instead of setResults", model.name, getResult())

        // I don't know if the following is necessary... yes it is. Otherwise, findMany.ts:128 'item is undefined'
        if (getResult() === undefined) {
          setResult([])
        }
      }
    })

    /* Mutations */

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
