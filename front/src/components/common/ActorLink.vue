<script setup lang="ts">
import type { Actor } from '~/types'
import type { components } from '~/generated/types'

import { toRefs } from '@vueuse/core'
import { computed } from 'vue'
import { truncate } from '~/utils/filters'

import Pill from '~/components/ui/Pill.vue'

interface Props {
  actor: Actor | components['schemas']['APIActor']
  avatar?: boolean
  admin?: boolean
  displayName?: boolean
  truncateLength?: number
  discrete?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  avatar: true,
  admin: false,
  displayName: false,
  truncateLength: 30,
  discrete: false
})

const { displayName, actor, truncateLength, admin, avatar } = toRefs(props)

const repr = computed(() => {
  const name = displayName.value || actor.value.is_local
    ? actor.value.preferred_username
    : actor.value.full_username

  return truncate(name || '', truncateLength.value)
})

const url = computed(() => {
  if (admin.value) {
    return { name: 'manage.moderation.accounts.detail', params: { id: actor.value.full_username } }
  }

  if (actor.value?.is_local) {
    return { name: 'profile.overview', params: { username: actor.value?.preferred_username } }
  }

  return {
    name: 'profile.full.overview',
    params: {
      username: actor.value?.preferred_username,
      domain: actor.value?.domain
    }
  }
})
</script>

<template>
  <router-link
    :to="url"
    class="username"
    @click.stop.prevent=""
  >
    <Pill>
      <template #image>
        <actor-avatar
          v-if="avatar"
          :actor="actor"
        />
        <i
          v-else
          class="bi bi-person-circle"
          style="font-size: 24px;"
        />
      </template>
      {{ repr }}
    </Pill>
  </router-link>
</template>

<style lang="scss" scoped>
a.username {
  text-decoration: none;
}
</style>
