<script setup lang="ts" generic="T extends string | number">
import { ref, computed, onMounted } from 'vue'
import { useId } from 'vue'

import Layout from '@ui/Layout.vue'
import Spacer from '@ui/Spacer.vue'
import Markdown from '@ui/Markdown.vue'

const id = useId()

// TODO: Make label prop non-optional. It'll be used with aria-labeledby.
const props = defineProps<{
  label?: string,
  options: Record<T, string>,
  autofocus?: true
}>()

const keys = computed(() => Object.keys(props.options) as T[])

const model = defineModel<T | undefined>({ required: true })

const index = computed({
  get() {
    return model.value
      ? keys.value.indexOf(model.value)
      : undefined
  },
  set(newIndex) {
    model.value = newIndex
      ? keys.value[newIndex]
      : undefined
  }
})

const input = ref()

onMounted(() => {
  if (props.autofocus) input.value.focus()
})
</script>

<template>
  <!-- TODO(ally): Decide which label should label which control. Probably the label is for the slider, and the three buttons have their content as label. Open question: Is focusability necessary? -->
  <Layout
    stack
    no-gap
    :class="$style.slider"
    :style="`
      --step-size: calc(100% / ${keys.length + 2});
      --slider-width: calc(var(--step-size) * ${keys.length - 1} + 16px);
      --slider-opacity: ${index === undefined ? .5 : 1};
      --current-step: ${index === undefined ? keys.length - 1 : index};
    `"
  >
    <!-- Label -->

    <label
      :id
      :class="$style.label"
    >
      <slot
        v-if="$slots['label']"
        name="label"
      />
      <template v-else>
        {{ label }}
      </template>
    </label>

    <!-- List of options -->

    <Layout
      flex
      no-gap
    >
      <button
        v-for="key in keys"
        :key="key"
        :class="[$style.key, { [$style.current]: key === model }]"
        style="flex-basis: var(--step-size); padding-bottom: 8px;"
        type="button"
        tabindex="-1"
        aria-hidden="true"
        @click="() => { model = key; input.focus(); }"
      >
        {{ key }}
      </button>
    </Layout>

    <!-- Slider -->

    <span style="position: relative;">
      <input
        ref="input"
        v-model="index"
        type="range"
        style="width: var(--slider-width); cursor: pointer;"
        :aria-labelledby="id"
        :max="keys.length - 1"
        :autofocus="autofocus || undefined"
      >
      <div :class="$style.range" />
      <div
        v-if="model !== undefined"
        :class="$style.pin"
      />
    </span>
    <Spacer size-8 />

    <!-- Description of current option -->

    <span style="position: relative;">
      <span style="display: inline-flex; margin-right: -100%; width: 100%; visibility: hidden;">
        <span
          v-for="key in keys"
          :key="key"
          :class="$style.description"
          :style="`margin-right: -20%; --current-step: 0; color: magenta;`"
        >
          <!-- For some reason, the linter complains that (Record<T, string>)[T] is not string... -->
          <!-- TODO: https://dev.funkwhale.audio/funkwhale/funkwhale/-/issues/2437 -->
          <!-- @vue-ignore -->
          <Markdown :md="options[model]" />
        </span>
      </span>
      <span
        v-if="model !== undefined"
        style="position: absolute;"
        :class="$style.description"
      >
        <!-- For some reason, the linter complains that (Record<T, string>)[T] is not string... -->
        <!-- TODO: https://dev.funkwhale.audio/funkwhale/funkwhale/-/issues/2437 -->
        <!-- @vue-ignore -->
        <Markdown :md="options[model]" />
      </span>
    </span>
  </Layout>
</template>

<style module lang="scss">
@use '~/style/funkwhale.scss';

.slider {
  .label {
    margin-top: -18px;
    padding-bottom: 8px;
    font-size: 14px;
    font-weight: 600;
  }

  .key {
    all: unset;
    cursor: pointer;
    opacity: .7;

    &.current {
      opacity: 1;
    }
  }

  .description {
    font-size: 12px;
    font-weight: 600;
    width: 11rem;
    overflow: visible;
    transition: margin .2s;
    --inset: calc(var(--step-size) * var(--current-step));
    margin-left: var(--inset);
    margin-right: calc(0px - var(--inset));

    p {
      margin: 0;
      line-height: 1.5em;
    }
  }

  // Fake slider
  .range {
    width: calc(var(--step-size) * var(--current-step) + 4px);
    position: absolute;
    top: 6px;
    left: 2.5px;
    height: 8px;
    border-radius: 8px;
    background-color: var(--fw-primary);
    transition: all .1s;
    pointer-events: none;
    opacity: var(--slider-opacity);
  }

  input[type=range]::-moz-range-thumb {
    background-color: var(--fw-primary);
    transition: all .1s;
    pointer-events: none;
  }

  input[type="range"]::-moz-range-track {
    border-radius: 8px;

    @include funkwhale.light-theme {
      background: var(--fw-gray-400);
    }
  }

  .pin {
    border-radius: 8px;
    width: 16px;
    height: 16px;
    left: calc(var(--step-size) * var(--current-step));
    background: var(--fw-primary);
    position: absolute;
    top: 2px;
    margin-left: 2px;
    transition: all .1s;
    pointer-events: none;
  }

  input:focus~.pin,
  input:hover~.pin {
    outline: 1px solid currentColor;
  }

  &[disabled] .pin {
    display: none;
  }

  &[disabled] * {
    pointer-events: none;
  }
}
</style>
