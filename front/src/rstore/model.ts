import type { ModelList } from '@rstore/vue'
import { defineItemType } from '@rstore/vue'
import type { Split } from 'type-fest'

import type { components } from '~/generated/types'
import type { paths } from '~/generated/types'

/** @returns the most unique identifier per item, assuming every item has at least one key field */
export const getKey = (item: { fid: string } | { artist: { fid: string } }) =>
  'fid' in item ? item.fid : item.artist.fid

/** Models

Note: The search endpoint is not in use. Instead, use param `q` in other endpoints

TODO: Describe relations (perhaps wait for OpenAPI plugin)
*/
export const models = [
  defineItemType<components['schemas']['Album']>().model({ name: 'albums', getKey }),
  defineItemType<components['schemas']['Channel']>().model({ name: 'channels', getKey })
] as const satisfies
  ModelList satisfies
  // Assert that the name is always the third segment in the API path:
  { name: Exclude<Split<keyof paths, '/'>[3], 'search'> }[]

export type Name = typeof models[number]['name']
export type Item = typeof models[number]['~item']
