<script setup lang="ts">
import type { RouteLocationRaw } from 'vue-router'
import type { Cover } from '~/types'

import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'

import Modal from '~/components/ui/Modal.vue'
import Link from '~/components/ui/Link.vue'
import Spacer from '~/components/ui/Spacer.vue'

interface Props {
  nextRoute: RouteLocationRaw
  message: string
  cover: Cover
}

defineProps<Props>()

const store = useStore()

const show = ref(false)

const { t } = useI18n()
const labels = computed(() => ({
  header: t('components.common.LoginModal.header.unauthenticated'),
  login: t('components.common.LoginModal.link.login'),
  signup: t('components.common.LoginModal.link.signup'),
  description: t('components.common.LoginModal.description.noAccess')
}))
</script>

<template>
  <Modal
    v-model="show"
    :title="labels.header"
  >
    <div
      v-if="cover"
      class="image content"
    >
      <div class="ui medium image">
        <img :src="cover.urls.medium_square_crop">
      </div>
      <div class="description">
        <div class="ui header">
          {{ labels.description }}
        </div>
        <p>
          {{ message }}
        </p>
      </div>
    </div>
    <div
      v-else
      class="content"
    >
      <div class="ui centered header">
        {{ labels.description }}
      </div>
      <p style="text-align: center;">
        {{ message }}
      </p>
    </div>
    <template #actions>
      <Spacer grow />
      <Link
        :to="{path: '/login', query: { next: nextRoute as string }}"
        icon="bi-key-fill"
      >
        {{ labels.login }}
      </Link>
      <Link
        v-if="store.state.instance.settings.users.registration_enabled.value"
        :to="{path: '/signup'}"
        icon="bi-person-fill"
      >
        {{ labels.signup }}
      </Link>
    </template>
  </Modal>
</template>
