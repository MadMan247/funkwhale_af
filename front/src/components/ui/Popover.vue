<script setup lang="ts">
import { computed, ref, inject, provide, shallowReactive, watch, onScopeDispose } from 'vue'
import { whenever, useElementBounding, onClickOutside, refDebounced } from '@vueuse/core'

import { isMobileView, useScreenSize } from '~/composables/screen'
import { POPOVER_INJECTION_KEY, POPOVER_CONTEXT_INJECTION_KEY } from '~/injection-keys'
import { type ColorProps, type DefaultProps, type RaisedProps, color } from '~/composables/color'

/* TODO: Basic accessibility

-> See ui-docs

*/

const isOpen = defineModel<boolean>({ default: false })

// Delay closing by 300ms, but allow immediate closing
const shouldDelayClose = ref(true)
const isOpenDelayed = refDebounced(isOpen, () => isOpen.value ? 0 : (shouldDelayClose.value ? 300 : 0))

const { positioning = 'vertical', ...colorProps } = defineProps<{
  positioning?: 'horizontal' | 'vertical'
} & (ColorProps | DefaultProps) & RaisedProps>()

// Template refs
const popover = ref()
const slot = ref()
const inSlot = ref()

// Click outside
const mobileClickOutside = (event: MouseEvent) => {
  const inPopover = !!(event.target as HTMLElement).closest('.funkwhale.popover')
  if (isMobile.value && !inPopover) {
    shouldDelayClose.value = false
    isOpen.value = false
  }
}
onClickOutside(popover, async (event) => {
  const inPopover = !!(event.target as HTMLElement).closest('.funkwhale.popover')
  if (!isMobile.value && !inPopover) {
    shouldDelayClose.value = false
    isOpen.value = false
  }
}, { ignore: [slot] })

// Auto positioning
const isMobile = isMobileView()
const { width, height, left, top, update } = useElementBounding(() => slot.value?.children[0])
const { width: popoverWidth, height: popoverHeight } = useElementBounding(popover, {
  windowScroll: false
})

whenever(isOpen, update, { immediate: true })

const { width: screenWidth, height: screenHeight } = useScreenSize()

// TODO (2.0.0+) ~Type::A11y #2487:
// - I can't operate the popup with a keyboard. Remove barrier for people not using a mouse (A11y)
// - Switching to submenus is error-prone. When moving cursor into freshly opened submenu, it should not close if the cursor crosses another menu item
// - Large menus disappear. When menus get big, they need to scroll.

const position = computed(() => {
  if (positioning === 'vertical' || isMobile.value) {
    let offsetTop = top.value + height.value
    if (offsetTop + popoverHeight.value > screenHeight.value) {
      offsetTop -= popoverHeight.value + height.value
    }

    let offsetLeft = left.value
    if (offsetLeft + popoverWidth.value > screenWidth.value) {
      offsetLeft -= popoverWidth.value - width.value
    }

    return {
      left: offsetLeft + 'px',
      top: offsetTop + 'px'
    }
  }

  let offsetTop = top.value
  if (offsetTop + popoverHeight.value > screenHeight.value) {
    offsetTop -= popoverHeight.value - height.value
  }

  let offsetLeft = left.value + width.value
  if (offsetLeft + popoverWidth.value > screenWidth.value) {
    offsetLeft -= popoverWidth.value + width.value
  }

  return {
    left: offsetLeft + 'px',
    top: offsetTop + 'px'
  }
})

// Popover close stack
let stack = inject(POPOVER_INJECTION_KEY, [ref(false)])
if (!stack) {
  provide(POPOVER_INJECTION_KEY, stack = shallowReactive([]))
}

stack.push(isOpen)
onScopeDispose(() => {
  stack?.splice(stack.indexOf(isOpen), 1)
})

// Check if there's an ancestral context to inherit close function from
const ancestralContext = inject(POPOVER_CONTEXT_INJECTION_KEY, null)

// Provide context for child items
const hoveredItem = ref(-2)
provide(POPOVER_CONTEXT_INJECTION_KEY, {
  items: ref(0),
  hoveredItem,
  close: ancestralContext?.close ?? (() => { isOpen.value = false })
})

// Closing
const closeChild = () => {
  const ref = stack?.[stack.indexOf(isOpen) + 1]
  if (!ref) return

  ref.value = false
}

// Recursively close popover tree
watch(isOpen, (isOpen) => {
  if (isOpen) {
    shouldDelayClose.value = true
    return
  }
  closeChild()
})
</script>

<template>
  <div
    ref="slot"
    :class="['funkwhale popover-container', { 'split-button': inSlot?.classList?.contains('button-group') }]"
    :style="inSlot?.classList?.contains('button-group') ? 'display: inline-flex' : 'display: contents'"
  >
    <slot
      ref="inSlot"
      :is-open="isOpen"
      :toggle-open="() => isOpen = !isOpen"
      :open="() => isOpen = true"
      :close="() => isOpen = false"
    />
  </div>

  <teleport
    v-if="isOpenDelayed"
    to="body"
  >
    <div
      :class="{ 'is-mobile': isMobile }"
      class="funkwhale popover-outer"
      @click.stop="mobileClickOutside"
    >
      <div
        ref="popover"
        :style="position"
        :class="{ 'is-mobile': isMobile }"
        class="funkwhale popover"
        v-bind="color(colorProps)()"
        style="display:flex; flex-direction:column;"
      >
        <slot
          name="items"
          :close="() => isOpen = false"
        />
      </div>
    </div>
  </teleport>
</template>

<style lang="scss">
@import '~/style/funkwhale.scss';

.funkwhale.popover-container {
  width: max-content;

  &.split-button {
     display: inline-flex;
     gap: 0;
   }
}

.funkwhale.popover-outer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 99999;

  &:not(.is-mobile) {
    pointer-events: none;
  }
}

.funkwhale.popover {
    border: 1px solid var(--fw-border-color);
    background-color: color-mix(in oklab, var(--background-color) 98%, var(--color));

    hr {
      border-bottom: 1px solid var(--fw-border-color);
    }

    @include light-theme {
      --fw-border-color: var(--fw-gray-500);

    }

    @include dark-theme {
      --fw-border-color: var(--fw-gray-800);

      .popover-item:hover {
        background-color: var(--hover-background-color);
      }
    }

    pointer-events: auto;

    &.is-mobile {
      width: 90vw;
      margin: 0 5vw;
      left: 0 !important;
      box-shadow: 0 0 0 1000vh rgba(0,0,0,0.2),
                  0 0 100vh rgba(0,0,0,0.6);
    }

    position: absolute;
    padding: 16px;
    border-radius: var(--fw-border-radius);
    min-width: 246px;
    z-index: 999;

    font-size: 0.875rem;

    hr {
      padding-top: 12px;
      margin-bottom: 12px;
    }
  }
</style>
