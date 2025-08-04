<script setup lang="ts">
import { type ColorProps, type DefaultProps, color } from '~/composables/color'
import { watchEffect, ref, nextTick } from 'vue'
import onKeyboardShortcut from '~/composables/onKeyboardShortcut'
import { useI18n } from 'vue-i18n'

import Button from '~/components/ui/Button.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Layout from '~/components/ui/Layout.vue'
import Heading from '~/components/ui/Heading.vue'

const { t } = useI18n()

const props = defineProps<{
  title: string,
  overPopover?: true,
  destructive?: true,
  cancel?: string | true,
  icon?: string,
  autofocus?: true | 'off'
} &(ColorProps | DefaultProps)>()

const isOpen = defineModel<boolean>({ default: false })

const previouslyFocusedElement = ref()

// Handle focus and inertness of the elements behind the modal
watchEffect(() => {
  if (isOpen.value) {
    nextTick(()=>{
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
            { 'is-destructive': destructive,
              'has-alert': !!$slots.alert,
              'over-popover': overPopover,
            }
          ]"
          v-bind="{...$attrs, ...color(props)}"
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
              :class="{'destructive-header': destructive}"
            />
            <Spacer grow />
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
              :on-click="()=>{ isOpen = false }"
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
@import './modal.scss'
</style>
