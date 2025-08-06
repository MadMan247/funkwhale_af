<script setup lang="ts">
import { toRefs, useClipboard } from '@vueuse/core'
import { useI18n } from 'vue-i18n'

import Button from '~/components/ui/Button.vue'
import Input from '~/components/ui/Input.vue'

interface Props {
  value: string
  buttonClasses?: string
  id?: string
  label: string
}

const props = withDefaults(defineProps<Props>(), {
  buttonClasses: 'accent',
  id: 'copy-input'
})

const { t } = useI18n()

const { value } = toRefs(props)
const { copy, isSupported: canCopy, copied } = useClipboard({ source: value, copiedDuring: 5000 })
</script>

<template>
  <Input
    :id="id"
    v-model="value"
    readonly
    :name="id"
    type="text"
    :label="label"
  >
    <template #input-right>
      <Button
        :class="['ui', buttonClasses, 'input-right']"
        min-content
        secondary
        :ghost="!copied || undefined"
        :aria-pressed="copied"
        raised
        icon="bi-copy"
        :disabled="!canCopy || undefined"
        @click="copy()"
      >
        {{ t('components.common.CopyInput.button.copy') }}
      </Button>

      <p
        v-if="copied"
        class="message blue"
      >
        {{ t('components.common.CopyInput.message.success') }}
      </p>
    </template>
  </Input>
</template>

<style scoped>
.input-right {
  position: absolute;
  right: 0px;
  bottom: 0px;
  height: 48px;
  min-width: 48px;
  display: flex;

  .button {
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
    margin-right: 0px !important;
  }
}
p.message {
  background-color: var(--background-color);
  color: var(--color);
  padding: 8px;
  position: absolute;
  top: 32px;
  right: -4px;
  width: max-content;
  box-shadow: 0px 1px 12px 0px var(--shadow-color);
}
</style>
