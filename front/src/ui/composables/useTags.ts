import type { paths } from '~/generated/types.ts'

import { computed, ref, type Ref } from 'vue'
import { useStore } from '~/store'
import axios from 'axios'

export type Item = { type: 'custom' | 'preset', label: string }
export type Model = { currents: Item[], others?: Item[] }

/**
 * Load and cache all tags.
 * - Two-way binding with store (any change to the store will be reflected in `others`)
 * - Two-way binding with ref
 * @param currents Selected tags
 * @returns an object with `currents` and `others`, ready to be used inside
 */
export const useTags = (currents: Ref<string[], string[]>) => {
  const store = useStore()

  // Ignore quick successive fetch triggers
  const ignorePeriod = 500

  // Wait between consecutiv fetches
  const waitInterval = 3000

  // Wait after changing a tag before re-fetching
  const refetchInterval = 6000

  // Number of tags to load on one page
  const maxTags = 100000

  const lastFetched = ref<number>(0)

  const fetch = async () => {
    // console.log('FETCH TAGS')
    // Ignore subsequent fetch commands triggered in quick succession
    if (lastFetched.value + ignorePeriod > Date.now())
      return

    // Always wait some milliseconds before re-fetching
    if (lastFetched.value + waitInterval > Date.now()) {
      window.setTimeout(fetch, lastFetched.value + waitInterval - Date.now())
      return
    }

    const response = await axios.get<paths['/api/v2/tags/']['get']['responses']['200']['content']['application/json']>(
      '/tags',
      { params: { page: 1, page_size: maxTags } }
    )

    // console.log('TAGS RESPONSE.data.results', response.data.results)
    store.commit('ui/tags', response.data.results)
  }

  fetch();

  /**
   * @returns v-model for `Pills` component
   */
  return computed({
    get () {
      // console.log("GET TAGS")
      return ({
      // Get `currents` from parameter
      currents: currents.value.map(tag => ({
        label: tag,
        type: (store.state.ui.tags || []).some(({ name }) => tag === name) ? 'preset' : 'custom'
      } as const)),

      // Get `others` from cache
      others: (store.state.ui.tags || [])
        .filter(({ name }) => !currents.value.includes(name))
        .map(({ name }) => ({
          label: name,
          type: 'preset'
        } as const))
    })},

    set (model) {
      // console.log('SET TAGS', response.data.results)

      // Set parameter `currents` from `model.currents`
      currents.value = model.currents.map(({ label }) => label)

      // Set runtime-only options from `model.others` and `model.current`
      // TODO: Broadcast new custom tags so that other pills components can use them

      // Re-fetch after each new setting
      window.setTimeout(fetch, refetchInterval)
    }
})
}

// alternative ways to generate tags
// ...
