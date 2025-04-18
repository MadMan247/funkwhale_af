<script setup lang="ts">
import type { ComponentProps } from 'vue-component-type-helpers'

import Layout from '~/components/ui/Layout.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Button from '~/components/ui/Button.vue'
import Link from '~/components/ui/Link.vue'
import Heading from '~/components/ui/Heading.vue'

const actionComponents
  = { Button, Link }

const props = defineProps<{
  columnsPerItem?: 1 | 2 | 3 | 4
  alignLeft?: boolean
  action?: { text: string } & (ComponentProps<typeof Link> | ComponentProps<typeof Button>)
  icon?: string
  noGap?: false
} & {
  [H in `h${ '1' | '2' | '3' | '4' | '5' | '6' }`]? : string
} & {
  [S in 'page-heading' | 'section-heading' | 'large-section-heading' | 'subsection-heading' | 'caption' | 'title' | 'radio' | 'secondary' ]? : true
} & {
  [Operation in 'expand' | 'collapse']?: () => void
}>()
</script>

<template>
  <Layout
    header
    flex
    gap-24
  >
    <div v-if="$slots.image">
      <slot name="image" />
    </div>
    <Layout
      stack
      :gap-8="!(props.noGap as boolean)"
      :no-gap="props.noGap"
      style="flex-grow: 1;"
    >
      <Layout
        flex
        no-gap
        style="align-self: stretch;"
      >
        <!-- Set distance between baseline and previous row -->
        <Spacer
          v
          :size="53"
          style="align-self: baseline;"
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
        <!-- The inferred type of props occasionally overloads the typescript compiler. -->
        <!-- TODO: Remove @vue-ignore once tsc is re-implemented in Go (and 10x faster) -->
        <!-- @vue-ignore -->
        <Heading
          v-bind="props"
          style="
            align-self: baseline;
            padding: 0 0 0 0;
            margin: 0;
          "
        />
        <Spacer grow />
        <!-- Action! You can either specify `to` or `onClick`. -->
        <component
          :is="'onClick' in action ? actionComponents.Button : actionComponents.Link"
          v-if="action"
          thin-font
          min-content
          align-self="baseline"
          :class="$style.action"
          v-bind="action"
        >
          {{ action?.text }}
        </component>
        <div
          v-if="$slots.action"
          style="align-self: center;"
        >
          <slot name="action" />
        </div>
      </Layout>
      <slot />
    </Layout>
  </Layout>
  <Spacer />
</template>

<style module lang="scss">
  // Visually push ghost link and non-solid button to the edge
  .action:global(.interactive:not(:is(.primary, .solid, .destructive, .secondary)):is(button, a.ghost)) {
    margin-right: -16px;
  }
</style>
