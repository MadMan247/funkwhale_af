<script setup lang="ts">
import { inject, ref, watchEffect } from 'vue'
import { POPOVER_CONTEXT_INJECTION_KEY } from '~/injection-keys'

import Popover from '../Popover.vue'
import PopoverItem from './PopoverItem.vue'

const context = inject(POPOVER_CONTEXT_INJECTION_KEY, {
  items: ref(0),
  hoveredItem: ref(-2)
})

const isOpen = ref(false)
const id = ref(-1)
watchEffect(() => {
  isOpen.value = context.hoveredItem.value === id.value
})
</script>

<template>
  <Popover
    v-model="isOpen"
    positioning="horizontal"
  >
    <PopoverItem
      :parent-popover-context="context"
      class="submenu"
      @click="isOpen = !isOpen"
      @internal:id="id = $event"
    >
      <slot />

      <template #after>
        <slot name="after">
          <i class="bi bi-chevron-right" />
        </slot>
      </template>
    </PopoverItem>

    <template #items>
      <slot name="items" />
    </template>
  </Popover>
</template>
