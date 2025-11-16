<script setup lang="ts">
import Card from "@ui/Card.vue"
import Layout from "@ui/Layout.vue"
</script>

<template>
  <Layout article>
    <!-- #region snippet -->
    <Card
      title="Your Collection"
      :alert-props="{ red: true }"
    >
      <template #alert>
        Please annotate all items with the required metadata.
      </template>
    </Card>
    <!-- #endregion snippet -->
  </Layout>
</template>
