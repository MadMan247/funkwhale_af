<script setup lang="ts">
import { computed, nextTick, ref, watch, onMounted } from 'vue'

import { color } from '~/composables/color'

import Pill from './Pill.vue'
import Layout from './Layout.vue'
import Button from './Button.vue'

/**
 * Use `get` to read the pills into your app.
 * Use `set` to write your app's state back into the pills.
 */
const props = defineProps<{
  icon?: string,
  placeholder?: string,
  label?: string,
  cancel?: string,
  get: (v: Model) => void,
  set: (v: Model) => Model
}>()

const model = ref<Model>({ currents: [] })

type Item = { type: 'custom' | 'preset', label: string }
type Model = { currents: Item[], others?: Item[] }

const isStatic = computed(() =>
  !model.value.others
)

const emptyItem = {
  label: '', type: 'custom'
} as const

const nextIndex = ref<number | undefined>(undefined)

const sanitize = () => {
  if (model.value.others) {
    model.value.currents = [...model.value.currents.filter(({ label }) => label !== ''), { ...emptyItem }]
    props.get({ ...model.value, currents: [...model.value.currents.filter(({ label }) => label !== '')] });
  }
}

const next = (index: number) => nextTick(() => { nextIndex.value = index + 1 })

watch(model, () => {
  sanitize()
})

sanitize();

onMounted(() => {
  model.value = props.set(model.value)
})
</script>

<template>
  <Layout
    stack
    no-gap
    label
    :class="$style.pills"
    for="dropdown"
  >
    <!-- Label -->

    <span
      v-if="$slots['label']"
      :class="$style.label"
    >
      <slot name="label" />
    </span>
    <span
      v-if="props.label"
      :class="$style.label"
    >
      {{ props.label }}
    </span>

    <!-- List of Pills -->

    <Layout
      flex
      gap-4
      v-bind="color({}, ['solid', 'default', 'secondary'])()"
      :class="$style.list"
    >
      <Pill
        v-for="(_, index) in model.currents"
        :key="index+1000*(nextIndex || 0)"
        v-model:current="model.currents[index]"
        v-model:others="model.others"
        :cancel="cancel"
        :autofocus="index === nextIndex && nextIndex < model.currents.length"
        outline
        no-underline
        :class="[$style.pill, $style[
          isStatic
            ? 'static'
            : model.currents[index].label === ''
              ? 'empty'
              : model.currents[index].type
        ]]"
        @opened="() => { model = props.set(model); }"
        @closed="() => { sanitize(); }"
        @confirmed="() => { next(index) }"
      >
        <span
          v-if="isStatic"
          :class="$style['pill-content']"
        >{{ model.currents[index].label }}</span>
        <template
          v-if="model.others && model.currents[index].label !== ''"
          #action
        >
          <Button
            ghost
            primary
            round
            icon="bi-x"
            title="Deselect"
            @click.stop.prevent="() => {
              if (!model.others) return
              model.others.push({...model.currents[index]});
              model.currents[index] = {label: '', type: 'custom'}
              sanitize()
            }"
          />
        </template>
      </Pill>
    </Layout>
  </Layout>
</template>

<style module lang="scss">
  .pills {
    >.label {
      margin-top: -18px;
      padding-bottom: 8px;
      font-size: 14px;
      font-weight: 600;
    }
    >.list {
      position: relative;

      // Compensation for round shapes -> https://en.wikipedia.org/wiki/Overshoot_(typography)
      margin: 0 -4px;

      // padding: 4px;
      border-radius: 22px;

      gap: 8px;
      padding: 2px;

      min-height: 36px;

      .empty {
        flex-grow: 1;
      }
    }
    &:hover:has(select)>.list {
      box-shadow: inset 0 0 0 4px var(--border-color)
    }
    :has(>select:focus) {
      box-shadow: inset 0 0 0 4px var(--focus-ring-color)
    }
  }
</style>
