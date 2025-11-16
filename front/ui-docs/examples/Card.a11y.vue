<script setup lang="ts">
import Card from "@ui/Card.vue"
import Link from "@ui/Link.vue"
import Layout from "@ui/Layout.vue"
import OptionsButton from '@ui/button/Options.vue'

import whales from '../../src/assets/network.png'

defineProps < { level: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' }>()

const toggleMenu = () => { }
</script>

<template>
  <Layout
    article
    class="default"
  >
    <!-- #region snippet -->
    <Card
      title="Card"
      :category="level"
      :image="{
        src: whales,
        label: 'Colorful whales communicating in a network'
      }"
      :tags="['Tag']"
      icon="bi-check-lg"
    >
      <Link to="https://funkwhale.audio">
        Inline link
      </Link>
      <template #action>
        <Link
          solid
          grow
          to="./"
        >
          Action link
        </Link>
      </template>
    </Card>
    <Card
      to="./"
      title="Link"
      :category="level"
    >
      <template #topright>
        <OptionsButton
          title="More"
          aria-label="Toggle Card menu"
          @click.stop.prevent="toggleMenu"
        />
      </template>
    </Card>
    <!-- #endregion snippet -->
  </Layout>
</template>
