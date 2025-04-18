<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useClipboard, useVModel } from '@vueuse/core'
import { useStore } from '~/store'

import Input from '~/components/ui/Input.vue'

interface Events {
  (e: 'update:modelValue', value: string): void
}

interface Props {
  modelValue: string
  defaultShow?: boolean
  copyButton?: boolean
  fieldId: string
}

const emit = defineEmits<Events>()
const props = withDefaults(defineProps<Props>(), {
  defaultShow: false,
  copyButton: false
})

const value = useVModel(props, 'modelValue', emit)

const { t } = useI18n()
const labels = computed(() => ({
  title: t('components.forms.PasswordInput.title'),
  copy: t('components.forms.PasswordInput.button.copy')
}))

const store = useStore()
const { isSupported: canCopy, copy } = useClipboard({ source: value })
const copyPassword = () => {
  copy()
  store.commit('ui/addMessage', {
    content: t('components.forms.PasswordInput.message.copy'),
    date: new Date()
  })
}
</script>

<template>
  <div>
    <Input
      :id="fieldId"
      v-model="value"
      password
      required
    >
      <template #input-right>
        <button
          v-if="copyButton && canCopy"
          role="switch"
          type="button"
          class="input-right copy"
          :title="labels.copy"
          @click.prevent="copyPassword"
        >
          <i class="bi bi-copy" />
        </button>
      </template>
    </Input>
  </div>
</template>

<style lang="scss" scoped>
  .funkwhale.input .input-right.copy {
    position: absolute;
    background:transparent;
    border:none;
    appearance:none;
    right: 40px;
    bottom: 12px;
    font-size: 18px;
    color: var(--fw-placeholder-color);
  }
</style>
