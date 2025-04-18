<script setup lang="ts">
import { useI18n } from 'vue-i18n'

import EditsCardList from '~/components/manage/library/EditsCardList.vue'

import Header from '~/components/ui/Header.vue'

interface Props {
  defaultQuery?: string
}

withDefaults(defineProps<Props>(), {
  defaultQuery: ''
})

const { t } = useI18n()

// TODO: Do we want to use this title?
// const labels = computed(() => ({
//   title: t('views.admin.library.EditsList.title')
// }))
</script>

<template>
  <Header
    page-heading
    :h1="t('views.admin.library.EditsList.header.edits')"
  />
  <edits-card-list
    :update-url="true"
    :default-query="defaultQuery"
  />
</template>
