<script setup lang="ts">
import { color } from '~/composables/color'

// TODO: Rename `big` to `large` for parity with large icons, and design appropriate tokens for consistency and customization (theming)
const { big } = defineProps<{
  big?: boolean
  label: string
}>()

const isOn = defineModel<boolean>()
const diameter = big ? '28px' : '20px'
</script>

<template>
  <label
    :class="[$style.toggle, 'funkwhale']"
    v-bind="color({}, ['interactive', 'raised'])"
    :checked="isOn || undefined"
  >
    <input
      v-model="isOn"
      type="checkbox"
      style="opacity: 0; /* Hide even before stylesheet is loaded */"
    >
    <!-- TODO: Consider refactoring to use slot instead of label for feature parity with other labeled components -->
    <!-- TODO: Document layout quirks when combining with multi-row components (e.g. labeled input, pills) in a toolbar-style row -->
    <span>{{ label }}</span>
  </label>
</template>

<style module lang="scss">
.toggle {
  font-size: 14px;
  font-weight: 600;
  line-height: 1em;
  position: relative;
  padding: calc(var(--padding) - 1px) 0 calc(var(--padding) + 1px) 0;
  min-width: calc(var(--diameter) * 2);
  height: min-content;

  --diameter: v-bind(diameter);
  --lineWidth: 2px;
  --padding: 10px;

  --void-color: var(--void-off-background-color);
  --pin-color: var(--void-off-pin-color);

  &[checked] {
    --void-color: var(--void-on-background-color);
    --pin-color: var(--void-on-pin-color);

    &::after {
      transform: translateX(var(--diameter));
    }
  }

  &:hover,
  &:has(:focus-visible) {
    --void-color: var(--void-off-hover-background-color);
    --pin-color: var(--void-off-hover-pin-color);

    &[checked] {
      --void-color: var(--void-on-hover-background-color);
      --pin-color: var(--void-on-hover-pin-color);
    }
  }

  &::before,
  &::after {
    content: '';
    position: absolute;
    border-radius: var(--diameter);
  }

  &::before {
    height: var(--diameter);
    aspect-ratio: 2;
    background-color: var(--void-color);
    left: 0;
    top: calc(var(--padding) * 2 - var(--diameter) / 2);
  }

  &::after {
    height: calc(var(--diameter) - var(--lineWidth) * 2);
    aspect-ratio: 1;
    background-color: var(--pin-color);
    left: var(--lineWidth);
    top: calc(var(--padding) * 2 - var(--diameter) / 2 + var(--lineWidth));
    transition: all .2s;
  }

  >span {
    padding-left: calc(var(--diameter) * 2 - 12px);
  }
}
</style>
