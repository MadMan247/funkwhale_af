<script setup lang="ts">
import Layout from '@ui/Layout.vue'
import Spacer from '@ui/Spacer.vue'
</script>

<template>
  <Layout article>
    <!-- #region snippet -->
    <Layout
      flex
      no-gap
      style="outline: 1px dashed currentcolor;"
    >
      Before
      <Spacer />
      After
    </Layout>
  <!-- #endregion snippet -->
  </Layout>
</template>
