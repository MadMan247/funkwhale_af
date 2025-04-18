<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import onKeyboardShortcut from '~/composables/onKeyboardShortcut'
import { type ColorProps, type VariantProps, type DefaultProps, type RaisedProps, type PastelProps, color } from '~/composables/color.ts'

import Button from '~/components/ui/Button.vue'
import Layout from '~/components/ui/Layout.vue'

const { icon, placeholder, ...props } = defineProps<{
    icon?: string;
    placeholder?: string;
    password?: true;
    search?: true;
    numeric?: true;
    label?: string;
    autofocus?: boolean;
    reset?:() => void;
  } & (ColorProps | DefaultProps | PastelProps)
    & VariantProps
    & RaisedProps>()

// TODO(A11y): Add `inputmode="numeric" pattern="[0-9]*"` to input if model type is number:
// https://technology.blog.gov.uk/2020/02/24/why-the-gov-uk-design-system-team-changed-the-input-type-for-numbers/
// const isNumeric = restProps.numeric

const showPassword = ref(false)
onKeyboardShortcut('escape', () => showPassword.value = false)

// TODO: Accept fallback $attrs:  `const fallthroughAttrs = useAttrs()`

// TODO: Implement `copy password` button?

const attributes = computed(() => ({
  ...(props.password && !showPassword.value ? { type: 'password' } : {}),
  ...(props.search ? { type: 'search' } : {}),
  ...(props.numeric ? { type: 'numeric' } : {})
}))

const { t } = useI18n()

const input = ref()

const previouslyFocusedElement = ref()

onMounted(() => props.autofocus && nextTick(() => {
  previouslyFocusedElement.value = document.activeElement
  previouslyFocusedElement.value?.blur()
  input.value.focus()
}))

onUnmounted(() =>
  previouslyFocusedElement.value?.focus()
)

const model = defineModel<string|number>({ required: true })
</script>

<template>
  <Layout
    stack
    no-gap
    label
    :class="{ 'has-icon': !!icon }"
    class="funkwhale input"
  >
    <span
      v-if="$slots['label']"
      class="label"
    >
      <slot name="label" />
    </span>

    <span
      v-if="props.label"
      class="label"
    >
      {{ props.label }}
    </span>

    <input
      v-bind="{...$attrs, ...attributes, ...color(props, ['solid', 'default', 'secondary'])()}"
      ref="input"
      v-model="model"
      :autofocus="autofocus || undefined"
      :placeholder="placeholder"
      @click.stop
      @blur="showPassword = false"
    >

    <!-- Left side icon -->

    <div
      v-if="icon"
      class="prefix"
    >
      <i :class="['bi', icon]" />
    </div>

    <!-- Search -->
    <div
      v-if="props.search"
      class="prefix"
    >
      <i class="bi bi-search" />
    </div>

    <!-- Right side -->

    <div
      v-if="$slots['input-right']"
      class="input-right"
    >
      <span class="span-right">
        <slot name="input-right" />
      </span>
    </div>

    <!-- Password -->
    <button
      v-if="props.password"
      style="background:transparent; border:none; appearance:none;"
      role="switch"
      type="button"
      class="input-right show-password"
      title="toggle visibility"
      @click="showPassword = !showPassword"
      @blur="(e) => { if (e.relatedTarget && 'value' in e.relatedTarget && e.relatedTarget.value === model) showPassword = showPassword; else showPassword = false; }"
    >
      <i class="bi bi-eye" />
    </button>

    <!-- Search -->
    <Button
      v-if="props.search"
      solid
      primary
      class="input-right search"
    >
      {{ t('components.Sidebar.link.search') }}
    </Button>

    <!-- Reset -->

    <Button
      v-if="props.reset"
      ghost
      primary
      square-small
      icon="bi-arrow-counterclockwise"
      class="input-right reset"
      :on-click="reset"
      :title="t('components.library.EditForm.button.reset')"
    />
  </Layout>
</template>

<style lang="scss">
@import './input.scss';

input[type=number]::-webkit-inner-spin-button {
    opacity: 1;
}
</style>
