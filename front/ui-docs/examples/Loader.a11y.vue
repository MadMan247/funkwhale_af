<script setup lang="ts">
import { ref } from 'vue'

import Layout from '@ui/Layout.vue'
import Loader from '@ui/Loader.vue'
import Button from '@ui/Button.vue'

const key = ref(0)
</script>

<template>
  <Layout
    flex
    article
  >
    <!-- #region snippet -->
    <Button @click="key++">
      Reload
    </Button>
    <Loader :key />
  <!-- #endregion snippet -->
  </Layout>
</template>
