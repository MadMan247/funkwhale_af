<script setup lang="ts">
import { computed, onMounted, ref, useSlots } from 'vue'

import { type RouterLinkProps, RouterLink } from 'vue-router'
import { type ColorProps, type DefaultProps, type VariantProps, color, isNoColors } from '~/composables/color'
import { type WidthProps, width } from '~/composables/width'
import { type AlignmentProps, align } from '~/composables/alignment'

import { fromProps, notUndefined } from '~/ui/composables/useModal.ts'

const props = defineProps<{
  thickWhenActive?: true

  thinFont?: true

  icon?: string;
  round?: true;

  autofocus? : boolean
  forceUnderline? : true
} & RouterLinkProps
  &(ColorProps | DefaultProps)
  & VariantProps
  & WidthProps
  & AlignmentProps>()

const isExternalLink = computed(() =>
  typeof props.to === 'string' && (props.to.startsWith('http') || props.to.startsWith('./'))
)

/**
 * Any query matches
 */
const isNoMatchingQueryFlags = computed(() =>
  fromProps(props, notUndefined)?.every(({ isOpen }) => !isOpen.value)
)

const [fontWeight, activeFontWeight] = 'solid' in props || props.thickWhenActive ? [600, 900] : [400, 400]

const isIconOnly = computed(() =>
  !!props.icon && (
    !useSlots().default
      || 'square' in props && props.square
      || 'squareSmall' in props && props.squareSmall
  )
)

const button = ref()

onMounted(() => {
  if (props.autofocus) button.value.focus()
})
</script>

<template>
  <component
    :is="isExternalLink ? 'a' : RouterLink"
    v-bind="
      color(props, ['interactive'])(
        width(props,
              isNoColors(props) ? [] : ['normalHeight', 'solid' in props ? 'buttonWidth' : 'auto']
        )(
          align(props, 'solid' in props ? {alignText: 'center'} : {})(
          )))"
    ref="button"
    :autofocus="autofocus || undefined"
    :class="[
      $style.link,
      round && $style['is-round'],
      isIconOnly && $style['is-icon-only'],
      (isNoColors(props) || props.forceUnderline) && $style['force-underline'],
      isNoColors(props) && $style['no-spacing'],
      isNoMatchingQueryFlags && 'router-link-no-matching-query-flag'
    ]"
    :href="isExternalLink ? to.toString() : undefined"
    :to="isExternalLink ? undefined : to"
    :target="isExternalLink ? '_blank' : undefined"
  >
    <i
      v-if="icon"
      :class="['bi', icon]"
    />

    <span>
      <slot />
    </span>
  </component>
</template>

<style module lang="scss">

  .link {

    // Layout

    --padding: 16px;
    --shift-by: 0.5px;

    position: relative;
    display: inline-flex;
    white-space: nowrap;
    align-items: center;

    padding: calc(var(--padding) / 2 - var(--shift-by)) var(--padding) calc(var(--padding) / 2 + var(--shift-by)) var(--padding);
    &.is-icon-only {
      padding: var(--padding);
    }
    &.no-spacing {
      padding: 0;
      margin: 0;
      font-size: 1em;
    }

    // Font

    font-family: $font-main;
    font-weight: v-bind(fontWeight);
    font-size: 14px;

    line-height: 1em;

    // Content

    > span {
      position: relative;
      top: calc(0px - var(--shift-by));
    }

    // Decoration

    &:not([disabled]) {
      cursor: pointer;
    }

    transform: translateX(var(--fw-translate-x)) translateY(var(--fw-translate-y)) scale(var(--fw-scale));
    transition:background-color .2s, border-color .3s;

    &:not(.force-underline) {
      text-decoration: none;
      // background-color: transparent;
      // border-color: transparent;
    }

    border-radius: var(--fw-border-radius);

    &.is-round {
      border-radius: 100vh;
    }

    // States

    &:global(.router-link-exact-active) {
      font-weight: v-bind(activeFontWeight);
    }

    // Icon

    > i:global(.bi) {
      font-size: 1.2rem;
      &.large {
        font-size:2rem;
      }
      &+span:not(:empty) {
        margin-left: 1ch;
      }
    }
  }
</style>
