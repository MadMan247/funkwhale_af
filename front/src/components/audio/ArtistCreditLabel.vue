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

// TODO: Fix getRoute

// TODO: check if still needed:
/*
const getRoute = (ac: ArtistCredit) => {
  return {
    name: ac.artist.channel ? 'channels.detail' : 'library.artists.detail',
    params: {
      id: ac.artist.id.toString()
    }
  }
}
*/
</script>

<template>
  <Layout
    flex
    gap-8
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
        <Pill>
          <template #image>
            <img
              v-if="ac.artist.cover && ac.artist.cover.urls.original"
              v-lazy="store.getters['instance/absoluteUrl'](ac.artist.cover.urls.small_square_crop)"
              :alt="ac.artist.name"
            >
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
