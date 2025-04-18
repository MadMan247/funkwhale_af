<script setup lang="ts">
import PopoverItem from './PopoverItem.vue'

const value = defineModel<boolean>('modelValue', { required: true })
</script>

<template>
  <PopoverItem
    class="checkbox"
    @click="value = !value"
  >
    <i :class="['bi', value ? 'bi-record-circle' : 'bi-circle']" />
    <slot />

    <template #after>
      <slot name="after" />
    </template>
  </PopoverItem>
</template>
