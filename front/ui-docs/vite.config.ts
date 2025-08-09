import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vueDevTools from 'vite-plugin-vue-devtools'
import path from 'node:path'

export default defineConfig({
  plugins: [vueDevTools()],
  publicDir: false,
  resolve: {
    alias: {
      '~': fileURLToPath(new URL('../src', import.meta.url)),
      '#': fileURLToPath(new URL('../src/ui/workers', import.meta.url)),
      '/node_modules': fileURLToPath(new URL('../node_modules', import.meta.url))
    }
  },

  css: {
    devSourcemap: true,
    preprocessorOptions: {
      scss: {
        additionalData: `
          $docs: ${!!process.env.VP_DOCS};
          @import "~/style/inc/docs.scss";
        `
      }
    }
  },
  build: {
    rollupOptions: {
      external: ['vue', 'vue-i18n', '@vueuse/core', 'vue-router', 'vue-devtools'],
      output: {
        globals: {
          Vue: 'vue'
        }
      }
    }
  }
})
