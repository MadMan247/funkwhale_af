<script setup lang="ts">
import { useId } from 'vue'

import { computed } from 'vue'

import Layout from '@ui/Layout.vue'
import Spacer from '@ui/Spacer.vue'
import Button from '@ui/Button.vue'
import Heading from '@ui/Heading.vue'
import Loader from '@ui/Loader.vue'

// #region props
const props = defineProps<{
  columnsPerItem?: 1 | 2 | 3 | 4
  alignLeft?: boolean
  icon?: string
  badge?: 'loading' | number
} & {
  [H in `h${ '1' | '2' | '3' | '4' | '5' | '6' }`]? : string
} & {
  [S in 'page-heading' | 'section-heading' | 'large-section-heading' | 'subsection-heading' | 'caption' | 'title' | 'radio' | 'secondary' ]? : true
} & {
  [Operation in 'expand' | 'collapse']?: () => void
}>()
// #endregion props

const id = useId()

// TODO: (flupsi) Have to tidy this up...
const headingProps = computed(() =>
  Object.fromEntries(Object.entries(props).filter(
    ([key, value]) => value
      && (['pageHeading', 'sectionHeading', 'largeSectionHeading', 'subsectionHeading', 'caption', 'title', 'radio', 'secondary']
        .includes(key) || key.startsWith('h'))
  )))
</script>

<template>
  <section
    style="flex-grow: 1;"
    :aria-labelledby="id"
  >
    <Layout
      header
      v-bind="columnsPerItem
        ? { grid: `auto / repeat(auto-fit, calc(46px * ${columnsPerItem} + 32px * ${(columnsPerItem) - 1}))` }
        : { flex: true }
      "
      :class="[alignLeft && $style.left, expand || collapse ? $style.collapsible : $style.uncollapsible]"
    >
      <!-- The title row's width is a multiple of the expected items' column span -->

      <Layout
        flex
        no-gap
        :class="$style.headerLayout"
      >
        <!-- Accordion? -->

        <template v-if="expand || collapse">
          <Button
            full
            align-text="start"
            align-self="end"
            :class="$style.summary"
            :aria-pressed="!!collapse"
            raised
            @click="() => expand ? expand() : collapse ? collapse() : (() => { return })()"
          >
            <slot name="topleft" />

            <Heading
              v-bind="headingProps"
              :id
            />
          </Button>
          <i
            :class="!!expand ? 'bi bi-chevron-down' : 'bi bi-chevron-up'"
            style="
              position: absolute;
              top: 12px;
              right: 0;
              pointer-events: none;
            "
          />
        </template>

        <!-- Normal (non-accordion)? -->

        <template v-else>
          <!-- Set distance between baseline and previous row -->
          <Spacer
            v
            :size="64"
          />
          <slot name="topleft" />
          <Heading
            v-bind="headingProps"
            :id
            style="
              padding: 0 0 24px 0;
              margin: 0;
            "
          >
            <template
              v-if="icon"
              #before
            >
              <div style="float: left; padding-right: .5em;">
                <i :class="['bi', icon]" />
              </div>
            </template>
            <template
              v-if="badge"
              #after
            >
              <Loader v-if="badge==='loading'" />
              <div
                v-else
                :class="['solid', $style.badge]"
              >
                {{ badge }}
              </div>
            </template>
          </Heading>
          <Spacer grow />
        </template>

        <!-- Action! You can either specify `to` or `onClick`. -->
        <!-- Note: We cannot simplify with  `<component is="action && 'to' in action ? Link : Button"` due to a Vue bug -->
        <!-- TODO: Refactor to a `#action` slot (for simplicity and composability) and make sure to pay extra attention to layout edge cases. -->


        <span
          v-if="$slots.action"
          :class="$style.action"
        >
          <slot name="action" />
        </span>
      </Layout>
    </Layout>

    <!-- Love: https://css-tricks.com/css-grid-can-do-auto-height-transitions/ -->

    <Layout
      role="group"
      :inert="!!expand"
      :style="`${
        'alignLeft' in props && props.alignLeft
          ? 'justify-content: start;'
          : ''
      }${
        !!expand
          ? 'grid-template-rows: 0fr; overflow: hidden; max-height: 0;'
          : 'max-height: 4000px;'
      }${
        !!collapse
          ? 'padding: 12px 0;'
          : ''
      }
        position: relative;
        transition: max-height .5s, grid-template-rows .3s, padding .2s;
      `"
      v-bind="columnsPerItem
        ? { grid: 'auto / repeat(auto-fit, 46px)' }
        : { stack: true }
      "
    >
      <slot />
    </Layout>
  </section>
</template>

<style module>
.headerLayout {
  /* Stretch the header of the section over all grid columns */
  --grid-column: 1 / -1;

  align-self: baseline;
  align-items: baseline;
  position: relative;

  /* When header is overlapping previous interactive elements, allow clicks to go through: */
  pointer-events: none;
  &>*{
    pointer-events: auto;
  }
}

.badge.badge.badge.badge {
    font-weight: 1000;
    border-radius: 100%;
    height: 21px;
    min-width: 21px;
    display: inline-block;
    font-size: 11px;
    text-align: center;
    vertical-align: text-top;
    line-height: 20px;
    pointer-events: none;
    background-color: var(--color);
    color: var(--background-color);
    border: none;
}


/* Thank you, css, for offering this weird alternative to !important */
header.left.left {
  justify-content: start;
}

.uncollapsible {
  margin-top: -64px;
  pointer-events: none;
  &>*{
    pointer-events: auto;
  }
}

.summary {
  align-self: baseline;
  min-width: calc(100% + 32px);
  margin: 0 -16px;
  --fw-border-radius: 32px;
}

/* Visually push ghost link and non-solid button to the edge */
.action {
  display: contents;
  & > :global(.interactive:not(:is(.primary, .solid, .destructive, .secondary)):is(button, a.ghost)) {
    margin-right: -16px;
  }
}
</style>
