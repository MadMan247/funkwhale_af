<script setup lang="ts">
import type { components } from '~/generated/types'
import { computed } from 'vue'

import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'

import Button from '~/components/ui/Button.vue'

const { t } = useI18n()

interface Events {
  (e: 'unfollowed'): void
  (e: 'followed'): void
}

interface Props {
  actor: components['schemas']['FullActor']
}

const emit = defineEmits<Events>()
const props = defineProps<Props>()

const store = useStore()
const follow = computed(() => store.getters['users/follow'](props.actor.fid))
const isPending = computed(() => follow.value && follow.value.approved === null)
const isApproved = computed(() => follow.value && follow.value.approved === true)

const toggle = () => {
  if (isPending.value || isApproved.value) {
    emit('unfollowed')
  } else {
    emit('followed')
  }

  return store.dispatch('users/toggle', props.actor.fid)
}
</script>

<template>
  <Button
    secondary
    :class="['ui', 'pink', {'inverted': isApproved || isPending}, {'favorited': isApproved}, 'icon', 'labeled', 'button']"
    :icon="isPending ? 'bi-heart' : 'bi-heart-fill'"
    @click.stop="toggle"
  >
    <span v-if="isApproved">
      {{ t('components.audio.LibraryFollowButton.button.unfollow') }}
    </span>
    <span v-else-if="isPending">
      {{ t('components.audio.LibraryFollowButton.button.cancel') }}
    </span>
    <span v-else>
      {{ t('components.audio.LibraryFollowButton.button.follow') }}
    </span>
  </button>
</template>
