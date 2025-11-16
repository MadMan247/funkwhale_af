<script setup lang="ts">
import type { BackendError } from '~/types'

import { useI18n } from 'vue-i18n'
import { computed, ref } from 'vue'
import { useStore } from '~/store'
import axios from 'axios'

import DangerousButton from '~/components/common/DangerousButton.vue'

import PasswordInput from '~/components/forms/PasswordInput.vue'
import Alert from '~/components/ui/Alert.vue'
import Button from '~/components/ui/Button.vue'

const { t } = useI18n()
const store = useStore()

const subsonicEnabled = computed(() => store.state.instance.settings.subsonic.enabled.value)
const labels = computed(() => ({
  subsonicField: t('components.auth.SubsonicTokenForm.label.subsonicField')
}))

const errors = ref([] as string[])
const success = ref(false)
const isLoading = ref(false)
const token = ref()
const fetchToken = async () => {
  success.value = false
  errors.value = []
  isLoading.value = true

  try {
    const response = await axios.get(`users/${store.state.auth.username}/subsonic-token/`)
    token.value = response.data.subsonic_api_token
  } catch (error) {
    errors.value = (error as BackendError).backendErrors
  }

  isLoading.value = false
}

const showToken = ref(false)
const successMessage = ref('')
const requestNewToken = async () => {
  successMessage.value = t('components.auth.SubsonicTokenForm.message.passwordUpdated')
  success.value = false
  errors.value = []
  isLoading.value = true

  try {
    const response = await axios.post(`users/${store.state.auth.username}/subsonic-token/`)
    showToken.value = true
    token.value = response.data.subsonic_api_token
    success.value = true
  } catch (error) {
    errors.value = (error as BackendError).backendErrors
  }

  isLoading.value = false
}

const disable = async () => {
  successMessage.value = t('components.auth.SubsonicTokenForm.message.accessDisabled')
  success.value = false
  errors.value = []
  isLoading.value = true

  try {
    await axios.delete(`users/${store.state.auth.username}/subsonic-token/`)
    token.value = null
    success.value = true
    showToken.value = false
  } catch (error) {
    errors.value = (error as BackendError).backendErrors
  }

  isLoading.value = false
}

fetchToken()
</script>

<template>
  <form
    class="ui form"
    @submit.prevent="requestNewToken()"
  >
    <h2>
      {{ t('components.auth.SubsonicTokenForm.header.subsonic') }}
    </h2>
    <p
      v-if="!subsonicEnabled"
      class="ui message"
    >
      {{ t('components.auth.SubsonicTokenForm.message.unavailable') }}
    </p>
    <p>
      {{ t('components.auth.SubsonicTokenForm.description.subsonic.paragraph1')
      }}&nbsp;{{ t('components.auth.SubsonicTokenForm.description.subsonic.paragraph2') }}
    </p>
    <p>
      {{ t('components.auth.SubsonicTokenForm.description.subsonic.paragraph3') }}
    </p>
    <p>
      <a
        href="https://docs.funkwhale.audio/user/apps.html#subsonic-compatible-clients"
        target="_blank"
      >
        {{ t('components.auth.SubsonicTokenForm.link.apps') }}
      </a>
    </p>
    <Alert
      v-if="success"
      green
    >
      <h4 class="header">
        {{ successMessage }}
      </h4>
    </Alert>
    <Alert
      v-if="subsonicEnabled && errors.length > 0"
      red
      role="alert"
    >
      <h4 class="header">
        {{ t('components.auth.SubsonicTokenForm.header.error') }}
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
    <template v-if="subsonicEnabled">
      <div
        v-if="token"
        class="field"
      >
        <label
          for="subsonic-password"
          class="visually-hidden"
        >{{ labels.subsonicField }}</label>
        <password-input
          ref="passwordInput"
          :key="token"
          v-model="token"
          field-id="subsonic-password"
          :copy-button="true"
          :default-show="showToken"
        />
      </div>
      <DangerousButton
        v-if="token"
        :is-loading="isLoading"
        :action="requestNewToken"
        :title="t('components.auth.SubsonicTokenForm.modal.newPassword.header')"
      >
        {{ t('components.auth.SubsonicTokenForm.button.newPassword') }}
        <template #content>
          {{ t('components.auth.SubsonicTokenForm.modal.newPassword.content.warning') }}
        </template>
        <template #confirm>
          {{ t('components.auth.SubsonicTokenForm.button.confirmNewPassword') }}
        </template>
      </DangerousButton>
      <Button
        v-else
        primary
        :is-loading="isLoading"
        @click="requestNewToken"
      >
        {{ t('components.auth.SubsonicTokenForm.button.confirmNewPassword') }}
      </Button>
      <DangerousButton
        v-if="token"
        :is-loading="isLoading"
        :action="disable"
        :title="t('components.auth.SubsonicTokenForm.modal.disableSubsonic.header')"
      >
        {{ t('components.auth.SubsonicTokenForm.button.disable') }}
        <template #content>
          {{ t('components.auth.SubsonicTokenForm.modal.disableSubsonic.content.warning') }}
        </template>
        <template #confirm>
          {{ t('components.auth.SubsonicTokenForm.button.confirmDisable') }}
        </template>
      </DangerousButton>
    </template>
  </form>
</template>
