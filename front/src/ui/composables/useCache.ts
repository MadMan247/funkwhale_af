import { computed, ref } from 'vue'

export const allCaches = ref<Map<unknown, unknown>[]>([]);

/**
 * Initialize a forgetful, reactive key-value store.
 *
 * @param retention: Milliseconds until a datum is deleted
 * @returns a factory for reactive values by key
 */
export const useCache = <K, V>({ retention }: { retention: number }) => {
  const cache = new Map<K, V>()

  allCaches.value.push(cache);

  return (key: K) => computed({
    get() {
      return cache.get(key)
    },
    set(value: V) {
      cache.set(key, value);
      setTimeout(() => cache.delete(key), retention)
    }
  })
}
