<script setup lang="ts">
import type { ComponentProps } from 'vue-component-type-helpers'

import { computed } from 'vue'

import Layout from '~/components/ui/Layout.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Button from '~/components/ui/Button.vue'
import Link from '~/components/ui/Link.vue'
import Heading from '~/components/ui/Heading.vue'

const props = defineProps<{
  columnsPerItem?: 1 | 2 | 3 | 4
  alignLeft?: boolean
  action?: { text: string, id?: string } & (ComponentProps<typeof Link> | ComponentProps<typeof Button>)
  icon?: string
} & {
  [H in `h${ '1' | '2' | '3' | '4' | '5' | '6' }`]? : string
} & {
  [S in 'page-heading' | 'section-heading' | 'large-section-heading' | 'subsection-heading' | 'caption' | 'title' | 'radio' | 'secondary' ]? : true
} & {
  [Operation in 'expand' | 'collapse']?: () => void
}>()

const hasContent = computed(() => {
  // @ts-expect-error too complex type thingy
  return Object.keys(props).some(key => (key === 'expand' || key === 'collapse' || key === 'action' || key.startsWith('h')) && props[key])
})

// TODO: (flupsi) Have to tidy this up...
const headingProps = computed(() =>
  Object.fromEntries(Object.entries(props).filter(
    ([key, value]) => value
      && (['pageHeading', 'sectionHeading', 'largeSectionHeading', 'subsectionHeading', 'caption', 'title', 'radio', 'secondary']
        .includes(key) || key.startsWith('h'))
  )))
</script>

<template>
  <section style="flex-grow: 1;">
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
        :style="`
          grid-column: 1 / -1;
          align-self: baseline;
          align-items: baseline;
          position: relative;
          flex-grow: 1;
          ${ hasContent ? '' : 'pointer-events: none;'}
        `"
      >
        <!-- Accordion? -->

        <template v-if="expand || collapse">
          <Button
            full
            align-text="start"
            align-self="end"
            :class="$style.summary"
            :aria-pressed="!!collapse"
            v-bind="action"
            raised
            @click="() => expand ? expand() : collapse ? collapse() : (() => { return })()"
          >
            <slot name="topleft" />

            <!-- @vue-ignore -->
            <Heading v-bind="headingProps" />
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
          <div
            v-if="icon"
            style="display: flex; justify-content: center; align-items: center; width: 48px;"
          >
            <i
              :class="['bi', icon]"
              style="font-size: 18px;"
            />
          </div>
          <slot name="topleft" />
          <Heading
            v-bind="headingProps"
            style="
              padding: 0 0 24px 0;
              margin: 0;
            "
          />
          <Spacer grow />
        </template>

        <!-- Action! You can either specify `to` or `onClick`. -->

        <component
          :is="'to' in action ? Link : Button"
          v-if="action"
          thin-font
          min-content
          align-self="baseline"
          :class="$style.action"
          v-bind="action"
        >
          {{ action?.text }}
        </component>
      </Layout>
    </Layout>

    <!-- Love: https://css-tricks.com/css-grid-can-do-auto-height-transitions/ -->

    <Layout
      main
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

<style module lang="scss">
// Thank you, css, for offering this weird alternative to !important
header.left.left {
  justify-content: start;
}

.uncollapsible {
  margin-top: -64px;
}

.summary {
  align-self: baseline;
  min-width: calc(100% + 32px);
  margin: 0 -16px;
  --fw-border-radius: 32px;
}

// Visually push ghost link and non-solid button to the edge
.action:global(.interactive:not(:is(.primary, .solid, .destructive, .secondary)):is(button, a.ghost)) {
  margin-right: -16px;
}
</style>
