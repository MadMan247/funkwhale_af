<script setup lang="ts">
import type { Actor } from '~/types'

import ChannelsWidget from '~/components/audio/ChannelsWidget.vue'
import ChannelForm from '~/components/audio/ChannelForm.vue'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'
import { useRouter } from 'vue-router'
import { useModal } from '~/ui/composables/useModal.ts'

import Modal from '~/components/ui/Modal.vue'
import Button from '~/components/ui/Button.vue'
import Link from '~/components/ui/Link.vue'

interface Events {
  (e: 'updated', value: Actor): void
}

interface Props {
  object: Actor | null
}

const store = useStore()
const { t } = useI18n()
const router = useRouter()

const emit = defineEmits<Events>()
defineProps<Props>()

const step = ref(1)
const { isOpen } = useModal('createChannel')
const isLoading = ref(false)
const submittable = ref(false)
const category = ref('podcast')

const modalContent = ref()
const createForm = ref()
</script>

<template>
  <section>
    <div>
      <h2 class="ui with-actions header">
        {{ t('views.auth.ProfileOverview.header.channels') }}
        <div
          v-if="store.state.auth.authenticated && object?.full_username === store.state.auth.fullUsername"
          class="actions"
        >
          <Link
            icon="bi-plus"
            thin-font
            force-underline
            :to="useModal('createChannel').to"
          >
            {{ t('views.auth.ProfileOverview.link.addNew') }}
          </Link>
        </div>
      </h2>
      <channels-widget :filters="{scope: `actor:${object?.full_username}`}" />
    </div>

    <Modal
      v-model="isOpen"
      :title="
        step === 1
          ? t('views.auth.ProfileOverview.modal.createChannel.header')
          : category === 'podcast'
            ? t('views.auth.ProfileOverview.modal.createChannel.podcast.header')
            : t('views.auth.ProfileOverview.modal.createChannel.artist.header')
      "
    >
      <channel-form
        ref="createForm"
        :object="null"
        :step="step"
        @loading="isLoading = $event"
        @submittable="submittable = $event"
        @category="category = $event"
        @errored="modalContent.scrollTop = 0"
        @created="router.push({name: 'channels.detail', params: {id: $event.actor.preferred_username}})"
      />
      <template #actions>
        <Button
          secondary
          autofocus
          @click="isOpen = false"
        >
          {{ t('views.auth.ProfileOverview.button.cancel') }}
        </Button>
        <Button
          v-if="step > 1"
          secondary
          @click.stop.prevent="step -= 1"
        >
          {{ t('views.auth.ProfileOverview.button.previous') }}
        </Button>
        <Button
          v-if="step === 1"
          primary
          @click.stop.prevent="step += 1"
        >
          {{ t('views.auth.ProfileOverview.button.next') }}
        </Button>
        <Button
          v-if="step === 2"
          primary
          type="submit"
          :disabled="!submittable && !isLoading"
          :is-loading="isLoading"
          @click.prevent.stop="createForm.submit"
        >
          {{ t('views.auth.ProfileOverview.button.createChannel') }}
        </Button>
      </template>
    </Modal>
  </section>
</template>
