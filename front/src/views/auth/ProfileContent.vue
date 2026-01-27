<script setup lang="ts">
import type { Actor } from '~/types'

import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'
import { useRouter } from 'vue-router'
import { useModal } from '~/ui/composables/useModal.ts'

import ChannelsWidget from '~/components/audio/ChannelsWidget.vue'
import PlaylistWidget from '~/components/playlists/Widget.vue'
import AlbumWidget from '~/components/album/Widget.vue'
import ChannelForm from '~/components/audio/ChannelForm.vue'

import Layout from '~/components/ui/Layout.vue'
import Header from '~/components/ui/Header.vue'
import Modal from '~/components/ui/Modal.vue'
import Button from '~/components/ui/Button.vue'
import Link from '~/components/ui/Link.vue'

interface Props {
  object: Actor | null
}

const props = defineProps<Props>()

const store = useStore()
const { t } = useI18n()

const scope = computed(() =>
  store.state.auth.authenticated && props.object?.full_username === store.state.auth.fullUsername
    ? 'me'
    : `actor:${props.object?.full_username ?? ''}`
)

const router = useRouter()

const step = ref(1)
const { isOpen } = useModal('createChannel')
const isLoading = ref(false)
const submittable = ref(false)
const category = ref('podcast')

const qualityFilters = computed(() => store.getters['instance/qualityFilters'])

const modalContent = ref()
const createForm = ref()
</script>

<template>
  <Header
    page-heading
    :h1="t('views.auth.ProfileContent.header.content')"
  >
    <!-- TODO: Fix actor radio
    <template #action>
      <radio-button
        v-if="typeof object?.preferred_username === 'string' && typeof object?.full_username === 'string'"
        class="right floated"
        type="account"
        :object-id="{ username: object?.preferred_username, fullUsername: object?.full_username }"
        :client-only="true"
      />
    </template> -->
  </Header>
  <Layout
    main
    stack
    gap-84
  >
    <section>
      <h3 class="ui with-actions header">
        {{ t('views.auth.ProfileContent.header.channels') }}
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
            {{ t('views.auth.ProfileContent.link.addNew') }}
          </Link>
        </div>
      </h3>
      <channels-widget :filters="{scope: scope, content_category: 'music', ...qualityFilters }" />
    </section>

    <channels-widget
      :filters="{ scope: scope, include_channels: true, content_category: 'podcast', ...qualityFilters }"
      :title="t('views.auth.ProfileContent.header.podcasts')"
    />

    <playlist-widget
      :url="'playlists/'"
      :filters="{ scope: scope, playable: true, ...qualityFilters, limit: 4 }"
      :title="t('views.auth.ProfileContent.header.playlists')"
    />

    <album-widget
      :filters="{ scope: scope, playable: true, ...qualityFilters }"
      :limit="8"
      :title="t('views.auth.ProfileContent.header.albums')"
    />

    <Modal
      v-model="isOpen"
      :title="
        step === 1
          ? t('views.auth.ProfileContent.modal.createChannel.header')
          : category === 'podcast'
            ? t('views.auth.ProfileContent.modal.createChannel.podcast.header')
            : t('views.auth.ProfileContent.modal.createChannel.artist.header')
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
          {{ t('views.auth.ProfileContent.button.cancel') }}
        </Button>
        <Button
          v-if="step > 1"
          secondary
          @click.stop.prevent="step -= 1"
        >
          {{ t('views.auth.ProfileContent.button.previous') }}
        </Button>
        <Button
          v-if="step === 1"
          primary
          @click.stop.prevent="step += 1"
        >
          {{ t('views.auth.ProfileContent.button.next') }}
        </Button>
        <Button
          v-if="step === 2"
          primary
          type="submit"
          :disabled="!submittable && !isLoading"
          :is-loading="isLoading"
          @click.prevent.stop="createForm.submit"
        >
          {{ t('views.auth.ProfileContent.button.createChannel') }}
        </Button>
      </template>
    </Modal>
  </Layout>
</template>
