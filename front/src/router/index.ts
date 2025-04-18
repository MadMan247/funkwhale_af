import { useLocalStorage } from '@vueuse/core'
import { createRouter, createWebHistory } from 'vue-router'
import { forceInstanceChooser } from './guards'

import routesV1 from './routes'
import routesV2 from '~/ui/routes'

// TODO:
// Research...
// - "What is the use case for this toggle?"
// - "Is Local Storage (persistence on a specific browser
//    on a specific machine) the right place?"
const isUIv2 = useLocalStorage('ui-v2', true)
const routes = isUIv2.value ? routesV2 : routesV1

const router = createRouter({
  history: createWebHistory(import.meta.env.VUE_APP_ROUTER_BASE_URL as string ?? '/'),
  linkActiveClass: 'active',
  routes,

  scrollBehavior (to, from, savedPosition) {
    if (to.meta.preserveScrollPosition) {
      return savedPosition ?? { left: 0, top: 0 }
    }

    return new Promise(resolve => {
      setTimeout(() => {
        if (to.hash) {
          resolve({ el: to.hash, behavior: 'smooth' })
        }

        resolve(savedPosition ?? { left: 0, top: 0 })
      }, 100)
    })
  }
})

router.beforeEach((to, from, next) => {
  return forceInstanceChooser(to, from, next)
})

export default router
