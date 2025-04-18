<script setup lang="ts">
import { useStore } from '~/store'

const store = useStore()
</script>

<template>
  <div class="ui toast-container">
    <message
      v-for="message in store.state.ui.messages"
      :key="message.key"
      :message="message"
    />
    <slot />
  </div>
</template>
