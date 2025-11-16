<script setup lang="ts">
import { ref } from 'vue'

import Layout from '@ui/Layout.vue'
import Pagination from '@ui/Pagination.vue'

// #region model
const page = ref(1)
const pages = 10
// #endregion model
</script>

<template>
  <Layout article>
    <!-- #region snippet -->
    <Pagination
      v-model:page="page"
      :pages
    />
  <!-- #endregion snippet -->
  </Layout>
</template>
