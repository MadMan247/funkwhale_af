<script setup lang="ts">
import { computed } from 'vue'
import { type ColorProps, type DefaultProps, type PastelProps, type RaisedProps, type VariantProps, color } from '~/composables/color'
import { type WidthProps, width } from '~/composables/width'

const props = defineProps<{
  columnWidth?: string,
  noRule?: true,
  noWrap?: true,
} & { [P in 'stack' | 'grid' | 'flex' | 'columns' | 'row' | 'page']?: true | string }
  & { [C in 'nav' | 'ul' | 'aside' | 'header' | 'footer' | 'main' | 'label' | 'form' | 'h1' | 'h2' | 'h3' | 'h4' | 'h5']?: true }
  & { [G in 'no-gap' | `gap-${'4' | '8' | '12' | '16' | '32' | '48' | '64' | '84' | 'auto'}` ]?: true }
  &(PastelProps | ColorProps | DefaultProps)
  & RaisedProps
  & VariantProps
  & WidthProps>()

const columnWidth = props.columnWidth ?? '46px'

const maybeGap = Object.entries(props).find(
  ([key, value]) => value === true && key.startsWith('gap'))
const gapWidth = maybeGap ? `${maybeGap[0].replace('gap', '').replace('-', '')}px` : '32px'

const attributes = computed(() => ({
  ...color(props)(width(props)()),
  layout:
    props.grid === true
      ? 'grid'
      : typeof props.grid === 'string'
        ? 'grid-custom'
        : props.flex === true
          ? 'flex'
          : props.columns === true
            ? 'columns'
            : 'stack'
}))
</script>

<template>
  <component
    :is="props.nav ? 'nav' : props.ul ? 'ul' : props.aside ? 'aside' : props.header ? 'header' : props.footer ? 'footer' : props.main ? 'main' : props.label ? 'label' : props.form ? 'form' : props.h1 ? 'h1' : props.h2 ? 'h2' : props.h3 ? 'h3' : props.h4 ? 'h4' : props.h5 ? 'h5' : 'div'"
    :class="[
      $style.layout,
      ('noGap' in props && props.noGap === true) || $style.gap,
      noWrap || $style.wrap,
    ]"
    v-bind="attributes"
  >
    <slot />
  </component>
</template>

<style module lang="scss">
.layout {
  transition: all .15s;

  /* Override --gap with your preferred value */

  gap: var(--gap, v-bind(gapWidth));
  &:not(.gap) {
    gap: 0;
  }

  /* Growth */

  &:has(:global(>.grow)) {
    >:not(:global(.grow)) {
      flex-grow: 0;
    }
  }

  /* Layout strategy */

  &[layout=columns] {
    column-count: auto;
    column-width: v-bind(columnWidth);
    display: block;
    column-rule: 1px solid v-bind("noRule ? 'transparent' : 'var(--border-color)'");
  }

  &[layout=grid] {
    display: grid;
    grid-template-columns:
      repeat(auto-fit, v-bind(columnWidth));
    grid-auto-flow: row dense;
    /* If the grid has a fixed size smaller than its container, center it */
    place-content: center;
    align-items: baseline;
  }

  &[layout=grid-custom] {
    display: grid;
    grid: v-bind("props.grid");
    grid-auto-flow: row dense;
    /* If the grid has a fixed size smaller than its container, center it */
    place-content: center;
  }

  &[layout=grid] > *, &[layout=grid-custom] > * {
    /* Set this global variable through `width` */
    grid-column: var(--grid-column);
  }

  &[layout=stack] {
    display: flex;
    flex-direction: column;
  }

  &[layout=flex] {
    display: flex;
    flex-direction: row;
    flex-wrap: v-bind('props.noWrap ? "nowrap" : "wrap"');
  }
}
</style>
