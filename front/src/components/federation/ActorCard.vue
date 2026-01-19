<script setup lang="ts">
import type { components } from '~/generated/types'
import { computed } from 'vue'

import { useStore } from '~/store'
import Card from '~/components/ui/Card.vue'

// TODO: use Actor (FullActor) until we have a different endpoint for remote user search with FullActor to get user avatars -->
interface Props {
  actor: components['schemas']['Actor']
}

const props = defineProps<Props>()

const store = useStore()
const localurl = store.getters['instance/domain']

function getDomain(id: string): string {
  const url = new URL(id)
  return url.hostname
}

const domain = getDomain(props.actor.id)

const description = computed(() => {
  return props.actor.summary?.length && props.actor.summary.length > 50
    ? props.actor.summary.slice(0, 50) + '...'
    : props.actor.summary || ''
})
</script>

<template>
  <Card
    v-if="props.actor.category === 'podcast' || props.actor.category === 'music'"
    :title="actor.name ?? ''"
    class="actor-card"
    :to="{name: 'channels.detail', params: {id: actor.name +'@' + domain}}"
    small
  >
    <template #image>
      <!-- TODO: add " || actor.icon.urls.medium_square_crop" to v-lazy if FullActor is used in search to get avatar support -->
      <img
        v-if="actor.icon"
        v-lazy="actor.icon.url"
        :alt="actor.name || undefined"
        class="channel-image"
      >
      <i
        v-else
        class="bi bi-person-circle"
        style="font-size: 167px; margin: 16px;"
      />
    </template>

    <div v-text="description" />

    <template
      v-if="domain && domain != localurl"
      #footer
    >
      <i class="bi bi-globe" />
      <span>{{ domain }}</span>
    </template>
  </Card>

  <Card
    v-else
    :title="actor.name ?? ''"
    class="actor-card"
    :to="{name: 'profile.full.content', params: {username: actor.name, domain}}"
    small
  >
    <template #image>
      <!-- TODO: add " || actor.icon.urls.medium_square_crop" to v-lazy if FullActor is used in search to get avatar support -->
      <img
        v-if="actor.icon"
        v-lazy="actor.icon.url"
        :alt="actor.name || undefined"
        class="channel-image"
      >
      <i
        v-else
        class="bi bi-person-circle"
        style="font-size: 167px; margin: 16px;"
      />
    </template>

    <div v-text="description" />

    <template
      v-if="domain && domain != localurl"
      #footer
    >
      <i class="bi bi-globe" />
      <span>{{ domain }}</span>
    </template>
  </Card>
</template>

<style lang="scss" scoped>
.channel-image {
  border-radius: 50%;
  width: 168px;
  height: 168px;
  margin: 16px;
}

.play-button {
  top: 16px;
  right: 16px;
}
</style>
