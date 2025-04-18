<script setup lang="ts">
import { nextTick, computed, ref, type ComputedRef, onMounted } from 'vue'
import { useTextareaAutosize, computedWithControl, useManualRefHistory, watchDebounced } from '@vueuse/core'
import { useI18n } from "vue-i18n"

import Button from './Button.vue'
import Spacer from './Spacer.vue'
import Markdown from './Markdown.vue'
import Layout from './Layout.vue'

const { t } = useI18n()

const { charLimit = Infinity, placeholder = '', initialLines: minLines = 3, ...props } = defineProps<{
  label?: string,
  placeholder?: string,
  charLimit?: number,
  initialLines?: number | string,
  autofocus?: true,
  required?: true
}>()

const model = defineModel<string>({ required: true })

const { undo, redo, commit: commitHistory, last } = useManualRefHistory(model)
const textarea = ref()
const { triggerResize } = useTextareaAutosize({ input: model, element: textarea })

const commit = () => {
  triggerResize()
  commitHistory()
}

const preview = ref(false)

watchDebounced(model, (value) => {
  if (value !== last.value.snapshot) {
    commit()
  }
}, { debounce: 300 })

const lineNumber = computedWithControl(
  () => [textarea.value, model],
  () => {
    const { selectionStart } = textarea.value ?? {}
    return model.value.slice(0, selectionStart).split('\n').length - 1
  }
)

const updateLineNumber = () => setTimeout(lineNumber.trigger, 0)

const currentLine = computed({
  get: () => (model.value.split('\n')[model.value.split('\n').length > lineNumber.value ? lineNumber.value : 0]),
  set: (line) => {
    const content = model.value.split('\n')
    content[lineNumber.value] = line
    model.value = content.join('\n')
  }
})

// Textarea manipulation
const splice = async (start: number, deleteCount: number, items?: string) => {
  let { selectionStart, selectionEnd } = textarea.value

  const lineBeginning = model.value.slice(0, selectionStart).lastIndexOf('\n') + 1
  let lineStart = selectionStart - lineBeginning
  let lineEnd = selectionEnd - lineBeginning

  const text = currentLine.value.split('')
  text.splice(start, deleteCount, items ?? '')
  currentLine.value = text.join('')

  if (start <= lineStart) {
    lineStart += items?.length ?? 0
    lineStart -= deleteCount
  }

  if (start <= lineEnd) {
    lineEnd += items?.length ?? 0
    lineEnd -= deleteCount
  }

  selectionStart = lineBeginning + Math.max(0, lineStart)
  selectionEnd = lineBeginning + Math.max(0, lineEnd)

  textarea.value.focus()
  await nextTick()
  textarea.value.setSelectionRange(selectionStart, selectionEnd)
}

const newLineOperations = new Map<RegExp, ((event: KeyboardEvent, line: string, groups: string[]) => void)>()
const newline = async (event: KeyboardEvent) => {
  const line = currentLine.value
  for (const regexp of newLineOperations.keys()) {
    const matches = line.match(regexp) ?? []
    if (matches.length > 0) {
      newLineOperations.get(regexp)?.(event, line, matches.slice(1))
    }
  }
}

// Conditions
const isHeading1 = computed(() => currentLine.value.startsWith('# '))
const isHeading2 = computed(() => currentLine.value.startsWith('## '))
const isQuote = computed(() => currentLine.value.startsWith('> '))
const isUnorderedList = computed(() => currentLine.value.startsWith('- ') || currentLine.value.startsWith('* '))
const isOrderedList = computed(() => /^\d+\. /.test(currentLine.value))

const isParagraph = computed(() => !isHeading1.value && !isHeading2.value && !isQuote.value && !isUnorderedList.value && !isOrderedList.value)

// Prefix operations
const paragraph = async (shouldCommit = true) => {
  if (isHeading1.value || isQuote.value || isUnorderedList.value) {
    await splice(0, 2)
    if (shouldCommit) commit()
    return
  }

  if (isHeading2.value || isOrderedList.value) {
    await splice(0, 3)
    if (shouldCommit) commit()
  }
}

const prefixOperation = (prefix: string, condition?: ComputedRef<boolean>) => async () => {
  if (condition?.value) {
    return paragraph()
  }

  await paragraph(false)
  await splice(0, 0, prefix)
  return commit()
}

const heading1 = prefixOperation('# ', isHeading1)
const heading2 = prefixOperation('## ', isHeading2)
const quote = prefixOperation('> ', isQuote)
const orderedList = prefixOperation('1. ', isOrderedList)
const unorderedList = prefixOperation('- ', isUnorderedList)

// Newline operations
const newlineOperation = (regexp: RegExp, newLineHandler: (line: string, groups: string[]) => Promise<void> | void) => {
  newLineOperations.set(regexp, async (event, line, groups) => {
    event.preventDefault()

    if (new RegExp(regexp.toString().slice(1, -1) + '$').test(line)) {
      return paragraph()
    }

    await newLineHandler(line, groups)
    lineNumber.trigger()
    return commit()
  })
}

newlineOperation(/^(\d+)\. /, (line, [lastNumber]) => splice(line.length, 0, `\n${+lastNumber + 1}. `))
newlineOperation(/^- /, (line) => splice(line.length, 0, '\n- '))
newlineOperation(/^> /, (line) => splice(line.length, 0, '\n> '))
newlineOperation(/^\* /, (line) => splice(line.length, 0, '\n* '))

// Inline operations
const inlineOperation = (chars: string) => async () => {
  const { selectionStart, selectionEnd } = textarea.value
  const lineBeginning = model.value.slice(0, selectionStart).lastIndexOf('\n') + 1
  await splice(selectionStart - lineBeginning, 0, chars)
  await splice(selectionEnd - lineBeginning + chars.length, 0, chars)

  const start = selectionStart === selectionEnd
    ? selectionStart + chars.length
    : selectionEnd + chars.length * 2
  textarea.value.setSelectionRange(start, start)
  return commit()
}

const bold = inlineOperation('**')
const italics = inlineOperation('_')
const strikethrough = inlineOperation('~~')

const link = async () => {
  const { selectionStart, selectionEnd } = textarea.value
  const lineBeginning = model.value.slice(0, selectionStart).lastIndexOf('\n') + 1
  await splice(selectionStart - lineBeginning, 0, '[')
  await splice(selectionEnd - lineBeginning + 1, 0, '](url)')
  textarea.value.setSelectionRange(selectionEnd + 3, selectionEnd + 6)
  return commit()
}

// Fix focus
const focus = () => textarea.value.focus()
onMounted(() => {
  if (props.autofocus) focus()
})
</script>

<template>
  <Layout
    stack
    gap-8
    label
    class="funkwhale textarea-label"
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
    <div
      :class="{ 'has-preview': preview }"
      class="funkwhale textarea"
      @mousedown.prevent="focus"
      @mouseup.prevent="focus"
    >
      <Markdown
        :md="model"
        class="preview"
      />
      <textarea
        v-bind="$attrs"
        id="textarea_id"
        ref="textarea"
        v-model="model"
        :maxlength="charLimit"
        :autofocus="autofocus || undefined"
        :required="required"
        :placeholder="placeholder"
        :rows="initialLines"
        :style="`min-height:${((typeof(initialLines) === 'string' ? parseInt(initialLines) : (initialLines ?? 3)) + 1.2) * 1.5}rem`"
        @click="updateLineNumber"
        @mousedown.stop
        @mouseup.stop
        @keydown.left="updateLineNumber"
        @keydown.right="updateLineNumber"
        @keydown.up="updateLineNumber"
        @keydown.down="updateLineNumber"
        @keydown.enter="newline"
        @keydown.ctrl.shift.z.exact.prevent="redo"
        @keydown.ctrl.z.exact.prevent="undo"
        @keydown.ctrl.b.exact.prevent="bold"
        @keydown.ctrl.i.exact.prevent="italics"
        @keydown.ctrl.shift.x.exact.prevent="strikethrough"
        @keydown.ctrl.k.exact.prevent="link"
      />
      <label
        class="textarea-buttons"
        :for="preview ? 'expanded-preview-button' : 'nothing'"
      >
        <Button
          secondary
          square-small
          icon="bi-paragraph"
          :aria-pressed="isParagraph || undefined"
          :disabled="preview"
          @click="paragraph"
        />
        <Button
          secondary
          square-small
          icon="bi-type-h1"
          :aria-pressed="isHeading1 || undefined"
          :disabled="preview"
          @click="heading1"
        />
        <Button
          secondary
          square-small
          icon="bi-type-h2"
          :aria-pressed="isHeading2 || undefined"
          :disabled="preview"
          @click="heading2"
        />
        <Button
          secondary
          square-small
          icon="bi-quote"
          :aria-pressed="isQuote || undefined"
          :disabled="preview"
          @click="quote"
        />
        <Button
          secondary
          square-small
          icon="bi-list-ol"
          :aria-pressed="isOrderedList || undefined"
          :disabled="preview"
          @click="orderedList"
        />
        <Button
          secondary
          square-small
          icon="bi-list-ul"
          :aria-pressed="isUnorderedList || undefined"
          :disabled="preview"
          @click="unorderedList"
        />

        <Spacer />

        <Button
          secondary
          square-small
          icon="bi-type-bold"
          :disabled="preview"
          @click="bold"
        />
        <Button
          secondary
          square-small
          icon="bi-type-italic"
          :disabled="preview"
          @click="italics"
        />
        <Button
          secondary
          square-small
          icon="bi-type-strikethrough"
          :disabled="preview"
          @click="strikethrough"
        />
        <Button
          secondary
          square-small
          icon="bi-link-45deg"
          :disabled="preview"
          @click="link"
        />

        <span
          v-if="charLimit !== Infinity && typeof charLimit === 'number'"
          class="letter-count"
        >{{ charLimit - model.length }}</span>

        <Spacer />

        <Spacer
          v-if="!$slots.default"
          h
          grow
        />

        <slot />

        <Button
          id="expanded-preview-button"
          secondary
          low-height
          min-content
          icon="bi-eye"
          :aria-pressed="preview || undefined"
          @click="preview = !preview"
        >
          {{ t('components.common.ContentForm.button.preview') }}
        </Button>
      </label>
    </div>
  </Layout>
</template>

<style lang="scss">
@import './textarea.scss';
</style>
