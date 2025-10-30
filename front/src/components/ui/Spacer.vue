<script setup lang="ts">
import { ref, watchEffect } from 'vue'

type Size = 'no-size' | `size-${'4' | '8' | '12' | '16' | '20' | '32' | '46' | '64'}`

const props = defineProps<{
  grow?:true;
  shrink?:true;
  title?:string;
} & { [Direction in 'h' | 'v']? : true }
  &({ [S in Size]? : true } | {size?:number})>()

const minSize = 0

const measure = ref()

watchEffect(() => {
  const maybeSize = Object.entries(props).find(
    ([key, value]) => value === true && key.startsWith('size'))
  const size
    = maybeSize
      ? +(maybeSize[0].replace('size', ''))
      : 'size' in props && props.size
        ? props.size
        : 'noSize' in props && props.noSize
          ? 0
          : 32
  measure.value = {
    size: `${Math.max(size, minSize)}px`,
    margin: `${(size - Math.max(size, minSize)) / 2}px`
  }
})
</script>

<template>
  <div :class="[$style.spacer, grow && 'grow', title && $style['has-title']]">
    <slot />
  </div>
</template>

<style module lang="scss">
.spacer {
  width: v-bind('props.v ? 0 : measure.size');
  height: v-bind('props.h ? 0 : measure.size');
  margin: v-bind('measure.margin');
  flex-grow: v-bind('grow ? 1 : 0');
  flex-shrink: v-bind('shrink ? 1 : 0');
  transition: flex-grow .2s, flex-shrink .2s;

  position: relative;

  &.has-title::after {
    position: absolute;
    inset: calc(50% - 1em);
    content: v-bind('`"${title}"`')
  }

  @if docs() {
    animation: blink .7s 1;
    @keyframes blink { 50% {
      outline: 2px dashed var(--fw-secondary);
      outline-offset: v-bind('measure.margin');
    } }
    &:hover {
      animation-iteration-count: infinite;
    }
  }
  @else {
    pointer-events: none;
  }
}
</style>
