<script setup lang="ts">
import type { User } from '~/types'

import { hashCode, intToRGB } from '~/utils/color'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'

import Link from '~/components/ui/Link.vue'

interface Props {
  user: User
  avatar?: boolean
  solid?: true
}

const store = useStore()
const { t } = useI18n()

const props = withDefaults(defineProps<Props>(), {
  avatar: true
})

const userColor = computed(() => intToRGB(hashCode(props.user.username + props.user.id)))
const defaultAvatarStyle = computed(() => ({ backgroundColor: `#${userColor.value}` }))
</script>

<template>
  <Link
    to="user"
    :title="user.full_username"
    :solid="solid"
    :round="solid"
    class="username"
  >
    <template v-if="avatar">
      <img
        v-if="user.avatar && user.avatar.urls.small_square_crop"
        v-lazy="store.getters['instance/absoluteUrl'](user.avatar.urls.small_square_crop)"
        class="ui avatar tiny circular image"
        alt=""
        @error="(e) => { e.target && user.avatar ? (e.target as HTMLImageElement).src = store.getters['instance/absoluteUrl'](user.avatar.urls.medium_square_crop) : null }"
      >
      <span
        v-else
        :style="defaultAvatarStyle"
        class="ui tiny avatar circular label"
      >
        {{ user.username[0] }}
      </span>
      &nbsp;
    </template>
    {{ t('components.common.UserLink.link.username', {username: user.username}) }}
  </Link>
</template>
