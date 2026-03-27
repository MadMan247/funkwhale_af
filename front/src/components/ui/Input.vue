<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, defineExpose, useId } from 'vue'
import { useI18n } from 'vue-i18n'
import onKeyboardShortcut from '~/composables/onKeyboardShortcut'
import { type ColorProps, type VariantProps, type DefaultProps, type RaisedProps, type PastelProps, color } from '~/composables/color.ts'
import { type WidthProps, width } from '~/composables/width'

import Button from '@ui/Button.vue'
import Layout from '@ui/Layout.vue'

// TODO: Tighten types and expand taxonomy: `['password' | 'search' | 'username' | 'numeric' | 'email']?: true`
const { icon, placeholder, ...props } = defineProps<{
  icon?: string;
  placeholder?: string;
  password?: true;
  search?: true;
  numeric?: true;
  label?: string;
  autofocus?: boolean;
  reset?: () => void;
} & (ColorProps | DefaultProps | PastelProps)
  & VariantProps
  & RaisedProps
  & WidthProps
>()

// TODO(A11y): Add `inputmode="numeric" pattern="[0-9]*"` to input if model type is number:
// https://technology.blog.gov.uk/2020/02/24/why-the-gov-uk-design-system-team-changed-the-input-type-for-numbers/
// const isNumeric = restProps.numeric

const isShowingPassword = ref(false)
onKeyboardShortcut('escape', () => isShowingPassword.value = false)

const id = useId()

// TODO: Accept fallback $attrs:  `const fallthroughAttrs = useAttrs()`

// TODO: Implement `copy password` button?

const attributes = computed(() => ({
  ...(props.password && !isShowingPassword.value ? { type: 'password' } : {}),
  ...(props.search ? { type: 'search' } : {}),
  ...(props.numeric ? { type: 'numeric' } : {})
}))

const { t } = useI18n()

const input = ref()

defineExpose({
  focus: () => input.value.focus()
})

const previouslyFocusedElement = ref()

onMounted(() => props.autofocus && nextTick(() => {
  previouslyFocusedElement.value = document.activeElement
  previouslyFocusedElement.value?.blur()
  input.value.focus()
}))

onUnmounted(() =>
  previouslyFocusedElement.value?.focus()
)

const model = defineModel<string | number>({ required: true })
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
      v-bind="{ ...$attrs, ...attributes, ...color(props, ['solid', 'default', 'secondary'])(width(props)()) }"
      ref="input"
      v-model="model"
      :class="$style.showsTooltip"
      :autofocus="autofocus || undefined"
      :placeholder="placeholder"
      @click.stop
      @blur="isShowingPassword = false"
    >

    <!-- Left side icon -->

    <div
      v-if="icon"
      class="prefix"
      :style="`--input-label-gap: ${label ? 7 : 0}px`"
    >
      <i :class="['bi', icon]" />
    </div>

    <!-- Search -->
    <div
      v-if="props.search"
      class="prefix"
      :style="`--input-label-gap: ${label ? 7 : 0}px`"
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
      :class="$style.showsTooltip"
      v-bind="{ ...$attrs, ...attributes, ...color(props, ['solid', 'default', 'secondary'])() }"
      style="background:transparent; border:none; appearance:none; height:calc(100% - 16px); color:var(--color); cursor:pointer;"
      role="switch"
      type="button"
      class="input-right show-password"
      :title="isShowingPassword ? t('vui.aria.password.hide') : t('vui.aria.password.show')"
      :aria-checked="isShowingPassword"
      :aria-labelledby="id"
      @click="isShowingPassword = !isShowingPassword"
      @blur="(e) => { if (e.relatedTarget && 'value' in e.relatedTarget && e.relatedTarget.value === model) isShowingPassword = isShowingPassword; else isShowingPassword = false; }"
    >
      <i
        class="bi bi-eye"
        role="presentation"
      />
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
      :class="$style.showsTooltip"
      :aria-labelledby="id"
      ghost
      primary
      square-small
      icon="bi-arrow-counterclockwise"
      class="input-right reset"
      :on-click="reset"
      :title="t('components.library.EditForm.button.reset')"
    />

    <!-- Floating label for icon-buttons -->
    <label
      :id
      :class="$style.floating"
    >
      {{ props.reset
        ? t('components.library.EditForm.button.reset')
        : props.password ? (
          isShowingPassword ? t('vui.aria.password.hide') : t('vui.aria.password.show')
        ) : '' }}
    </label>
  </Layout>
</template>

<style>
/* TODO: Move into the style module block so as to not pollute global namespace*/
.funkwhale.input {
  position: relative;
  flex-grow: 1;

  --padding-v: 9px;
  --padding: 16px;

  > input {
    border: none !important;
    width: 100%;
    padding: 10px 16px;
    font-size: 14px;
    font-family: var(--font-family);
    line-height: 28px;
    border-radius: var(--fw-border-radius);
    cursor: text;

    /*@include light-theme {
        &.raised {
          background-color: #ffffff;
          border-color: var(--border-color);
        }
    }*/

    &:hover {
      box-shadow: inset 0 0 0 4px var(--border-color);
    }

    &:focus {
      box-shadow: inset 0 0 0 4px var(--focus-ring-color);

      &:focus-visible {
        outline: none;
      }
    }

    &::placeholder {
      color: var(--fw-placeholder-color);
    }
  }

  &.has-icon > input {
    padding-left: 36px;
  }

  > .label {
    margin-top: -18px;
    padding-bottom: 8px;
    font-size:14px;
    font-weight:600;
  }

  &:has(>[required])>.label:after {
      content: ' *';
  }

  & > .prefix,
  & > .input-right {
    align-items: center;
    font-size: 14px;
    color: var(--fw-placeholder-color);
  }

  & > .prefix {
    position: absolute;
    left: 0;
    bottom: 0;

    height: calc(100% - var(--input-label-gap));
    min-width: 48px;
    display: flex;
    color: var(--color);

    & > i {
      font-size: 18px;
      margin: auto;
    }
  }

  &:has(>.prefix)>input {
    padding-left: 40px;
  }

  & > .input-right {
    position: absolute;
    right: 0px;
    bottom: 0px;
    height: 100%;
    min-width: 48px;
    display: flex;

    > i {
      font-size:18px;
    }

    > .span-right {
      padding: calc(var(--padding-v) - 1px) var(--padding) calc(var(--padding-v) + 1px) var(--padding);

      > .button {
        margin-right: -16px;
        margin-top: 2px;
        border-bottom-left-radius: 0px;
        border-top-left-radius: 0px;
      }
    }

  }

  & > .search {
    > i {
      font-size:18px;
    }
    &.button {
      border-top-left-radius: 0;
      border-bottom-left-radius: 0;
    }
  }
  &:has(>.search)>input {
    padding-right: 140px;
  }

  & > .show-password {
    justify-content:center;
  }
  &:has(>.show-password)>input {
    padding-right: 40px;
  }

  &>.reset {
    min-width: auto;
    margin: 4px;

    /* Make button fit snuggly into rounded border */
    border-radius: 4px;
  }
}
</style>
<style module>
:has(>.showsTooltip:hover)>label.floating:not(:empty) {
    opacity: 1;
}
label.floating {
    position: absolute;
    opacity: 0;
    transition: opacity .2s;
    right: 8px;
    bottom: 37px;
    font-size: 12px;
    background: var(--background-color);
    padding: 0 8px;
    outline: .5px solid currentcolor;
    pointer-events: none;
}
</style>
