<script setup lang="ts">
import type { Channel } from '~/types'

import { useI18n } from 'vue-i18n'
import { computed, ref } from 'vue'
import { useStore } from '~/store'
import { useRoute } from 'vue-router'

import LoginModal from '~/components/common/LoginModal.vue'
import Button from '~/components/ui/Button.vue'

const route = useRoute()

interface Events {
  (e: 'unsubscribed'): void
  (e: 'subscribed'): void
}

interface Props {
  channel: Channel
}

const emit = defineEmits<Events>()
const props = defineProps<Props>()

const { t } = useI18n()
const store = useStore()

const isSubscribed = computed(() => store.getters['channels/isSubscribed'](props.channel.uuid))
const title = computed(() => isSubscribed.value
  ? t('components.channels.SubscribeButton.title.unsubscribe')
  : t('components.channels.SubscribeButton.title.subscribe')
)

const message = computed(() => ({
  authMessage: t('components.channels.SubscribeButton.help.auth')
}))

const toggle = async () => {
  await store.dispatch('channels/toggle', props.channel.uuid)

  if (isSubscribed.value) emit('unsubscribed')
  else emit('subscribed')
}

const loginModal = ref()
</script>

<template>
  <Button
    v-if="store.state.auth.authenticated"
    :class="['pink', {'favorited': isSubscribed}]"
    outline
    :aria-pressed="isSubscribed || undefined"
    @click.stop="toggle"
  >
    {{ title }}
  </Button>
  <Button
    v-else
    outline
    icon="bi-heart"
    @click="loginModal.show = true"
  >
    {{ title }}
    <login-modal
      ref="loginModal"
      class="small"
      :next-route="route.fullPath"
      :message="message.authMessage"
      :cover="channel.artist?.cover!"
      @created="loginModal.show = false"
    />
  </Button>
</template>
