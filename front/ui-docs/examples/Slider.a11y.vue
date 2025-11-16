<script setup lang="ts">
import { ref } from 'vue';

import Layout from '@ui/Layout.vue'
import Slider from '@ui/Slider.vue'

const value = ref(1)
</script>

<template>
  <Layout article>
    <!-- #region snippet -->
    <Slider
      v-model="value"
      :options="{1: '1', 2: '2'}"
    />
  <!-- #endregion snippet -->
  </Layout>
</template>
