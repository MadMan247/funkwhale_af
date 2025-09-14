import { defineQuery, useQuery } from '@pinia/colada'

import type { paths } from '~/generated/types'
import type { Split } from 'type-fest'

import useLogger from '~/composables/useLogger'
import { useRateLimiter, isRateLimiterError } from '~/rstore/useRateLimiter'
import { useCache } from '~/rstore/useCache'


import axios from 'axios'
import hash from 'stable-hash'


const logger = useLogger()




/**Global rate limiting for any Api call */
const rateLimiter = useRateLimiter<[Name, object | undefined]>({
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


// =======================================================================



// Object names
const names = [
  'artists',
  'albums',
  'artists',
  'playlists',
  'tracks',
  'channels',
  'radios/radios',
  'tags'] as const satisfies (Exclude<Split<keyof paths, '/'>[3], 'search'> | 'radios/radios')[]
type Name = typeof names[number]

// Paginated lists
type PathMany<N extends Name> = `/api/v2/${N}/` // Has trailing slash in API
type GetPaginatedResponses<N extends Name> = paths[PathMany<N>]['get']['responses'][200]['content']['application/json']



// ======================================================================




/** @returns the most unique identifier available per item, assuming every item has at least one key field */
const getKey = (item: { fid: string } | { artist: { fid: string } } | { id: number } | { name: string }) =>
  'fid' in item ? item.fid : 'artist' in item ? item.artist.fid : 'id' in item ? item.id.toString() : item.name

/** @returns a query function that fetches paginated data from the API */
const define = <N extends Name>(name: N) => (params: object) => defineQuery(() => useQuery ({
  key: [name, hash(params)],
  query: async () => { try {
    await rateLimiter.greenlight([name, params])
    const paginatedResponse = await axios.get<GetPaginatedResponses<N>>(
      name,
      { params }
    )

    const { results, count } = paginatedResponse.data

    // Update the cache of filters
    keysFor(name, params).value = results.map(getKey)

    // Return the resulting list
    return ({ results, count }) as ({ results: GetPaginatedResponses<N>['results'], count: number })

  } catch (error) {
    if (isRateLimiterError(error as Error)) logger.info(error)
    else logger.error(`Error fetching multiple ${name} with filter/params ${JSON.stringify(params)}:`, error);
  }}
}))

/**
 * Select a query for the Funkwhale object you want to fetch
 *
 * Example:
 * import useQuery from '~/query.ts'
 * const state = useQuery.artists({ q: 'a', page: 1, page_size: 4 })
 *
 * // You can now use  state.value.status, state.value.data etc. to build a user interface.
 */
const query = {
  artists: define( 'artists'),
  albums: define('albums'),
  channels: define('channels'),
  tracks: define('tracks'),
  playlists: define('playlists'),
  radios: define('radios/radios'),
  tags: define('tags')
} as const

export default  query;
