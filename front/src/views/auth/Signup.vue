<script setup lang="ts">
import type { RouteLocationRaw } from 'vue-router'

import { useI18n } from 'vue-i18n'
import { computed } from 'vue'

import SignupForm from '~/components/auth/SignupForm.vue'

interface Props {
  defaultInvitation?: string
  next?: RouteLocationRaw
}

withDefaults(defineProps<Props>(), {
  defaultInvitation: undefined,
  next: '/'
})

const { t } = useI18n()

const labels = computed(() => ({
  title: t('views.auth.Signup.title')
}))
</script>

<template>
  <main
    v-title="labels.title"
    class="main"
  >
    <h2>
      {{ t('views.auth.Signup.header.createAccount') }}
    </h2>
    <signup-form
      :default-invitation="defaultInvitation"
      :next="next"
    />
  </main>
</template>
