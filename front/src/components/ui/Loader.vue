<script setup lang="ts">
const { container = true } = defineProps<{ container?: boolean }>()

// TODO: Revisit this. For now, normal loaders as displayed without any container over the next higher non-`static`-positioned element while `container="false` loaders are positioned in-place.
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
@use '~/style/funkwhale.scss';

.funkwhale {
  &:not(:has(>.loader-container)):has(>.loader) {
      position: relative;
      margin-bottom: 100%;
  }
  &.loader-container {
    position: relative;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
  }
}

.loader-container {
  position: relative;
}

.loader,
.loader:after {
  border-radius: 50%;
  width: 1.5em;
  height: 1.5em;
}

.loader {
  border-radius: 50%;
  animation: spin 0.6s linear 8; /* spin 8x, i.e. 4.9s ;-) */

  font-size: 1.2em;
  position: absolute;
  left: 50%;
  top: 50%;
  margin-left: -0.75em;
  margin-top: -0.75em;
  text-indent: -9999em;

  @include funkwhale.light-theme {
    border-top: 0.2em solid rgba(0, 0, 0, 0.2);
    border-right: 0.2em solid rgba(0, 0, 0, 0.2);
    border-bottom: 0.2em solid rgba(0, 0, 0, 0.2);
    border-left: 0.2em solid rgba(0, 0, 0, 0.7);
  }

  @include funkwhale.dark-theme {
    border-top: 0.2em solid rgba(255, 255, 255, 0.2);
    border-right: 0.2em solid rgba(255, 255, 255, 0.2);
    border-bottom: 0.2em solid rgba(255, 255, 255, 0.2);
    border-left: 0.2em solid rgba(255, 255, 255, 0.7);
  }
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}
</style>
