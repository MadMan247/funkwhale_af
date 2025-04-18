<script setup lang="ts">
import LibraryFilesTable from './FilesTable.vue'

interface Props {
  query: string
}

defineProps<Props>()
</script>

<template>
  <library-files-table :default-query="query" />
</template>
