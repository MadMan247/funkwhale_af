<script setup lang="ts">
import { ref } from 'vue'

import Layout from '@ui/Layout.vue'
import Textarea from '@ui/Textarea.vue'

const text = ref("")
</script>

<template>
  <Layout article>
    <!-- #region snippet -->
    <Textarea
      v-model="text"
      label="Textarea"
    />
  <!-- #endregion snippet -->
  </Layout>
</template>
