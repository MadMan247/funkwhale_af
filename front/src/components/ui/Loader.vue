<script setup lang="ts">
const { container = true } = defineProps<{ container?: boolean }>()
</script>

<template>
  <div
    v-if="container"
    class="funkwhale loader-container"
  >
    <div class="funkwhale">
      <div class="loader" />
    </div>
  </div>

  <div
    v-else
    class="funkwhale"
  >
    <div class="loader" />
  </div>
</template>

<style lang="scss">
@import './loader.scss'
</style>
