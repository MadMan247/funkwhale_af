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

<style lang="css">
.funkwhale {
  &.options-button {
    will-change: transform;
    transition: all .2s ease;
    font-size: 0.6rem !important;
    padding: 0.6em;
    &.is-ghost {
      position: absolute;
      bottom: 0px;
      right: 0px;
    }
  }
}

</style>
