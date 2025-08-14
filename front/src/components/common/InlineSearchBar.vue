<script setup lang="ts">
import { useVModel } from '@vueuse/core'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import Input from '~/components/ui/Input.vue'
import Layout from '~/components/ui/Layout.vue'

interface Events {
  (e: 'update:modelValue', value: string): void
  (e: 'search', query: string): void
}

interface Props {
  modelValue: string
  placeholder?: string
}

const emit = defineEmits<Events>()
const props = withDefaults(defineProps<Props>(), {
  placeholder: ''
})

const value = useVModel(props, 'modelValue', emit)

const { t } = useI18n()
const labels = computed(() => ({
  searchPlaceholder: t('components.common.InlineSearchBar.placeholder.search'),
  clear: t('components.common.InlineSearchBar.button.clear')
}))
</script>

<template>
  <Layout
    form
    @submit.stop.prevent="emit('search', value)"
  >
    <Input
      v-model="value"
      search
      name="search-query"
      type="text"
      :label=" t('components.common.InlineSearchBar.label.search')"
      :placeholder="placeholder || labels.searchPlaceholder"
    />
  </Layout>
</template>
