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
        ))
    }"
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
@import '~/style/funkwhale.scss';

.funkwhale.alert {

  padding: 2rem 2rem;
  line-height: 1.2;
  display: flex;
  flex-direction: column;

  h2, h3, h4 {
    margin-top: 0;
    margin-bottom: 0;
  }

  > .actions {
    margin-left: auto;
  }

  // Add styles for when alert is used as a notification
  &.is-notification {
    position: fixed;
    bottom: 1rem;
    right: 1rem;
    z-index: 1000;
    min-width: 200px;
    max-width: 400px;
    background-color: var(--background-color);

    &.fade-enter-active,
    &.fade-leave-active {
      transition: all 0.3s ease;
    }

    &.fade-enter-from,
    &.fade-leave-to {
      opacity: 0;
      transform: translateY(1rem);
    }
  }
}
</style>
