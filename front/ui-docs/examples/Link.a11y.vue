<script setup lang="ts">
import Link from '@ui/Link.vue'
import Layout from '@ui/Layout.vue'
</script>

<template>
  <Layout
    article
    flex
    class="default"
  >
    <!-- #region snippet -->
    <Link
      to="https://funkwhale.audio"
      aria-label="Go to homepage"
      icon="bi bi-house"
    />
    <p>
      Lorem ipsum dolor sit amet, <Link to="https://funkwhale.audio">
        Text-only link in a paragraph
      </Link>, consectetur adipiscing elit.
    </p>
    <Link
      to="https://funkwhale.audio"
      solid
      secondary
    >
      Link with solid secondary background
    </Link>
    <Link
      to="https://funkwhale.audio"
      solid
      primary
    >
      Link with solid primary background
    </Link>
    <!-- #endregion snippet -->
  </Layout>
</template>
