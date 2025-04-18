<script setup lang="ts">

const { as = 'div', html: rawHtml } = defineProps<{ as?:string, html:string }>()

</script>

<template>
  <component
    :is="as"
    v-dompurify-html="rawHtml"
  />
</template>
