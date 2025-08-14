<script setup lang="ts">
import type { ArtistCredit } from '~/types'
import { useStore } from '~/store'

import Layout from '~/components/ui/Layout.vue'
import Pill from '~/components/ui/Pill.vue'

const store = useStore()

interface Props {
  artistCredit: ArtistCredit[]
}

const props = defineProps<Props>()
</script>

<template>
  <Layout
    flex
    gap-8
    style="/*2px typographic overshoot compensation+ 4px pill paddings */ margin: 0 -6px;"
  >
    <template
      v-for="ac in props.artistCredit"
      :key="ac.artist.id"
    >
      <router-link
        :to="{name: 'library.artists.detail', params: {id: ac.artist.id }}"
        class="username"
        @click.stop.prevent=""
      >
        <Pill v-bind="$attrs">
          <template #image>
            <img
              v-if="ac.artist.cover && ac.artist.cover.urls.original"
              v-lazy="store.getters['instance/absoluteUrl'](ac.artist.cover.urls.small_square_crop)"
              :alt="ac.artist.name"
              @error="(e) => { e.target && ac.artist.cover ? (e.target as HTMLImageElement).src = store.getters['instance/absoluteUrl'](ac.artist.cover.urls.medium_square_crop) : null }"
            />
            <i
              v-else
              class="bi bi-person-circle"
              style="font-size: 24px;"
            />
          </template>
          {{ ac.credit }}
        </Pill>
      </router-link>
      <span>{{ ac.joinphrase }}</span>
    </template>
  </Layout>
</template>

<style lang="scss" scoped>
a.username {
  text-decoration: none;
  height: 25px;
}
</style>
