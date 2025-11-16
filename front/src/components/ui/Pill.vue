<script setup lang="ts">
import { ref, watch, nextTick, computed, onMounted } from 'vue'
import { type ColorProps, type PastelProps, type VariantProps, type RaisedProps, type DefaultProps, color } from '~/composables/color'

import { uniqBy } from 'lodash-es'
import { stringSimilarity } from "string-similarity-js";
import { useI18n } from 'vue-i18n'

import Layout from '@ui/Layout.vue'
import Button from '@ui/Button.vue'
import Input from '@ui/Input.vue'
import Popover from '@ui/Popover.vue'
import PopoverItem from '@ui/popover/PopoverItem.vue'

const { t } = useI18n()

/* Event */

const emit = defineEmits<{
  confirmed: [],
  closed: [],
  opened: []
}>()

/* Model */

// TODO(a11y): Specify precise role (such as status, presentation, checkbox etc.) - currently, it's always `button`.
// This opens an important library architecture decision: Are UI components organized by how they look (Pill, Button, Card...) or by how they behave (Section, Update, Link, SingleSelect, MultiSelect, EitherOr, Trigger, ModalDialog...)? Either way, we'll need to declare valid combinations of shape * behavior for each component (and component variant)
// For the upcoming refactoring and design documents, I feel like we should move from self-contained UI primitives towards composable UX primitives! This will make readoning about possible workflows much easier, and add to the maintainability of the code.
const props = defineProps<{
  noUnderline?: true,
  cancel?: string,
  autofocus?: boolean
} & (PastelProps | ColorProps | DefaultProps)
  & VariantProps
  & RaisedProps
>()

type Item = { type: 'custom' | 'preset', label: string }

const currentItem = defineModel<Item>('current'),
      otherItems = defineModel<Item[]>('others')

// Make sure there are no duplicate labels
const unique = (value: Item[]) => uniqBy(value, item => item.label)

const isEditing = ref<boolean>(false)

/* Lifecycle */

onMounted(() => {
  if (props.autofocus) {
    nextTick(() => {
      if (!currentItem.value || !otherItems.value) return
      clicked()
    })
  }
})

let previousValue: Item | undefined

let previouslyFocusedElement: Element | null

watch(isEditing, (isTrue, wasTrue) => {
  if (!currentItem.value || !otherItems.value) return
  // Cache the previous value, in case the user cancels later
  if (isTrue && !wasTrue) {
    emit('opened')
    previousValue = { ...currentItem.value }
    if (currentItem.value.type === 'preset') {
      otherItems.value.push({...currentItem.value})
      otherItems.value = unique(otherItems.value)
      currentItem.value.type = 'custom'
    }
  // Shift focus between the input and the previously focused element
    previouslyFocusedElement = document.activeElement
  } else if (wasTrue && !isTrue) {
    nextTick(() => (previouslyFocusedElement as HTMLElement)?.focus())

    const matchInOthers
      = otherItems.value.find(({ label }) => label === currentItem.value?.label.trim())

    if (matchInOthers) {
      currentItem.value = { ...matchInOthers }
    }
    otherItems.value = otherItems.value.filter(({ label }) => label !== currentItem.value?.label)

    emit('closed')
  }
})

/* Update */

const clicked = () => {
  if (!currentItem.value || !otherItems.value) return
  if (!isEditing.value) {
    isEditing.value = true
  }
}

const pressedKey = (e: KeyboardEvent) => {
  if (!currentItem.value || !otherItems.value) return

  // confirm or cancel
  switch (e.key) {
    case "Enter":
      confirmed("BestMatch"); break;
    case "Tab":
    // case "ArrowLeft":
    // case "ArrowRight":
    case "Space":
    case ",":
    case " ":
      confirmed("New"); break;
    case "Escape":
      canceled(); break;
  }
}

const releasedKey = () => {
  if (!otherItems.value || !currentItem.value) return
    currentItem.value.label = currentItem.value.label.replace(',', '').replace(' ', '').trim()
}

const canceled = () => {
  if (!previousValue || !currentItem.value || !otherItems.value) return

  const matchInOthers
    = otherItems.value?.find(({ label })=>label === currentItem.value?.label.trim())

  // Reset current label
  currentItem.value
    = matchInOthers
    || {...previousValue}

  // Close dropdown
  isEditing.value = false
}

const confirmed = (option:"BestMatch" | "New") => {
  if (!previousValue || !currentItem.value || !otherItems.value) return

  // Save the choice
  currentItem.value
    = option === "New"
      ? match.value && other.value(match.value).item.isCurrent
        ? match.value
        : { label: currentItem.value.label.replace(',', '').replace(' ', '').trim(), type: "custom" }
      : match.value && option === "BestMatch"
        ? match.value
        : currentItem.value

  // Close dropdown
  isEditing.value = false

  // Tell parent component
  if (previousValue !== currentItem.value)
    emit('confirmed')
}

/* TODO (2.0.0+):
- Add MusicBrainz Tags from the Funkwhale Database
*/
const sortedOthers = computed(()=>
  otherItems.value && currentItem.value
    ? otherItems.value.map((item) =>
      [ 1-stringSimilarity(item.label, currentItem.value?.label || ''), item] as const
    )
    .filter(([delta, item]) =>
      // The current label is empty
      currentItem.value!.label!.length < 2
      // OR The difference between the other label and the current one is less than 100%
      || delta<1
    )
    .sort(([deltaA, a], [deltaB, b]) =>
      // Sort from the lowest to the highest delta
      deltaA - deltaB
    )
    .map(([delta, item], index) =>
      index===0 && delta < 0.99 && currentItem.value && currentItem.value.label.length>0 &&  currentItem.value.label !== previousValue?.label
        ? [-1, item] as const /* It's a match */
        : [delta, item] as const /* It's not a direct match */
      )
    : []
)

const match = computed(()=>
  sortedOthers.value.at(0)?.[0] === -1
    ? sortedOthers.value.at(0)?.[1]
    : undefined
)

/* Properties of any non-current item */
const other = computed(() => (option: Item) => ({
  item: {
    onClick: () => {
      if (!currentItem.value || !otherItems.value) return;
      currentItem.value = { ...option, type: 'custom' }
      otherItems.value = unique([...(
            currentItem.value.label.trim() === '' || otherItems.value.find(({ label }) => label === currentItem.value?.label.trim())
              ? []
              : [{ ...currentItem.value }]
          ), ...otherItems.value.filter(
            ({ label, type }) => label !== option.label || type === 'preset'
          )])
      isEditing.value = false
    },
    isMatch: match.value?.label === option.label,
    isCurrent: option.label === currentItem.value?.label
  },
  action: option.type === 'custom'
    ? {
      title: t('vui.delete'),
      'aria-label': t('vui.delete'),
      icon: 'bi-trash',
      onClick: () => {
        if (!currentItem.value || !otherItems.value) return;
        otherItems.value = otherItems.value.filter(({ label }) => label !== option.label)
      }
    }
  : undefined
} as const))

const current = computed(() => (
  !currentItem.value || !otherItems.value
    ? undefined
    : currentItem.value.label === '' && previousValue?.label !== ''
      ? {
        attributes: {
          title: t('vui.resetTo', { previousValue: (previousValue || currentItem.value)?.label }),
          'aria-label': t('vui.resetTo', { previousValue: (previousValue || currentItem.value)?.label }),
          icon: 'bi-arrow-counterclockwise'
        },
        onClick: () => {
          if (!currentItem.value || !otherItems.value) return;
          currentItem.value = previousValue || currentItem.value
        }
      } as const
    : currentItem.value.label === previousValue?.label && currentItem.value.type==='custom' && !otherItems.value?.find(({ label })=>label === currentItem.value?.label.trim()) && currentItem.value.label !== ''
      ? {
        attributes: {
          title: t('vui.deletItem', { item: currentItem.value.label }),
          'aria-label': t('vui.deletItem', { item: currentItem.value.label }),
          icon: 'bi-trash',
          destructive: true
        },
        onClick: () => {
          if (!currentItem.value || !otherItems.value) return;
          currentItem.value.label = ''
          isEditing.value = false
        }
      } as const
      : currentItem.value.label !== match.value?.label
        && currentItem.value.type === 'custom'
        && currentItem.value.label.trim() !== ''
        && !otherItems.value?.find(({ label }) => label === currentItem.value?.label.trim())
      ? {
        attributes: {
          title: t('vui.addItem', { item: currentItem.value.label }),
          'aria-label': t('vui.addItem', { item: currentItem.value.label }),
          icon: 'bi-plus',
          'solid': !match.value,
          primary: true
        },
        onClick: () => {
          if (!otherItems.value || !currentItem.value || otherItems.value.find(({ label }) => label === currentItem.value?.label.trim()))
            return
          otherItems.value.push({...currentItem.value})
          otherItems.value = unique(otherItems.value)
        }
      } as const
      : undefined
))
</script>

<template>
  <button
    :class="['funkwhale', $style.pill, (props.noUnderline || currentItem) && $style['no-underline']]"
    type="button"
    @click="clicked"
  >
    <Layout
      flex
      no-wrap
      no-gap
      :class="$style.container"
      v-bind="color(props, ['solid', 'interactive', 'secondary'])()"
    >
      <!-- Image -->
      <div
        v-if="!!$slots.image"
        :class="$style['pill-image']"
      >
        <slot name="image" />
      </div>

      <!-- Preset content -->
      <div :class="$style['pill-content']">
        <slot />
        {{ currentItem?.label }} {{ `&ZeroWidthSpace;${''}` }}
        <Popover
          v-if="currentItem && otherItems"
          v-model="isEditing"
        >
          <div />
          <template #items>
            <!-- Current item -->

            <PopoverItem>
              <Input
                v-model="currentItem.label"
                autofocus
                :class="$style.input"
                @keydown.enter.stop.prevent="pressedKey"
                @keydown="pressedKey"
                @keyup="releasedKey"
              />
              <template #after>
                <Button
                  v-if="current"
                  ghost
                  v-bind="current?.attributes"
                  square-small
                  style="border-radius: 0 4px 4px 0;"
                  :class="$style['input-delete-button']"
                  @click.stop.prevent="current?.onClick"
                />
              </template>
            </PopoverItem>
            <hr v-if="sortedOthers.length > 0">

            <!-- Other items, Sorted by matchingness -->

            <PopoverItem
              v-for="[, option] in sortedOthers"
              :key="option.label"
              v-bind="(other(option).item.isMatch || other(option).item.isCurrent
                ? ['aria-selected', 'solid', 'primary'] as const
                : [] as const
              ).reduce((acc, key) => ({ ...acc, [key]: true }), {})"
              :icon-after="other(option).item.isMatch || other(option).item.isCurrent
                ? 'bi-arrow-return-left'
                : undefined"
              :title="other(option).item.isMatch || other(option).item.isCurrent
                ? t('vui.pressKeyToAction', { key: 'ENTER', action: 'accept' })
                : undefined"
              @click.stop.prevent="other(option).item.onClick"
            >
              <span :class="other(option).item.isMatch && $style.match">
                {{ option.label }}
              </span>
              <template #after>
                <Button
                  v-if="other(option).action"
                  round
                  ghost
                  square-small
                  destructive
                  :title="other(option).action?.title"
                  :icon="other(option).action?.icon"
                  @click.stop.prevent="other(option).action?.onClick"
                />
              </template>
            </PopoverItem>

            <hr v-if="cancel && sortedOthers.length > 0">

            <PopoverItem
              v-if="cancel"
              @click.stop.prevent="canceled"
            >
              {{ cancel }}
            </PopoverItem>
          </template>
        </Popover>
      </div>

      <!-- Action -->
      <label
        v-if="!!$slots.action"
        :class="$style['pill-action']"
      >
        <slot name="action" />
      </label>
    </Layout>
  </button>
</template>

<style module lang="scss">
.pill {
  position: relative;
  display: block;
  appearance: none;
  background: transparent;
  outline: 0px transparent;
  border: 0px;

  font-size: 12px;
  line-height: 16px;

  border-radius: 100vh;

  // Negative margins for increased interactive area; visual correction for rounded shape
  margin: -4 -8px;
  padding: 4px 4px;

  border-radius: 100vh;

  width: fit-content;

  cursor:var(--cursor, pointer);

  > .container {

    border-radius: inherit;

    > .pill-content {
      // 1px border
      padding: 4px 9px;
      white-space: nowrap;
      min-width: 56px;
      border-radius: inherit;

      //Works as anchor point for popup
      position: relative;

      &input {
        min-width: 44px; flex-basis: 44px;
      }

      &:focus-visible, &:focus {
        outline: 1px solid var(--focus-ring-color);
        outline-offset: 2px;
      }

      &:has(+.pill-action) {
        margin-right: -26px;
        padding-right: 26px;
      }
    }

    > .pill-image {
      position: relative;
      border-radius: inherit;
      overflow: hidden;
      height: 26px;
      aspect-ratio: 1;
      align-content: center;

      > * {
        height: 100%;
        width: 100%;
      }

      > i.bi {
        font-size: 18px;
      }

      > img {
        object-fit: cover;
      }
    }

    > .pill-action {
      position: relative;
      width: 44px;
      cursor: var(--cursor, pointer);
      height: 44px;
      padding: 9px;
      margin: -9px;
      aspect-ratio: 1;
      border-radius: inherit;
      overflow: hidden;
      align-content: center;
      flex-shrink:0;

      > * {
        height: 100% !important;
        width: 100% !important;
        padding: 0 !important;
      }
    }

  }

  &:hover:not(.no-underline) {
    text-decoration: underline;
  }

  &[disabled] {
    font-weight: normal;
    cursor: default;
  }

  &.is-focused,
  &:focus {
    box-shadow: none !important;
  }
}
.input {
  margin: -4px -16px;
  position: relative;
  &:has(+* .input-delete-button:hover) input{
    background: var(--background-color);
    color: var(--disabled-color) !important;
  }
}
</style>
