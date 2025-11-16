<script setup lang="ts" generic="T extends string">
defineProps<{
  gridTemplateColumns:(`${number}${'px' | 'fr'}` | 'auto')[]
  headerProps?: { [key: string]: unknown }
  isTable?: boolean
}>()
</script>

<template>
  <!-- TODO: Refactor to use semantic elements `td`, `tr`, `th`, `table`, `caption`. See https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-3-1a for details.-->
  <component
    :is="isTable ? 'table' : 'section'"
    :class="$style.table"
    :style="`grid-template-columns: ${gridTemplateColumns.join(' ')};`"
  >
    <span
      :class="$style['table-header']"
      v-bind="headerProps"
    >
      <slot name="header" />
    </span>
    <slot />
  </component>
</template>

<style module>
  .table {
    width: 100%; align-self: stretch; display: grid;
  }

  /* Table cells */
  .table > * {
    height: 64px;
    display: flex;
    align-items: center;
  }

  /* Table header */
  .table-header {
    display: contents;
  }
  /* Table header cells */
  .table-header > *{
    height: 40px;
    display: flex;
    align-items: center;
    line-height: 36px;
    border: 0px solid var(--border-color);
    border-width: 1px 0;
    color: color-mix(in oklab, currentcolor 50%, var(--border-color));
    font-weight: 900;
    grid-column: span 1;
  }

  /* Auto-expand cells if following cells are empty */
  .table > :has(+ :empty) {
    grid-column-end: span 2;
  }
  .table > :has(+ :empty + :empty) {
    grid-column-end: span 3;
  }
  .table > :has(+ :empty + :empty + :empty) {
    grid-column-end: span 4;
  }

  /* Hide empty content (after the header row)  */
  .table > .table-header ~ :empty {
    display: none;
  }
</style>
