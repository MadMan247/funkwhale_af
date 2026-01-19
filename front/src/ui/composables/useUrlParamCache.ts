import { watch, onScopeDispose, onMounted, computed, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const cache = reactive<Record<string, string>>({})

/**
 * Caches a URL parameter in memory and restores it (at mount-time) if missing. Useful for preserving filters and tabs across navigation.
 * Only use in component `<script setup>` blocks. While the component is mounted, the cache stays in sync with the URL parameter.
 *
 * @param param - URL parameter to cache
 * @param config - Optional fallback value to cache something if nothing is cached or present in the URL yet
 * @example `useUrlParamCache('library', 'me')`
 * @returns a computed ref with the cached value
 */

export default function useUrlParamCache(
  param: string,
  config?: { fallback: string|number }
) {

  onMounted(async () => {
    const router = useRouter()
    const route = useRoute()

    await router.isReady()

    const getParam = () => {
        const v = route.query[param]
        return Array.isArray(v) ? v[0] : v
    }
    const current = getParam()

    // Restore parameter if missing
    if (current === undefined || current === null || current === '') {
      let mem = cache[`url-param-cache:${param}`]
      // Cache fallback value if nothing is cached yet
      if (mem === undefined && config?.fallback !== undefined) {
        mem = String(config.fallback)
        cache[`url-param-cache:${param}`] = mem
      }
      // Restore parameter from cache
      if (mem !== undefined) {
        const location = route.name ? {
          name: route.name as any,
          params: { ...route.params },
          query: { ...route.query, [param]: mem }
        } : {
          path: route.path,
          query: { ...route.query, [param]: mem }
        }

        let remove: () => void = () => {}
        remove = router.afterEach(async (to) => {
          try {
            if (!to.query[param]) {
              await router.replace(location)
              // wait a tick for the router's reactive currentRoute to update
              await new Promise(r => setTimeout(r, 0))
            }
          } finally {
            remove()
          }
        })
      }
    }

    // Start watcher after any replace so `immediate: true` sees the final state.
    const stop = watch(getParam, v => {
        if (v === null || v === undefined || v === '') return
        cache[`url-param-cache:${param}`] = v
      },
      { immediate: true }
    )

    onScopeDispose(stop)
  })

  return computed(() => cache[`url-param-cache:${param}`])
}
