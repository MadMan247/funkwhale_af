import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vueDevTools from 'vite-plugin-vue-devtools'
import { sassFalse, sassTrue } from 'sass-embedded'

export default defineConfig({
  plugins: [vueDevTools()],
  publicDir: false,
  resolve: {
    alias: {
      '#': fileURLToPath(new URL('../src/ui/workers', import.meta.url)),
      '?': fileURLToPath(new URL('../test', import.meta.url)),
      '~': fileURLToPath(new URL('../src', import.meta.url)),
      '@ui': fileURLToPath(new URL('../src/components/ui', import.meta.url)),
      '@': fileURLToPath(new URL('./', import.meta.url))
    }
  },

  css: {
    devSourcemap: true,
    preprocessorOptions: {
      scss: {
        functions: {
          'docs()': () => (!!process.env.VP_DOCS) ? sassTrue : sassFalse
        },
        additionalData: `
          @use "~/style/inc/docs.scss";
        `
      }
    }
  },
  build: {
    rolldownOptions: {
      external: ['vue', 'vue-i18n', '@vueuse/core', 'vue-router', 'vue-devtools'],
      output: {
        globals: {
          Vue: 'vue'
        }
      }
    }
  }
})
