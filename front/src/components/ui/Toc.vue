<script setup lang="ts">
import { computed, ref, watchEffect, onMounted, useTemplateRef } from 'vue'
import { slugify } from 'transliteration'
import { useDebounceFn, useEventListener } from '@vueuse/core'

import Button from '~/components/ui/Button.vue'

const { heading = 'h1' } = defineProps<{ heading?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6' }>()

const toc = useTemplateRef('toc');
const links = useTemplateRef('links');

const headings = computed(() => Array.from(toc.value?.querySelectorAll(heading) ?? []))

watchEffect(() => {
  for (const heading of headings.value) {
    heading.id = slugify(heading.textContent)
  }
})

const activeHeading = ref<HTMLElement>()

const setActiveHeading = (id:string)  => {
  activeHeading.value = headings.value.find(({id: headingId}) =>headingId === id)
}

const findActiveHeading = () => {
   activeHeading.value = headings.value.find((heading_, index, array) =>
     array.length === 1 ? true
     : ( index === 0
       ? array[index+1].getBoundingClientRect().top>=magicHeight
       : heading_.getBoundingClientRect().top<magicHeight
     )
    &&  ( index >= array.length-1
    ? true
    : array[index+1].getBoundingClientRect().bottom>=magicHeight
    )
  )
}

/** Headings at this height count as selected */
const magicHeight = 200

const topOfActive = ref<number>(0);

const debouncedFn = useDebounceFn(() => {
  console.log("activeHeading if", activeHeading.value?.id)
  console.log("activeHeading top", activeHeading.value?.getBoundingClientRect()?.top)
  console.log("activeHeading bottom", activeHeading.value?.getBoundingClientRect()?.bottom)
  console.log("links top", links.value?.getBoundingClientRect()?.top)
  console.log("links bottom", links.value?.getBoundingClientRect()?.bottom)
  // Is the currently selected out of bounds?
  const { top, bottom } = activeHeading.value?.getBoundingClientRect() ?? { top: magicHeight, bottom:magicHeight };
  topOfActive.value = top-(links.value?.getBoundingClientRect().top || 0);
  const isInsideBounds
    = bottom > (links.value?.getBoundingClientRect().top || 0)
    && top<(links.value?.getBoundingClientRect()?.bottom || 1000)

  if (isInsideBounds) return;

  findActiveHeading()
}, 15)

onMounted(() => {
  const findScrollContainer = (element: HTMLElement) => {
    if (!element) {
      return undefined;
    }

    let parent = element.parentElement;
    while (parent) {
      const { overflow } = window.getComputedStyle(parent);
      if (overflow.split(' ').every(o => o === 'auto' || o === 'scroll')) {
        return parent;
      }
      parent = parent.parentElement;
    }

    return document.documentElement;
  };
  useEventListener(findScrollContainer(toc.value as HTMLDivElement), 'scroll', debouncedFn)
  findActiveHeading()
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
      <div
        ref="links"
        class="toc-links"
      >
        <Button
          v-for="h of headings"
          :key="h.id"
          :class="{ 'is-active': activeHeading?.id === h.id }"
          @click.prevent="activeHeading = h; h.scrollIntoView({ behavior: 'smooth' })"
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
    grid-template-columns: 1fr max-content;
    gap: 1rem;

    > .toc-toc {
      border-left: 1px solid var(--fw-border-color);
      width: max-content;

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
