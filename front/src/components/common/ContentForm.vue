<script setup lang="ts">
import { useVModel } from '@vueuse/core'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import Textarea from '~/components/ui/Textarea.vue'

interface Events {
  (e: 'update:modelValue', value: string): void
}

interface Props {
  modelValue: string
  placeholder?: string
  autofocus?: boolean
  permissive?: boolean
  required?: boolean
  charLimit?: number
}

const emit = defineEmits<Events>()
const props = withDefaults(defineProps<Props>(), {
  placeholder: undefined,
  autofocus: false,
  charLimit: 5000,
  permissive: false,
  required: false
})

const { t } = useI18n()
const value = useVModel(props, 'modelValue', emit)

const labels = computed(() => ({
  placeholder: props.placeholder ?? t('components.common.ContentForm.placeholder.input')
}))

</script>

<template>
  <Textarea
    v-model="value"
    :required="required || undefined"
    :placeholder="labels.placeholder"
    :autofocus="autofocus || undefined"
    :char-limit="charLimit"
  />
  <p>
    {{ t('components.common.ContentForm.help.markdown') }}
  </p>
</template>
