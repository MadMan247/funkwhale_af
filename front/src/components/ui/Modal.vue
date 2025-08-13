<script setup lang="ts">
import { type ColorProps, type DefaultProps, color } from '~/composables/color'
import { watchEffect, ref, nextTick, computed } from 'vue'
import onKeyboardShortcut from '~/composables/onKeyboardShortcut'
import { useI18n } from 'vue-i18n'
import { useWindowSize
 } from '@vueuse/core'

const { width: screenWidth } = useWindowSize
()

import Button from '~/components/ui/Button.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Layout from '~/components/ui/Layout.vue'
import Heading from '~/components/ui/Heading.vue'

const { t } = useI18n()

const props = withDefaults(
    defineProps<{
      title?: string,
      overPopover?: true,
      isdestructive?: true,
      cancel?: string | true,
      icon?: string,
      autofocus?: true | 'off',
      maximizeSize?: true
    } & (ColorProps | DefaultProps)>(),
    { title: '' }
)

const size = { padding: 32, gap: 32, card: 202 }

const maxWidth = computed(() =>
  props.maximizeSize
  ? `${[0, 1, 2, 3, 4, 5, 6, 7, 8].map(n => size.padding*2+(n+1)*size.card+n*size.gap).findLast(n => n< screenWidth.value)}px`
  : 'min(90vw, 55rem)',
  { immediate: true }
)

const isOpen = defineModel<boolean>({ default: false })

const previouslyFocusedElement = ref()

// Handle focus and inertness of the elements behind the modal
watchEffect(() => {
  if (isOpen.value) {
    nextTick(() => {
      previouslyFocusedElement.value = document.activeElement
      previouslyFocusedElement.value?.blur()
      document.querySelector('#app')?.setAttribute('inert', 'true')
    })
  } else {
    nextTick(() => previouslyFocusedElement.value?.focus())
    document.querySelector('#app')?.removeAttribute('inert')
  }
})

onKeyboardShortcut('escape', () => { isOpen.value = false })

// TODO:
// When overflowing content: Add inset shadow to indicate scrollability
</script>

<template>
  <Teleport to="body">
    <Transition mode="out-in">
      <div
        v-if="isOpen"
        class="funkwhale overlay"
        @click.exact.stop="isOpen = false"
      >
        <div
          class="funkwhale modal"
          :class="[
            {
              'isdestructive': isdestructive,
              'has-alert': !!$slots.alert,
              'over-popover': overPopover,
            }
          ]"
          v-bind="{ ...$attrs, ...color(props, ['default'])() }"
          @click.stop
        >
          <Layout
            flex
            gap-12
            style="padding: 12px 12px 0 12px;"
          >
            <div
              v-if="!$slots.topleft && !icon"
              style="width: 48px;"
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
            <Spacer
              v-if="!$slots.topleft"
              grow
            />
            <Heading
              v-if="title !== ''"
              :h2="title"
              section-heading
              :class="{ 'destructive-header': isdestructive }"
            />
            <Spacer
              v-if="title !== ''"
              grow
            />
            <Button
              icon="bi-x-lg"
              ghost
              align-self="baseline"
              :aria-label="t('vui.aria.close')"
              :autofocus="props.autofocus === undefined ? ($slots.actions || cancel ? undefined : true) : props.autofocus !== 'off'"
              @click="isOpen = false"
            />
          </Layout>

          <!-- Content -->

          <div class="modal-shadow-top" />

          <div class="modal-content">
            <Transition>
              <div
                v-if="$slots.alert"
                class="alert-container"
              >
                <div>
                  <slot name="alert" />
                </div>
              </div>
            </Transition>

            <slot />

            <Spacer v-if="!$slots.actions" />
          </div>

          <div class="modal-shadow-bottom" />

          <!-- Actions slot -->

          <Layout
            v-if="$slots.actions || cancel"
            flex
            gap-12
            style="flex-wrap: wrap;"
            class="modal-actions"
          >
            <slot name="actions" />
            <Button
              v-if="cancel"
              secondary
              autofocus
              :on-click="() => { isOpen = false }"
            >
              {{ typeof cancel === 'string' ? cancel : t('vui.cancel') }}
            </Button>
          </Layout>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style lang="scss">
.funkwhale.modal {
  background: var(--background-color);

  box-shadow: 0 2px 12px 2px var(--shadow-color);
  border-radius: 1rem;
  max-width: v-bind("maxWidth");
  width: 100%;

  display: grid;
  max-height: 90vh;
  grid-template-rows: auto 1fr auto;

  position: relative;

  &.isdestructive {
    border-top: 24px solid var(--fw-red-400);

    > h2 {
      &.destructive-header {
        color: var(--fw-red-400);
      }
    }
  }

  > h2 {
    font-size: 1.25em;
    padding: 1.625rem 4.5rem;
    line-height: 1.2;
    text-align: center;
    position: relative;

    > .funkwhale.button {
      font-size: 1rem;
      position: absolute;
      right: 1rem;
      top: 50%;
      transform: translateY(-49%);
    }
  }

  .modal-content {
    padding: 1rem 2rem 3rem 2rem;
    overflow: auto;
    position: relative;

    > .alert-container {
      position: sticky;
      top: -1rem;
      margin: -1rem -2rem 1rem;

      display: grid;
      grid-template-rows: 1fr;

      &.v-enter-active,
      &.v-leave-active {
        transition: grid-template-rows 0.2s ease;
      }

      &.v-enter-from,
      &.v-leave-to {
        grid-template-rows: 0fr;
      }

      > div {
        overflow: hidden;
      }
    }
  }

  .modal-shadow-top {
    z-index: 2;
    height: 16px;
    width: 100%;
    position: absolute;
    top: 60px;
    background:linear-gradient(var(--background-color), color-mix(in oklab, var(--background-color) 50%, transparent), color-mix(in oklab, var(--background-color) 20%, transparent), transparent);
  }

  .modal-shadow-bottom {
    height: 32px;
    margin-top: -32px;
    position: sticky;
    bottom: 0px;
    background:linear-gradient(transparent, color-mix(in oklab, var(--background-color) 20%, transparent), color-mix(in oklab, var(--background-color) 50%, transparent), var(--background-color));
    &:last-child{
      border-bottom-right-radius: 1rem;
      border-bottom-left-radius: 1rem;
    }
  }

  .modal-actions {
    padding: 0 2rem 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;

    > :first-child {
      margin-left: 0px !important;
    }

    > :last-child {
      margin-right: 0px !important;
    }

    position: relative;
  }
}

.funkwhale.overlay:has(.over-popover) {
  /* override z-index */
  z-index: 9999;
}

.funkwhale.overlay {
  background: rgba(#000, .2);

  position: fixed;
  inset: 0;

  z-index: 9001;

  display: flex;
  align-items: center;
  justify-content: center;

  &.v-enter-active,
  &.v-leave-active {
    transition: opacity 0.2s ease;

    .funkwhale.modal {
      transition: transform 0.2s ease;
    }
  }

  &.v-enter-from,
  &.v-leave-to {
    opacity: 0;

    .funkwhale.modal {
      transform: translateY(1rem);
    }
  }

  &.v-leave-to {
    .funkwhale.modal {
      transform: translateY(-1rem);
    }
  }
}
</style>
