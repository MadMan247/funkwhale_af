<script setup lang="ts">
import { ref } from 'vue'
import Toggle from '@ui/Toggle.vue'
import Layout from '@ui/Layout.vue'
import Heading from '@ui/Heading.vue'

const isLevel1And2 = ref(false)

</script>

<template>
  <Layout
    article
    class="default"
  >
    <Toggle
      v-model="isLevel1And2"
      label="Also show Headings level 1 and 2"
    />
    <!-- #region snippet -->
    <Heading
      v-if="isLevel1And2"
      h1="Page heading (h1)"
      page-heading
    />
    <Heading
      v-if="isLevel1And2"
      h2="Section heading (h2)"
      section-heading
    />
    <Heading
      v-if="isLevel1And2"
      h2="Large section heading (h2)"
      subsection-heading
    />
    <Heading
      h3="Subsection heading"
      subsection-heading
    />
    <hr>
    <Heading
      h4="Caption"
      caption
    />
    <Heading
      h4="Title"
      title
    />
    <Heading
      h4="Radio"
      radio
    />
    <!-- #endregion snippet -->
  </Layout>
</template>
