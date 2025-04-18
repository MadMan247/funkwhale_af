<script setup lang="ts">
import { computed, ref, inject, provide, shallowReactive, watch, onScopeDispose } from 'vue'
import { whenever, useElementBounding, onClickOutside } from '@vueuse/core'

import { isMobileView, useScreenSize } from '~/composables/screen'
import { POPOVER_INJECTION_KEY, POPOVER_CONTEXT_INJECTION_KEY } from '~/injection-keys'
import { type ColorProps, type DefaultProps, type RaisedProps, color } from '~/composables/color'

/* TODO: Basic accessibility

-> See ui-docs

*/

const isOpen = defineModel<boolean>({ default: false })

const { positioning = 'vertical', ...colorProps } = defineProps<{
  positioning?:'horizontal' | 'vertical'
} &(ColorProps | DefaultProps) & RaisedProps>()

// Template refs
const popover = ref()
const slot = ref()
const inSlot = ref()

// Click outside
const mobileClickOutside = (event: MouseEvent) => {
  const inPopover = !!(event.target as HTMLElement).closest('.funkwhale.popover')
  if (isMobile.value && !inPopover) {
    isOpen.value = false
  }
}
onClickOutside(popover, async (event) => {
  const inPopover = !!(event.target as HTMLElement).closest('.funkwhale.popover')
  if (!isMobile.value && !inPopover) {
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

// TODO (basic functionality):
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

// Provide context for child items
const hoveredItem = ref(-2)
provide(POPOVER_CONTEXT_INJECTION_KEY, {
  items: ref(0),
  hoveredItem
})

// Closing
const closeChild = () => {
  const ref = stack?.[stack.indexOf(isOpen) + 1]
  if (!ref) return

  ref.value = false
}

// Recursively close popover tree
watch(isOpen, (isOpen) => {
  if (isOpen) return
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
    v-if="isOpen"
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
        <slot name="items" />
      </div>
    </div>
  </teleport>
</template>

<style lang="scss">
@import './popover.scss'
</style>
