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
      medium
      title="For music lovers"
      :tags="['rock', 'folk', 'punk']"
    >
      Access your personal music collection from anywhere.
      Funkwhale gives you access to publication and sharing tools
      that you can use to promote your content across the web.
    </Card>
    <!-- #endregion snippet -->
  </Layout>
</template>
