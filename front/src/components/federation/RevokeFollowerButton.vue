<script setup lang="ts">
import type { components } from '~/generated/types'
import type { BackendError } from '~/types'

import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'
import { ref } from 'vue'
import axios from 'axios'
import useErrorHandler from '~/composables/useErrorHandler'

import DangerousButton from '../common/DangerousButton.vue'
import Alert from '../ui/Alert.vue'

const { t } = useI18n()

interface Events {
  (e: 'revoked'): void
}

interface Props {
  actor: components['schemas']['FullActor']
}

const emit = defineEmits<Events>()
const props = defineProps<Props>()

const store = useStore()
const error = ref<string | null>(null)

const revokeUserFollower = async () => {
  // Revoke an incoming follower (someone who follows you)
  error.value = null
  try {
    const incomingFollow = store.getters['users/incomingFollow'](props.actor.fid)

    if (incomingFollow) {
      await axios.delete(`federation/follows/user/${incomingFollow.uuid}/`)
      // Update store to remove the revoked follower
      const updatedFollows = store.state.users.incomingFollows.filter((f: any) => f.uuid !== incomingFollow.uuid)
      store.commit('users/incomingFollows', updatedFollows)
    }
  } catch (err: any) {
    error.value = err?.message || t('components.federation.RevokeFollowerButton.header.revokeFailure')
    useErrorHandler(err as BackendError)
  }
  emit('revoked')
}
</script>

<template>
  <DangerousButton
    :title="t('components.federation.RevokeFollowerButton.header.title', { username: props.actor.name })"
    :action="revokeUserFollower"
  >
    <template #content>
      <Alert
        v-if="error"
        destructive
      >
        <span>{{ error }}</span>
      </Alert>
      <span>{{ t('components.federation.RevokeFollowerButton.message', { username: props.actor.name }) }}</span>
    </template>
    <label>
      {{ t('components.federation.RevokeFollowerButton.label') }}
    </label>
  </DangerousButton>
</template>
