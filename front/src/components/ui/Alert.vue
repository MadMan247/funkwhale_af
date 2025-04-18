<script setup lang="ts">
import { type PastelProps, color } from '~/composables/color'
import { type AlignmentProps, align } from '~/composables/alignment'

import Layout from '~/components/ui/Layout.vue'

export type Props = PastelProps & AlignmentProps

const props = defineProps<Props>()
</script>

<template>
  <div
    class="funkwhale alert"
    role="alert"
    v-bind="{
      ...$attrs,
      ...color(props, ['solid'])(
        align(props)(
        ))}"
  >
    <slot />

    <Layout
      v-if="$slots.actions"
      flex
      class="actions"
    >
      <slot name="actions" />
    </Layout>
  </div>
</template>

<style lang="scss">
@import './alert.scss'
</style>
