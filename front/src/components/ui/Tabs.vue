<script setup lang="ts">
import { type TabProps, TABS_INJECTION_KEY } from '~/injection-keys'
import { computed, provide, reactive, ref, watch } from 'vue'

import Button from '~/components/ui/Button.vue'
import Link from '~/components/ui/Link.vue'
import { useRoute } from 'vue-router'

const currentTitle = ref<TabProps['title']>('')
const tabs = reactive<TabProps[]>([])
const currentRoute = useRoute()

provide(TABS_INJECTION_KEY, {
  currentTitle,
  tabs
})

/* Note that this only compares the name. Make sure to add a `name` field to identify paths in your router config! */
const actualCurrentTitle = computed(() =>
  tabs.find(({ to }) => to && typeof to !== 'string' && 'name' in to && currentRoute.name === to?.name)?.title
  || currentTitle.value)

const currentIndex = computed(() =>
  tabs.findIndex(({ title }) => title === actualCurrentTitle.value)
)

// select first tab
watch(tabs, () => {
  if (tabs.length === 1) {
    currentTitle.value = tabs[0].title
  }
})
</script>

<template>
  <div class="funkwhale tabs">
    <div class="tabs-header">
      <component
        :is="tab.to ? Link : Button"
        v-for="tab in tabs"
        :key="tab.title"
        ghost
        :class="{ 'is-active': actualCurrentTitle === tab.title }"
        v-bind="tab"
        :on-click="'to' in tab ? undefined : () => { currentTitle = tab.title }"
        class="tabs-item"
        @keydown.left="currentTitle = tabs[(currentIndex - 1 + tabs.length) % tabs.length].title"
        @keydown.right="currentTitle = tabs[(currentIndex + 1) % tabs.length].title"
      >
        <div class="is-spacing">
          {{ tab.title }}
        </div>
        <label>{{ tab.title }}</label>
      </component>

      <div class="tabs-right">
        <slot name="tabs-right" />
      </div>
    </div>

    <slot />
  </div>
</template>

<style lang="scss">
@import './tabs.scss'
</style>
