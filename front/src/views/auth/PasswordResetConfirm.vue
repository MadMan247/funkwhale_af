<script setup lang="ts">
import type { BackendError } from '~/types'

import { useI18n } from 'vue-i18n'
import { computed, ref } from 'vue'

import axios from 'axios'

import Layout from '~/components/ui/Layout.vue'
import Alert from '~/components/ui/Alert.vue'
import Input from '~/components/ui/Input.vue'
import Link from '~/components/ui/Link.vue'
import Button from '~/components/ui/Button.vue'

interface Props {
  defaultToken: string
  defaultUid: string
}

const props = defineProps<Props>()

const { t } = useI18n()

const labels = computed(() => ({
  changePassword: t('views.auth.PasswordResetConfirm.title')
}))

const newPassword = ref('')
const token = ref(props.defaultToken)
const uid = ref(props.defaultUid)

const errors = ref([] as string[])
const isLoading = ref(false)
const success = ref(false)
const submit = async () => {
  isLoading.value = true
  errors.value = []

  try {
    await axios.post('auth/password/reset/confirm/', {
      uid: uid.value,
      token: token.value,
      new_password1: newPassword.value,
      new_password2: newPassword.value
    })

    success.value = true
  } catch (error) {
    errors.value = (error as BackendError).backendErrors
  }

  isLoading.value = false
}
</script>

<template>
  <main
    v-title="labels.changePassword"
    class="main"
  >
    <h2>{{ labels.changePassword }}</h2>
    <Layout
      v-if="!success"
      form
      @submit.prevent="submit()"
    >
      <Alert
        v-if="errors.length > 0"
        red
      >
        <h4 class="header">
          {{ t('views.auth.PasswordResetConfirm.header.failure') }}
        </h4>
        <ul class="list">
          <li
            v-for="(error, key) in errors"
            :key="key"
          >
            {{ error }}
          </li>
        </ul>
      </Alert>
      <template v-if="token && uid">
        <div class="field">
          <Input
            v-model="newPassword"
            password
            :label="t('views.auth.PasswordResetConfirm.label.newPassword')"
          />
        </div>
        <Layout flex>
          <Link
            solid
            secondary
            :to="{path: '/login'}"
          >
            {{ t('views.auth.PasswordResetConfirm.link.back') }}
          </Link>
          <Button
            :class="['ui', {'loading': isLoading}, 'right', 'floated', 'success', 'button']"
            type="submit"
            auto
            primary
          >
            {{ t('views.auth.PasswordResetConfirm.button.update') }}
          </Button>
        </Layout>
      </template>
      <template v-else>
        <p>
          {{ t('views.auth.PasswordResetConfirm.message.requestSent') }}
        </p>
      </template>
    </Layout>
    <Alert
      v-else
      green
    >
      <h4 class="header">
        {{ t('views.auth.PasswordResetConfirm.header.success') }}
      </h4>
      <p>
        {{ t('views.auth.PasswordResetConfirm.message.success') }}
      </p>
      <router-link :to="{name: 'login'}">
        {{ t('views.auth.PasswordResetConfirm.link.login') }}
      </router-link>
    </Alert>
  </main>
</template>
