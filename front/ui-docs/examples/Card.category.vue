<script setup lang="ts">
import Card from "@ui/Card.vue"
import Layout from "@ui/Layout.vue"
</script>

<template>
  <Layout
    article
    flex
  >
    <!-- #region snippet -->
    <Card
      flat
      solid
      purple
      category
      min-content
      title="My Favorites"
    />...
    <Card
      category="h1"
      title="What others listen to"
    />...
    <!-- #endregion snippet -->
  </Layout>
</template>
