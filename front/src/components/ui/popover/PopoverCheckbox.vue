<script setup lang="ts">
import PopoverItem from './PopoverItem.vue'

const value = defineModel<boolean>()
</script>

<template>
  <PopoverItem
    class="checkbox"
    :keep-open="true"
    @click="value = !value"
  >
    <i :class="['bi', value ? 'bi-check-square' : 'bi-square']" />
    <slot />

    <template #after>
      <slot name="after" />
    </template>
  </PopoverItem>
</template>
