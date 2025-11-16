<script setup lang="ts">
import Layout from '@ui/Layout.vue'
import Section from '@ui/Section.vue'
import Card from '@ui/Card.vue'
</script>

<template>
  <Layout
    article
    class="solid default"
  >
    <!-- #region snippet -->

    <Section
      align-left
      :columns-per-item="3"
      large-section-heading
      h3="Section heading (h3)"
      :action="{
        text:'Link',
        to:'https://funkwhale.audio'
      }"
    >
      <Card
        small
        default
        solid
        blue
        category="h4"
        title="1"
        to="https://funkwhale.audio"
      >
        Content
      </Card>
      <Card
        small
        default
        solid
        red
        category="h4"
        title="2"
        to="https://funkwhale.audio"
      >
        Content
      </Card>
      <Card
        small
        default
        solid
        green
        category="h4"
        title="3"
        to="https://funkwhale.audio"
      >
        Content
      </Card>
    </Section>
  <!-- #endregion snippet -->
  </Layout>
</template>
