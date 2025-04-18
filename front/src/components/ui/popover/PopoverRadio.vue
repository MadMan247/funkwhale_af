<script setup lang="ts">
import PopoverRadioItem from './PopoverRadioItem.vue'

import { computed } from 'vue'

const { choices } = defineProps<{ choices:string[] }>()

const filteredChoices = computed(() => new Set(choices))

const value = defineModel<string>('modelValue', { required: true })

// NOTE: Due to the usage of a ref inside a Proxy, this is reactive.
const choiceValues = new Proxy<Record<string, boolean>>(Object.create(null), {
  get (_, key) {
    return key === value.value
  },

  set (_, key, val) {
    if (!val || typeof key === 'symbol') return false

    value.value = key
    return true
  }
})
</script>

<template>
  <PopoverRadioItem
    v-for="choice of filteredChoices"
    :key="choice"
    v-model="choiceValues[choice]"
  >
    {{ choice }}
  </PopoverRadioItem>
</template>
