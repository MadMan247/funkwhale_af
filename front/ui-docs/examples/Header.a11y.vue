<script setup lang="ts">
import Layout from '@ui/Layout.vue'
import Header from '@ui/Header.vue'
import Spacer from '@ui/Spacer.vue'
import Button from '@ui/Button.vue'

</script>

<template>
  <Layout class="default">
    <!-- #region snippet -->
    <Header
      h3="My title"
      page-heading
    >
      <template #image>
        <img
          style="width: 196px;"
          src="https://images.unsplash.com/photo-1524650359799-842906ca1c06?ixlib=rb-1.2.1&dl=te-nguyen-Wt7XT1R6sjU-unsplash.jpg&w=640&q=80&fm=jpg&crop=entropy&cs=tinysrgb"
          role="presentation"
        >
      </template>
      <div style="height: 48px;">
        My subtitle
      </div>
      <Layout
        flex
        gap-8
      >
        <Button
          raised
          default
          square
        >
          A
        </Button>
        <Button
          raised
          default
          square
        >
          B
        </Button>
        <Spacer
          h
          grow
        />
        <Button
          raised
          default
          square
        >
          C
        </Button>
      </Layout>
    </Header>
    <!-- #endregion snippet -->
  </Layout>
</template>
