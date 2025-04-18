<script setup lang="ts">
import { type TabProps, TABS_INJECTION_KEY } from '~/injection-keys'
import { whenever } from '@vueuse/core'
import { inject, ref } from 'vue'

const props = defineProps<TabProps>()

const { currentTitle, tabs } = inject(TABS_INJECTION_KEY, {
  currentTitle: ref(props.title),
  tabs: []
})

whenever(() => !tabs.some(tab => props.title === tab.title), () => {
  tabs.push(props)
}, { immediate: true })
</script>

<template>
  <div
    v-if="currentTitle === title"
    class="tab-content"
  >
    <slot />
  </div>
</template>
