<script setup lang="ts">
import { ref, computed, useSlots, onMounted, onUnmounted, nextTick } from 'vue'

import { type ColorProps, type VariantProps, type DefaultProps, type RaisedProps, type PastelProps, color } from '~/composables/color'
import { type WidthProps, width } from '~/composables/width'
import { type AlignmentProps, align } from '~/composables/alignment'

import Loader from '@ui/Loader.vue'

const props = defineProps<{
  thinFont?: true
  lowHeight?: true

  isActive?: boolean
  isLoading?: boolean

  shadow?: boolean
  round?: boolean
  icon?: string | `right ${string}`

  onClick?: (...args: any[]) => void | Promise<void> // The default fallback is `submit`

  split?: boolean // Add this prop for split button support
  splitIcon?: string // Add this prop for the split button icon
  splitTitle?: string // Add this prop
  onSplitClick?: (...args: any[]) => void | Promise<void> // Add click handler for split part
  dropdownOnly?: boolean

  disabled?: boolean

  autofocus?: boolean
  ariaPressed?: true
} & (ColorProps | DefaultProps | PastelProps)
  & VariantProps
  & RaisedProps
  & WidthProps
  & AlignmentProps>()

const slots = useSlots()

// TODO: Refactor this once upload button progress indicator can be tested (in Sidebar.vue)
const isIconOnly = computed(() =>
  !!props.icon
  && (!slots.default
    || ('square' in props && props.square)
    || ('squareSmall' in props && props.squareSmall)
  )
)

const isSplitIconOnly = computed(() => !!props.splitIcon && !props.splitTitle)

const internalLoader = ref(false)
const isLoading = computed(() => props.isLoading || internalLoader.value)

const fontWeight = props.thinFont ? 400 : 900

const button = ref()

const click = async (...args: any[]) => {
  internalLoader.value = true

  try {
    await props.onClick?.(...args)
  } finally {
    internalLoader.value = false
  }
}

const previouslyFocusedElement = ref()

onMounted(() => props.autofocus && nextTick(() => {
  previouslyFocusedElement.value = document.activeElement
  previouslyFocusedElement.value?.blur()
  button.value.focus()
}))

onUnmounted(() =>
  previouslyFocusedElement.value?.focus()
)
</script>

<template>
  <div
    v-if="split"
    class="funkwhale split-button"
  >
    <button
      v-if="!dropdownOnly"
      ref="button"
      v-bind="{
        ...$attrs,
        ...color(props, ['interactive'])(
          width(props, isIconOnly ? ['square'] : ['normalHeight', 'buttonWidth'])(
            align(props, { alignText: 'center' })(
            ))
        )
      }"
      class="funkwhale button split-main"
      :autofocus="autofocus || undefined"
      :disabled="disabled || undefined"
      :aria-pressed="props.ariaPressed"
      :class="{
        'is-loading': isLoading,
        'is-icon-only': isIconOnly,
        'has-icon': !!icon,
        'is-round': round,
        'is-shadow': shadow,
      }"
      @click="click"
    >
      <slot name="main">
        <i
          v-if="icon && !icon.startsWith('right ')"
          :class="['bi', icon]"
        />

        <span v-if="!isIconOnly">
          <slot />
        </span>

        <i
          v-if="icon && icon.startsWith('right ')"
          :class="['bi', icon.replace('right ', '')]"
        />
      </slot>
      <Loader
        v-if="isLoading"
        :container="false"
      />
    </button>
    <button
      v-bind="{
        ...$attrs,
        ...color(props, ['interactive'])(
          width(props, isSplitIconOnly ? ['square'] : ['normalHeight', 'buttonWidth'])(
            align(props, { alignSelf: 'start', alignText: 'center' })(
            )))
      }"
      :disabled="disabled || undefined"
      :autofocus="autofocus || undefined"
      :class="[
        'funkwhale',
        'button',
        {
          'split-toggle': true,
          'is-loading': isLoading,
          'is-icon-only': isSplitIconOnly,
          'has-icon': !!splitIcon,
          'is-round': round,
          'is-shadow': shadow
        }
      ]"
      @click="onSplitClick"
    >
      <span v-if="splitTitle">{{ splitTitle }}</span>
      <i :class="['bi', splitIcon]" />
    </button>
  </div>

  <!-- Not a split button -->

  <!-- TODO: Refactor button to require an accessible label in the props (either `label:string` or `hiddenLabel:string` for icon-only buttons) -->

  <button
    v-else
    ref="button"
    v-bind="color(props, ['interactive'])(
      width(props, isIconOnly ? ['square'] : ['normalHeight', 'buttonWidth'])(
        align(props, { alignText: 'center' })(
        )))"
    :disabled="disabled || undefined"
    :autofocus="autofocus || undefined"
    class="funkwhale button"
    :aria-label="isIconOnly ? icon : $attrs['aria-label'] ? $attrs['aria-label'] as string : ''"
    :aria-pressed="props.ariaPressed"
    :class="{
      'is-loading': isLoading,
      'is-icon-only': isIconOnly,
      'has-icon': !!icon,
      'is-round': round,
      'is-shadow': shadow,
    }"
    :type="onClick ? 'button' : 'submit' /* Prevents default `submit` if onCLick is set */"
    @click="click"
  >
    <i
      v-if="icon && !icon.startsWith('right ')"
      :class="['bi', icon]"
    />
    <span v-if="!isIconOnly">
      <slot />
    </span>
    <i
      v-if="icon && icon.startsWith('right ')"
      :class="['bi', icon.replace('right ', '')]"
    />
    <div
      v-if="isLoading"
      style="position: relative;"
    >
      <Loader
        :container="false"
        style="position: absolute;"
      />
    </div>
  </button>
</template>

<style lang="scss">
/*TODO: Check if we want to implement W3C recommended pointers (as Tailwind v4 is going that route, it's going to be the default again)*/

.funkwhale {
  &.split-button {
    cursor: var(--cursor, pointer);

    .button {
      display: inline-flex; // Ensure consistent display
      align-items: center;

      &.split-main {
        border-top-right-radius: 0;
        border-bottom-right-radius: 0;
        border-right: 1px solid var(--border-color);
      }

      &.split-toggle {
        border-top-left-radius: 0;
        border-bottom-left-radius: 0;
      }
    }
  }

  &.button {
    cursor: var(--cursor, pointer);

    // Layout

    --padding: 16px;
    --shift-by: 0.5px;
    gap: 8px;

    position: relative;
    display: inline-flex;
    white-space: nowrap;
    justify-content: space-between;
    align-items: center;

    &:not([disabled]) {
      cursor: pointer;
    }

    padding: calc(var(--padding) / 2 - var(--shift-by)) var(--padding) calc(var(--padding) / 2 + var(--shift-by)) var(--padding);

    &.is-icon-only {
      padding: var(--padding);
    }

    // Font

    font-family: var(--font-family);
    font-weight: v-bind(fontWeight);
    font-size: 14px;

    line-height: 14px;

    // Decoration

    transform: translateX(var(--fw-translate-x)) translateY(var(--fw-translate-y)) scale(var(--fw-scale));
    transition: all .2s ease;

    &.is-shadow {
      box-shadow: 0px 2px 4px 0px rgba(0, 0, 0, 0.2);
    }

    border-radius: var(--fw-border-radius);

    &.is-round {
      border-radius: 100vh;
    }

    // States

    &[disabled] {
      font-weight: normal;
      pointer-events: none;
    }

    &.is-loading {
      @extend :active !optional;

      >span {
        opacity: 0;
      }
    }

    // Content

    >span {
      position: relative;
      top: calc(0px - var(--shift-by));
    }

    // Icon

    >i.bi {
      font-size: 18px;
      margin: -2px 0;

      &.large {
        font-size: 32px;
        margin: -8px 0;
      }
    }

    &.is-icon-only i.bi {
      margin: -6px;

      &.large {
        margin: -8px;
      }
    }

    &:has(>i) {
      gap: 10px;
    }
  }
}
</style>
