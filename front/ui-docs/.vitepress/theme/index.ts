import { createI18n } from 'vue-i18n'

import DefaultTheme from 'vitepress/theme'
import type { App } from 'vue'
import './style.css'
import en_US from '../../../src/locales/en_US.json'

import VueDOMPurifyHTML from 'vue-dompurify-html'

import { createMemoryHistory, createRouter, createWebHistory } from 'vue-router'

// Satisfy Vue router for fake links
const CatchAll = { render: () => null };

export default {
  ...DefaultTheme,
  enhanceApp({ app }: { app: App }) {
    const i18n = createI18n({
      legacy: false,
      locale: 'en_US',
      fallbackLocale: 'en_US',
      messages: { en_US }
    })

    const router = createRouter({
      history: import.meta.env!.SSR
      ? createMemoryHistory()
      : createWebHistory('/'),
      routes: [
        {
          path: '/:pathMatch(.*)*',
          name: 'CatchAll',
          component: CatchAll,
        }]
    })

    // Simsalabim: Incantation for a confused i18n... Thank you s-ol https://github.com/vikejs/vike/discussions/1778#discussioncomment-10192261
    if (!('__VUE_PROD_DEVTOOLS__' in globalThis)) {
      (globalThis as any).__VUE_PROD_DEVTOOLS__ = false;
    }
    app.use(i18n)
    app.use(router)
    app.use(VueDOMPurifyHTML);

    if (typeof document !== 'undefined' && document?.body) {
    // Necessary classes for funkwhale theme to take effect
      document.body.classList.add('funkwhale', 'default')
      // A11y fix: Add a landmark to the page content container
      const observer = new MutationObserver((mutationsList, observer) => {
        document.getElementById("VPContent")?.setAttribute("role", "main")
      })
      observer.observe(document.body, { childList: true, subtree: true })
    }
  }
}
