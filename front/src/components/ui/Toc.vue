<script setup lang="ts">
import { computed, ref, watchEffect } from 'vue'
import { slugify } from 'transliteration'
import { useScroll } from '@vueuse/core'

import Button from '@ui/Button.vue'

const { heading = 'h1' } = defineProps<{ heading?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6' }>()

const toc = ref()

const headings = computed(() => toc.value?.querySelectorAll(heading) ?? [])
watchEffect(() => {
  for (const heading of headings.value) {
    heading.id = slugify(heading.textContent)
  }
})

const activeLink = ref()
const { y } = useScroll(window)
watchEffect(() => {
  let lastActive = headings.value[0]
  for (const heading of headings.value) {
    if (y.value > heading.offsetTop) {
      lastActive = heading
    }
  }

  activeLink.value = lastActive?.id
})
</script>

<template>
  <div
    ref="toc"
    class="funkwhale toc"
  >
    <div class="toc-content">
      <slot />
    </div>

    <div class="toc-toc">
      <div class="toc-links">
        <Button
          v-for="h of headings"
          :key="h.id"
          :class="{ 'is-active': activeLink === h.id }"
          @click.prevent="h.scrollIntoView({ behavior: 'smooth' })"
        >
          {{ h.textContent }}
        </Button>
      </div>
    </div>
  </div>
</template>

<style lang="scss">
@use '~/style/funkwhale.scss';

.funkwhale {
  &.toc {
    > .toc-toc > .toc-links > button {
      --fw-link-color: var(--fw-text-color) !important;

      &.is-active::before {
        background-color: var(--fw-secondary);
      }
    }

    @include funkwhale.light-theme {
      --fw-border-color: var(--fw-gray-300);
    }

    @include funkwhale.dark-theme {
      --fw-border-color: var(--fw-gray-700);

      > .toc-toc > .toc-links > button {
        --fw-text-color: var(--fw-gray-300);
      }
    }

    display: grid;
    grid-template-columns: 1fr 280px;
    gap: 1rem;

    > .toc-toc {
      border-left: 1px solid var(--fw-border-color);

      > .toc-links {
        position: sticky;
        top: 0;

        padding-left: 8px;

        /* @include docs {
          top: 72px;
        } */

        > button {
          position: relative;
          font-size: 1rem;
          padding: 4px 8px 4px 11px;
          display: block;
          width: 100%;
          text-align: left;

          &.is-active {
            font-weight: 900;

            &::before {
              content: '';
              width: 4px;
              height: 100%;
              position: absolute;
              right: 100%;
              top: 0;
              border-radius: 100vh;
            }
          }
        }
      }
    }
  }
}
</style>
