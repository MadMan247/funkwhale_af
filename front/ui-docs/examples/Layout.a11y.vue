<script setup lang="ts">
import { ref } from 'vue'

import Button from '@ui/Button.vue'
import Layout from '@ui/Layout.vue'
import Slider from '@ui/Slider.vue'

const screenWidth = ref(360)
</script>

<template>
  <Layout
    article
    class="solid default"
    :class="$style.scrolling"
  >
    <Slider
      v-model="screenWidth"
      label="Container width"
      :options="{360: 'mobile', 720: 'tablet', 1440: 'desktop'}"
    />
    <Layout :class="$style.responsive">
      <!-- #region snippet -->
      <Layout flex>
        <Button>1</Button>
        <Button>2</Button>
        <Button>3</Button>
        <Button>4</Button>
        <Button>5</Button>
      </Layout>
      <Layout grid>
        <Button>1</Button>
        <Button>2</Button>
        <Button>3</Button>
        <Button>4</Button>
        <Button>5</Button>
      </Layout>
      <Layout
        columns
        column-width="200"
      >
        <Button>1</Button>
        <Button>2</Button>
        <Button>3</Button>
        <Button>4</Button>
        <Button>5</Button>
        <Button>6</Button>
      </Layout>
      <!-- #endregion snippet -->
    </Layout>
  </Layout>
</template>

<style module>
    .scrolling {
        overflow: scroll;
    }
    .responsive {
        border: .5px dashed currentcolor;
        transition: width .5s;
        width: v-bind("`${screenWidth}px`")
    }
    </style>
