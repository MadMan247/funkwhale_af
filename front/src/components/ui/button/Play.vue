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
@import './play.scss';
</style>
