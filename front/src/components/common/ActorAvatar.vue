<script setup lang="ts">
import type { Actor } from '~/types'

import { hashCode, intToRGB } from '~/utils/color'
import { computed } from 'vue'

interface Props {
  actor: { full_username : string; preferred_username?:string; icon?:Actor['icon'] }
}

const props = defineProps<Props>()

const actorColor = computed(() => intToRGB(hashCode(props.actor.full_username)))
const defaultAvatarStyle = computed(() => ({ backgroundColor: `#${actorColor.value}` }))
</script>

<template>
  <img
    v-if="actor.icon && actor.icon.urls.original"
    alt=""
    :src="actor.icon.urls.small_square_crop"
    class="ui tiny avatar circular image"
  >
  <span
    v-else
    :style="defaultAvatarStyle"
    class="ui tiny avatar circular label"
  >
    {{ actor.preferred_username?.[0] || "" }}
  </span>
</template>

<style lang="scss" scoped>
.ui.circular.avatar {
  float: left;
  text-align: center;
  border-radius: 50%;

  &.label {
    align-content: center;
    padding: 4px 8px;
    margin-right: 8px;
  }

}
</style>
