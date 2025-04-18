<script setup lang="ts">
import { useTimeAgo } from '@vueuse/core'
import type { Channel } from '~/types'

import OptionsButton from '~/components/ui/button/Options.vue'
import Card from '~/components/ui/Card.vue'

const { podcast } = defineProps<{ podcast: Channel }>()

const timeAgo = useTimeAgo(new Date(podcast.artist?.modification_date ?? new Date()))
</script>

<template>
  <Card
    :title="podcast.uuid || '' /* TODO: This is probably not what we want as a title? */"
    :image="podcast.artist?.cover?.urls.original"
    class="podcast-card"
    :to="/* TODO: where should it link? */ ''"
  >
    {{ podcast.artist?.name }}

    <template #footer>
      {{ timeAgo }}
      <OptionsButton />
    </template>
  </Card>
</template>

<style lang="scss">
@import './style.scss'
</style>
