<script setup lang="ts">
import { useVModel } from '@vueuse/core'
import { useI18n } from 'vue-i18n'

import Button from '~/components/ui/Button.vue'

interface Events {
  (e: 'update:modelValue', value: boolean): void
}

interface Props {
  modelValue: boolean
}

const { t } = useI18n()

const emit = defineEmits<Events>()
const props = defineProps<Props>()
const value = useVModel(props, 'modelValue', emit)
</script>

<template>
  <Button
    secondary
    low-height
    tiny
    :icon="value ? 'bi-chevron-expand' : 'bi-chevron-contract'"
    class="collapse link"
    @click.prevent="value = !value"
  >
    <span v-if="value">
      {{ t('components.common.CollapseLink.button.expand') }}
    </span>
    <span v-else>
      {{ t('components.common.CollapseLink.button.collapse') }}
    </span>
    <i :class="[{ down: !value, right: value }, 'angle', 'icon']" />
  </Button>
</template>
