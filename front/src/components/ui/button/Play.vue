<script setup lang="ts">
import Button from '../Button.vue'

const play = defineEmits(['play'])
</script>

<template>
  <Button
    icon="bi-play-fill"
    class="play-button"
    shadow
    round
    @click="$emit('play')"
  />
</template>

<style lang="scss">
@use '~/style/funkwhale.scss';

.funkwhale {
  &.play-button {

    @include funkwhale.light-theme {
      --fw-bg-color: var(--fw-red-010) !important;
      --fw-text-color: var(--fw-gray-600) !important;

      &:hover {
        --fw-text-color: var(--fw-pastel-4, var(--fw-primary)) !important;
      }
    }

    @include funkwhale.dark-theme {
      --fw-bg-color: var(--fw-gray-800) !important;
      --fw-text-color: var(--fw-gray-300) !important;

      &:hover {
        --fw-text-color: var(--fw-pastel-2, var(--fw-blue-400)) !important;
      }
    }

    will-change: transform;
    font-size: 0.6rem !important;
    padding: 0.625em !important;
    border: 0px !important;

    i {
      font-size: 2rem;

      &::before {
        transform: translateX(1px);
        backface-visibility: hidden;
      }
    }

    &:hover {
      --fw-scale: 1.091;
    }
  }
}

</style>
