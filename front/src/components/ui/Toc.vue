<script setup lang="ts">
import { computed, ref, watchEffect } from 'vue'
import { slugify } from 'transliteration'
import { useScroll } from '@vueuse/core'

import Button from '~/components/ui/Button.vue'

const { heading = 'h1' } = defineProps<{heading?:'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6'}>()

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
@import './toc.scss'
</style>
