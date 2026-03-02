<script setup lang="ts">
import { useI18n } from 'vue-i18n'

import Input from '~/components/ui/Input.vue'
import Layout from '~/components/ui/Layout.vue'

const { t } = useI18n()

const emit = defineEmits<{
  (e: 'search', query: string): void
}>()

defineProps<{
  placeholder?: string
}>()

const value = defineModel<
  string
>({ required: true })

</script>

<template>
  <Layout
    form
    flex
    gap-12
    @submit.stop.prevent="emit('search', value)"
  >
    <Input
      v-model="value"
      search
      :label="t('components.common.InlineSearchBar.label.search')"
      :placeholder="placeholder ?? t('components.common.InlineSearchBar.placeholder.search')"
    />
  </Layout>
</template>
