<script setup lang="ts">
import type { components } from '~/generated/types'

import { onBeforeRouteUpdate } from 'vue-router'
import { computed, ref, watch } from 'vue'
import { useClipboard } from '@vueuse/core'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'
import { hashCode, intToRGB } from '~/utils/color'

import UserFollowButton from '~/components/federation/UserFollowButton.vue'
import { useModal } from '~/ui/composables/useModal.ts'

import axios from 'axios'

import useErrorHandler from '~/composables/useErrorHandler'
import RenderedDescription from '~/components/common/RenderedDescription.vue'

import Layout from '~/components/ui/Layout.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Header from '~/components/ui/Header.vue'
import Button from '~/components/ui/Button.vue'
import Link from '~/components/ui/Link.vue'
import Nav from '~/components/ui/Nav.vue'
import Alert from '~/components/ui/Alert.vue'
import Modal from '~/components/ui/Modal.vue'

interface Props {
  username: string
  domain?: string | null
}

const props = withDefaults(defineProps<Props>(), {
  domain: null
})

const store = useStore()

const object = ref<components['schemas']['FullActor'] | null>(null)

const actorColor = computed(() => intToRGB(hashCode(object.value?.full_username)))
const defaultAvatarStyle = computed(() => ({ backgroundColor: `#${actorColor.value}` }))

// TODO: Check if still needed
//const displayName = computed(() => object.value?.name ?? object.value?.preferred_username)

const fullUsername = computed(() => props.domain
  ? `${props.username}@${props.domain}`
  : `${props.username}@${store.getters['instance/domain']}`
)

const routerParams = computed(() => props.domain
  ? { username: props.username, domain: props.domain }
  : { username: props.username }
)

const { t } = useI18n()
const labels = computed(() => ({
  usernameProfile: t('views.auth.ProfileBase.title', { username: props.username })
}))

onBeforeRouteUpdate((to) => {
  to.meta.preserveScrollPosition = true
})

const isLoading = ref(false)
const fetchData = async () => {
  object.value = null
  isLoading.value = true

  try {
    const response = await axios.get(`federation/actors/${fullUsername.value}/`)
    object.value = response.data
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

watch(props, fetchData, { immediate: true })

const { copy, copied, isSupported } = useClipboard()

const tabs = ref([{
  title: t('views.auth.ProfileBase.link.overview'),
  to: { name: 'profile.overview', params: routerParams }
}, {
  title: t('views.auth.ProfileBase.link.activity'),
  to: { name: 'profile.activity', params: routerParams }
}, ...(
  store.state.auth.authenticated && fullUsername.value === store.state.auth.fullUsername
    ? [{
      title: t('views.auth.ProfileBase.link.manageUploads'),
      to: { name: 'profile.manageUploads', params: routerParams }
    }]
    : []
)])

const isOpen = useModal('artist-description').isOpen
</script>

<template>
  <Layout
    v-title="labels.usernameProfile"
    stack
    main
    no-gap
  >
    <!-- TODO: Translate Edit Link -->
    <!-- TODO: `yarn lint:tsc` doesn't understand the `Prop` type for `Header` while the language server does. It may be a question of typescript version... Investigate and fix! https://dev.funkwhale.audio/funkwhale/funkwhale/-/issues/2437 -->
    <!-- @vue-ignore -->
    <Header
      :h1="props.username"
      :action="{
        text: t('views.auth.ProfileBase.link.edit'),
        // @ts-ignore
        to: '/settings',
        // @ts-ignore
        primary: true,
        // @ts-ignore
        solid: true,
        // @ts-ignore
        icon: 'bi-pencil-fill',
        // @ts-ignore
        lowHeight: true
      }"
      no-gap
      page-heading
    >
      <template #image>
        <img
          v-if="object?.icon"
          v-lazy="store.getters['instance/absoluteUrl'](object.icon.urls.large_square_crop)"
          alt=""
          class="avatar"
        >
        <span
          v-else
          :style="defaultAvatarStyle"
          class="ui avatar circular label"
        >
          {{ fullUsername[0] || "" }}
        </span>
      </template>
      <Layout flex>
        <span style="grid-column: 1 / -1">
          {{ fullUsername }}
          <Button
            icon="bi-copy"
            style="margin-left: 8px;"
            :aria-label="t('views.auth.ProfileBase.copyUsername')"
            :title="t('components.common.CopyInput.button.copy')"
            ghost
            secondary
            low-height
            @click="copy(fullUsername)"
          />
        </span>
        <Alert
          v-if="isSupported && copied"
          green
        >
          <Layout flex>
            <i class="bi bi-check" />
            {{ t('components.common.CopyInput.message.success') }}
          </Layout>
        </Alert>
        <Alert
          v-else-if="!isSupported && copied"
          red
        >
          <Layout flex>
            <i class="bi bi-x" />
            {{ t('components.common.CopyInput.message.fail') }}
          </Layout>
        </Alert>
      </Layout>
      <Layout
        flex
        no-gap
      >
        <RenderedDescription
          v-if="object?.summary"
          class="description"
          :content="{ html: object?.summary.html || '' }"
          :truncate-length="100"
        />
        <Spacer grow />
        <Link
          v-if="object?.summary"
          :to="useModal('artist-description').to"
          style="color: var(--fw-primary); text-decoration: underline;"
          thin-font
          force-underline
        >
          {{ t('components.common.RenderedDescription.button.more') }}
        </Link>
      </Layout>
      <Modal
        v-if="object?.summary"
        v-model="isOpen"
        :title="object?.name"
      >
        <img
          v-if="object?.user.avatar"
          v-lazy="object?.user.avatar.urls.original"
          :alt="object?.name"
          style="object-fit: cover; width: 100%; height: 100%;"
        >
        <sanitized-html
          v-if="object?.summary"
          :html="object?.summary.html"
        />
      </Modal>
      <UserFollowButton
        v-if="store.state.auth.authenticated && fullUsername !== store.state.auth.fullUsername && object"
        low-height
        :actor="object"
      />
    </Header>
    <Nav v-model="tabs" />

    <router-view
      :object="object"
      @updated="fetchData"
    />
  </Layout>
</template>

<style scoped>
img.avatar {
  width: 200px;
  height: 200px;
  border-radius: 50%;
}

span.avatar {
  display: block;
  font-size: 150px;
  font-style: normal;
  font-weight: 800;
  text-align: center;
  align-content: center;
  background-color: var(--fw-gray-500);
  border-radius: 50%;
  width: 200px;
  height: 200px;
}

h1 {
  font-size: 48px;
  margin-bottom: 8px;
}

a.edit span {
  color: var(--fw-primary);

  &:hover {
    color: var(--color);
  }
}
</style>
