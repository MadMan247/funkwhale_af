<script setup lang="ts">
import Card from "@ui/Card.vue"
</script>

<template>
  <div
    class="funkwhale default"
    style="display: contents;"
  >
    <!-- #region snippet -->
    <Card
      small
      title="For music lovers"
      image="https://images.unsplash.com/photo-1524650359799-842906ca1c06?ixlib=rb-1.2.1&dl=te-nguyen-Wt7XT1R6sjU-unsplash.jpg&w=640&q=80&fm=jpg&crop=entropy&cs=tinysrgb"
    />
    <Card
      title="For music lovers"
      :image="{
        src: 'https://images.unsplash.com/photo-1524650359799-842906ca1c06?ixlib=rb-1.2.1&dl=te-nguyen-Wt7XT1R6sjU-unsplash.jpg&w=640&q=80&fm=jpg&crop=entropy&cs=tinysrgb',
        style: 'withPadding',
        label: 'Funkwhale users rejoice'
      }"
    />
    <!-- #endregion snippet -->
  </div>
</template>
