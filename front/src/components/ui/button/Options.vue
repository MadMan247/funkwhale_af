<script setup lang="ts">
import Button from '../Button.vue'

defineProps<{
  isSquare?: boolean
  isGhost?: boolean
  isSquareSmall?: boolean
}>()
</script>

<template>
  <Button
    icon="bi-three-dots-vertical"
    v-bind="$attrs"
    :class="['options-button', {'is-ghost': isGhost}]"
    :secondary="!isGhost"
    :ghost="isGhost"
    :round="!isSquare && !isSquareSmall"
    :square-small="isSquareSmall"
  />
</template>

<style lang="scss">
@import './options.scss'
</style>
