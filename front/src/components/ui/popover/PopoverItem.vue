<script setup lang="ts">
import { inject, ref } from 'vue'
import { type RouterLinkProps, RouterLink } from 'vue-router'
import { POPOVER_CONTEXT_INJECTION_KEY, type PopoverContext } from '~/injection-keys'

import Button from '~/components/ui/Button.vue'

const emit = defineEmits<{ setId: [value: number] }>()

const { parentPopoverContext, to } = defineProps<{
  parentPopoverContext?: PopoverContext;
  to?:RouterLinkProps['to'];
  icon?: string;
}>()
const { items, hoveredItem } = parentPopoverContext ?? inject(POPOVER_CONTEXT_INJECTION_KEY, {
  items: ref(0),
  hoveredItem: ref(-2)
})

const id = items.value++
emit('setId', id)
</script>

<template>
  <a
    v-if="to && typeof to === 'string' && to.startsWith('http')"
    :href="to.toString()"
    class="popover-item"
    target="_blank"
  >
    <i
      v-if="icon"
      :class="['bi', icon]"
    />
    <slot />

    <div class="after">
      <slot name="after" />
    </div>
  </a>
  <RouterLink
    v-else-if="to"
    :to="to"
    class="popover-item"
    @mouseover="hoveredItem = id"
  >
    <i
      v-if="icon"
      :class="['bi', icon]"
    />
    <slot />

    <div class="after">
      <slot name="after" />
    </div>
  </RouterLink>
  <Button
    v-else
    ghost
    thin-font
    v-bind="$attrs"
    style="
      width: 100%;
      textAlign: left;
      gap: 8px;
    "
    :icon="icon"
    class="popover-item"
    @mouseover="hoveredItem = id"
  >
    <slot />

    <div class="after">
      <slot name="after" />
    </div>
  </Button>
</template>

<style scoped>
  div { color:var(--fw-text-color); }
</style>

<style lang="scss">
.popover .popover-item {
  cursor: pointer;
  text-decoration: none;
  padding: 0px 8px;
  height: 32px;
  display: flex;
  align-items: center;
  border-radius: var(--fw-border-radius);
  white-space: nowrap;

  &:hover {
    background-color: var(--hover-background-color);
  }

  > .bi:first-child {
    margin-right: 16px;
  }

  > .bi:last-child {
    margin-right: 8px;
  }

  > .after {
    margin-left: auto;
  }
}
.popover .popover-item.button {
  justify-content: flex-start !important;
  height: 32px !important;
  padding: 0px 8px;
  border: none;
  align-items: center;
  &:hover {
    background-color: var(--hover-background-color) !important;
  }
  span {
    width: 100%;
    position: relative;
    i {
      font-size: 14px;
    }
    > i {
      margin-right: 14px !important;
    }
    .after {
      position: absolute;
      right: -12px;
      top: 0;
      height: 100%;
      display: flex;
      place-items: center;
      gap: 8px;
    }
  }
}
</style>
