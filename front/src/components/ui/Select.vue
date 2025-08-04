<script setup lang="ts" generic="TOption extends string|number">
import { nextTick, onMounted, onUnmounted, ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { type ColorProps, type VariantProps, type DefaultProps, type RaisedProps, type PastelProps, color } from '~/composables/color.ts'

import Button from '~/components/ui/Button.vue'
import Layout from '~/components/ui/Layout.vue'

/** Select a value from a list of labeled options. */

const props = defineProps<{
    icon?: string;
    placeholder?: string;
    label?: string;
    autofocus?: boolean;
  } & (ColorProps | DefaultProps | PastelProps)
    & VariantProps
    & RaisedProps>()

const { t } = useI18n()

const select = ref()

const previouslyFocusedElement = ref()

onMounted(() => props.autofocus && nextTick(() => {
  previouslyFocusedElement.value = document.activeElement
  previouslyFocusedElement.value?.blur()
  select.value.focus()
  // Use initial value if current is undefined
  current.value = current.value ?? initial.value
}))

onUnmounted(() =>
  previouslyFocusedElement.value?.focus()
)

const current = defineModel<TOption | string>('current')
const options = defineModel<Record<TOption, string>>('options', { required: true })
const initial = defineModel<TOption>('initial')

// const selected =computed(()=> current.value ?? props.placeholder ?? initial.value ?? '')
const selected = computed<TOption | string>({
  get():TOption | string{
    return current.value ?? initial.value ?? props.placeholder ?? ''
  },
  set(newValue: TOption | string) {
    current.value = newValue
  }
})

const reset = () => { current.value = initial.value }
</script>

<template>
  <Layout
    stack
    no-gap
    label
    class="funkwhale select"
  >
    <span
      v-if="$slots['label']"
      :class="$style.label"
    >
      <slot name="label" />
    </span>

    <span
      v-if="label"
      :class="$style.label"
    >
      {{ label }}
    </span>

    <select
      v-bind="{...$attrs, ...color(props, ['solid', 'secondary'])()}"
      ref="select"
      v-model="selected"
      :autofocus="autofocus || undefined"
    >
      <option
        v-for="([option, label_], index) in placeholder ? [[placeholder, placeholder], ...Object.entries(options)] : Object.entries(options)"
        :key="index"
        :value="option"
        :disabled="label_ === placeholder"
        :selected="label_ === placeholder"
      >
        {{ label_ }}
      </option>
    </select>

    <!-- Left side icon -->

    <div
      v-if="icon"
      :class="$style.prefix"
    >
      <i :class="['bi', icon]" />
    </div>

    <!-- Right side -->

    <div
      v-if="$slots['input-right']"
      :class="$style['input-right']"
    >
      <span :class="$style['span-right']">
        <slot name="input-right" />
      </span>
    </div>

    <!-- Reset -->

    <Button
      v-if="initial && initial !== current"
      ghost
      primary
      square-small
      icon="bi-arrow-counterclockwise"
      :class="[$style['input-right'], $style.reset]"
      :on-click="reset"
      :title="t('components.library.EditForm.button.reset')"
    />
  </Layout>
</template>

<style module>
:global(.funkwhale.select) {
  position: relative;
  flex-grow: 1;
  --gap: 8px;
  --height: 48px;
  --v: 8px;

  box-sizing: border-box;

  * {
    box-sizing: border-box;
  }

  > select {
    width: 100%;
    min-height:var(--height);
    padding: calc(var(--v) - 0.5px) 16px calc(var(--v) + 0.5px) 16px;
    font-size: 14px;
    line-height: var(--height);
    border-radius: var(--fw-border-radius);
    color:var(--color);

    &:hover {
      box-shadow: inset 0 0 0 3px var(--border-color);
      border-color: var(--border-color);
      &:global(.primary) {
          outline: 3px solid var(--focus-ring-color);
          box-shadow: none;
      }
    }


    &:focus {
      box-shadow: inset 0 0 0 3px var(--focus-ring-color);
      border-color: var(--focus-ring-color);

      &:focus-visible {
        outline: none;
      }
    }

    select:required:invalid {
        color: var(--fw-placeholder-color);
    }
    option[value=""][disabled] {
      display: none;
    }
  }

  &:has(.prefix>i) > select {
    padding-left: 36px;
  }

  > .label {
    margin-top: -18px;
    padding-bottom: var(--gap);
    font-size: 14px;
    font-weight: 600;
  }

  &:has(>[required])>.label:after {
      content: ' *';
  }

  > .prefix,
  > .input-right {
    align-items: center;
    font-size: 14px;
    color: var(--fw-placeholder-color);
  }

  > .prefix {
    position: absolute;
    left: 0;
    bottom: 0;

    height: calc(100% - 13px);
    min-width: 40px;
    display: flex;

    > i {
      font-size:18px;
      margin: auto;
    }

    &:has(>i) {
        /* Icon prefixes allow click-through; i.e. the user can open the dropdown by clicking the icon */
        pointer-events: none;
    }
  }

  &:has(>.prefix)>input {
    padding-left: 40px;
  }

  > .input-right {
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

  >.reset {
    min-width: auto;
    margin: 4px;
    border-radius: 4px;
    max-height: 36px;
    max-width: 36px;
  }
}
</style>
