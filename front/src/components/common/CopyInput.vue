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
  id: 'copy-input',
  label: 'label'
})

const { t } = useI18n()

const { value } = toRefs(props)
const { copy, isSupported: canCopy, copied } = useClipboard({ source: value, copiedDuring: 5000 })
</script>

<template>
  <p
    v-if="copied"
    class="message"
  >
    {{ t('components.common.CopyInput.message.success') }}
  </p>
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
        :disabled="!canCopy || undefined"
        @click="copy()"
      >
        <i class="bi bi-copy" />
        {{ t('components.common.CopyInput.button.copy') }}
      </Button>
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
  background-color: var(--hover-background-color);
  padding: 8px;
  position: absolute;
  bottom: -32px;
  right: 0px;
}
</style>
