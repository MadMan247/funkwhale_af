import type { App } from 'vue'
import type { VueStore } from '@rstore/vue'
import type { InjectionKey } from 'vue'
import { inject } from 'vue'

import { createStore } from '@rstore/vue'
import { models } from './model'
import funkwhale from './plugin'

const injectStoreKey = Symbol('rstore') as InjectionKey<VueStore<typeof models>>

/**
Normalized reactive cache for remote objects
- Offline-first cache (WIP)
- Rate limited fetching per query -> ./plugin.ts
- Declarative normalization -> ./model.ts

TODO: Migrate all imperative `axios` calls to use rstore refs
- store.users.queryMany()
- store.users.queryFirst(key)

Documentation: https://rstore.dev/guide
*/
export async function rstore(app: App) {
  const store = await createStore({
    models,
    plugins: [
      funkwhale
    ],

    findDefaults: {
      fetchPolicy: 'cache-and-fetch'
    }
  })

  store.$cache.clear()

  app.provide(injectStoreKey, store)
}

export function useStore() {
  const store = inject(injectStoreKey, null)
  if (store == null) {
    throw new Error('No rstore provided.')
  }
  return store
}
