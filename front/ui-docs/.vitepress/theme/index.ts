import { createI18n } from 'vue-i18n'

import DefaultTheme from 'vitepress/theme'
import en from '../../../src/locales/en_US.json'

import Theme from './Theme.vue'
import VueDOMPurifyHTML from 'vue-dompurify-html';

import { createRouter, createWebHistory } from 'vue-router'

import routesV2 from '../../../src/ui/routes'

const routes = routesV2

export default {
  ...DefaultTheme,
  Theme: Theme,
  enhanceApp({ app }) {
    const i18n = createI18n({
      legacy: false,
      locale: 'en',
      fallbackLocale: 'en',
      messages: { en }
    })

    const router = createRouter({
      history: createWebHistory('/'),
      linkActiveClass: 'active',
      routes,

      scrollBehavior (to, _, savedPosition) {
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

    // Simsalabim: Incantation for a confused i18n... Thank you s-ol https://github.com/vikejs/vike/discussions/1778#discussioncomment-10192261
    if (!('__VUE_PROD_DEVTOOLS__' in globalThis)) {
      (globalThis as any).__VUE_PROD_DEVTOOLS__ = false;
    }
    app.use(i18n)
    app.use(router)
    app.use(VueDOMPurifyHTML);
  }
}
