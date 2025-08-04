import type { Token } from '~/utils/search'

import { compileTokens, normalizeQuery, parseTokens } from '~/utils/search'
import { refWithControl } from '@vueuse/core'
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

/**
 * Configuration options for the smart search composable.
 */
export interface SmartSearchProps {
  /** Initial query string to populate the search */
  defaultQuery?: string
  /** Whether to sync search state with the browser URL */
  updateUrl?: boolean
}

/**
 * Enables structured search queries like "status:pending category:music" while maintaining
 * bidirectional sync between raw query strings and parsed tokens. Supports URL synchronization
 * and programmatic search manipulation.
 *
 * @param props - Configuration options for the search behavior
 * @returns Object containing search methods and reactive query state
 *
 * @example
 * ```ts
 * const search = useSmartSearch({ updateUrl: true })
 * search.addSearchToken('status', 'pending')
 * search.addSearchToken('category', 'music')
 * // Generates query: "status:pending category:music"
 * ```
 */
export default (props: SmartSearchProps) => {
  const query = refWithControl(props.defaultQuery ?? '')
  const tokens = ref([] as Token[])

  watch(query, (value) => {
    tokens.value = parseTokens(normalizeQuery(value))
  }, { immediate: true })

  const updateHandlers = new Set<() => void>()

  /**
   * Calls a function whenever search tokens have changed.
   *
   * @param fn - Callback function
   * @returns Cleanup function to unregister the callback
   */
  const onSearch = (fn: () => void) => {
    updateHandlers.add(fn)
    return () => updateHandlers.delete(fn)
  }

  const router = useRouter()
  watch(tokens, (value) => {
    const newQuery = compileTokens(value)
    if (props.updateUrl) {
      return router.replace({ query: { q: newQuery } })
    }

    // TODO (wvffle): updateUrl = false only in FilesTable.vue
    query.set(newQuery, false)
    for (const handler of updateHandlers) {
      handler()
    }
    // this.page = 1
    // this.fetchData()
  }, { deep: true })

  /**
   * Retrieves the value of a specific search token by its field key.
   *
   * @param key - The field name to search for (e.g., 'status', 'category')
   * @param fallback - Default value to return if the token is not found
   * @returns The token's value if found, otherwise the fallback value
   */
  const getTokenValue = (key: string, fallback: string) => {
    const matching = tokens.value.find(token => {
      return token.field === key
    })

    return matching?.value ?? fallback
  }

  /**
   * Adds or updates a search token with the specified field and value.
   *
   * If the value is empty, removes all tokens with the given field.
   * If tokens with the field already exist, updates their values.
   * If no tokens with the field exist, creates a new token.
   *
   * @param key - The field name for the search token
   * @param value - The value for the search token (empty string removes the token)
   */
  const addSearchToken = (key: string, value: string) => {
    if (value === '') {
      tokens.value = tokens.value.filter(token => {
        return token.field !== key
      })

      return
    }

    const existing = tokens.value.filter(token => {
      return token.field === key
    })

    if (!existing.length) {
      tokens.value.push({ field: key, value })
      return
    }

    for (const token of existing) {
      token.value = value
    }
  }

  return {
    getTokenValue,
    addSearchToken,
    onSearch,
    query: computed({
      get: () => compileTokens(tokens.value),
      set: (value: string) => query.set(value, true)
    })
  }
}
