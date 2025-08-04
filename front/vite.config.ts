import { visualizer } from 'rollup-plugin-visualizer'
import { defineConfig, type PluginOption } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'
import { fileURLToPath, URL } from 'node:url'



import manifest from './pwa-manifest.json'

import VueI18n from '@intlify/unplugin-vue-i18n/vite'
import Vue from '@vitejs/plugin-vue'
import { nodePolyfills } from 'vite-plugin-node-polyfills'
import vueDevTools from 'vite-plugin-vue-devtools'


// We don't use port but, magically, it is necessary to set it here.
const port = +(process.env.VUE_PORT ?? 8080)

// To prevent a linter warning, here is a partial Haiku:
export const exPort = port

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  envPrefix: ['VUE_', 'TAURI_', 'FUNKWHALE_SENTRY_'],
  plugins: [
    // https://github.com/vitejs/vite/tree/main/packages/plugin-vue
    Vue(),

    // https://github.com/intlify/bundle-tools/tree/main/packages/vite-plugin-vue-i18n
    VueI18n({
      include: fileURLToPath(new URL('./src/locales/**', import.meta.url))
    }),

    // https://github.com/btd/rollup-plugin-visualizer
    visualizer() as unknown as PluginOption,

    // https://github.com/antfu/vite-plugin-pwa
    VitePWA({
      strategies: 'injectManifest',
      srcDir: 'src',
      filename: 'serviceWorker.ts',
      manifestFilename: 'manifest.json',
      devOptions: {
        enabled: true,
        type: 'module',
        navigateFallback: 'index.html'
      },
      manifest
    }),

    // https://github.com/davidmyersdev/vite-plugin-node-polyfills
    // see: https://github.com/Borewit/music-metadata-browser/issues/836
    nodePolyfills(),


    vueDevTools()
  ],
  server: {
    port: +(process.env.VUE_PORT ?? 8080),
    watch: {
      usePolling: true
    },
    allowedHosts: [".funkwhale.test"],
    hmr: {
      overlay: false
    }
  },
  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia', 'axios', 'lodash-es'],
    exclude: ['@sentry/vue', '@sentry/tracing']
  },
  resolve: {
    alias: [
      { find: '#', replacement: fileURLToPath(new URL('./src/ui/workers', import.meta.url)) },
      { find: '?', replacement: fileURLToPath(new URL('./test', import.meta.url)) },
      { find: '~', replacement: fileURLToPath(new URL('./src', import.meta.url)) }
    ]
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `
          $docs: ${!!process.env.VP_DOCS};
          @use "~/style/_vars" as *;
          @import "~/style/inc/theme";
          @import "~/style/funkwhale";
        `
      }
    }
  },
  esbuild: {
    target: mode === 'development' ? 'esnext' : 'es2020',
    supported: {
      'top-level-await': true
    }
  },
  build: {
    target: mode === 'development'
      ? 'esnext'
      : ['es2020', 'chrome87', 'firefox78', 'safari14', 'edge88'],
    sourcemap: true,
    minify: mode === 'development' ? false : 'esbuild',
    // https://rollupjs.org/configuration-options/
    rollupOptions: {
      output: mode === 'production' ? {
        manualChunks: {
          axios: ['axios', 'axios-auth-refresh'],
          dompurify: ['dompurify'],
          lodash: ['lodash-es'],
          moment: ['moment'],
          sentry: ['@sentry/vue', '@sentry/tracing'],
          'standardized-audio-context': ['standardized-audio-context'],
          'vue-router': ['vue-router']
        }
      } : {}
    }
  },
  test: {
    environment: 'jsdom',
    globals: true,
    reporters: ['default', 'junit'],
    outputFile: './test_results.xml',
    coverage: {
      src: './src',
      all: true,
      reporter: ['text', 'cobertura']
    },
    setupFiles: [
      './test/setup/mock-server.ts',
      './test/setup/mock-audio-context.ts',
      './test/setup/mock-vue-i18n.ts',
      './test/setup/mock-lru-cache.ts'
    ]
  }
}))
