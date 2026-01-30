<script setup lang="ts">
import type { RouteLocationRaw } from 'vue-router'
import type { BackendError, Form } from '~/types'

import { computed, reactive, ref, watchEffect } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'

import axios from 'axios'

import LoginForm from '~/components/auth/LoginForm.vue'
import Alert from '~/components/ui/Alert.vue'
import Input from '~/components/ui/Input.vue'
import Textarea from '~/components/ui/Textarea.vue'
import Button from '~/components/ui/Button.vue'
import Layout from '~/components/ui/Layout.vue'

import useLogger from '~/composables/useLogger'

interface Props {
  defaultInvitation?: string | null
  next?: RouteLocationRaw
  buttonClasses?: string
  customization?: Form | null
  fetchDescriptionHtml?: boolean
  signupApprovalEnabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  defaultInvitation: null,
  next: '/',
  buttonClasses: 'success',
  customization: null,
  fetchDescriptionHtml: false,
  signupApprovalEnabled: undefined
})

const { t } = useI18n()
const logger = useLogger()
const store = useStore()

const labels = computed(() => ({
  placeholder: t('components.auth.SignupForm.placeholder.invitation'),
  usernamePlaceholder: t('components.auth.SignupForm.placeholder.username'),
  emailPlaceholder: t('components.auth.SignupForm.placeholder.email')
}))

const signupRequiresApproval = computed(() => props.signupApprovalEnabled ?? store.state.instance.settings.moderation.signup_approval_enabled.value)
const formCustomization = computed(() => props.customization ?? store.state.instance.settings.moderation.signup_form_customization.value)
watchEffect(() => logger.debug(store.state.instance.settings.moderation.signup_approval_enabled.value))

const payload = reactive({
  username: '',
  password1: '',
  email: '',
  invitation: props.defaultInvitation,
  request_fields: {} as Record<string, string | number | string[]>
})

const submitted = ref(false)
const isLoading = ref(false)
const errors = ref([] as string[])
const submit = async () => {
  isLoading.value = true
  errors.value = []

  try {
    await axios.post('auth/registration/', {
      ...payload,
      password2: payload.password1
    })

    logger.info('Successfully created account')
    submitted.value = true
  } catch (error) {
    errors.value = (error as BackendError).backendErrors
  }

  isLoading.value = false
}

const isLoadingInstanceSetting = ref(false)
const fetchInstanceSettings = async () => {
  isLoadingInstanceSetting.value = true
  await store.dispatch('instance/fetchSettings')
  isLoadingInstanceSetting.value = false
}

fetchInstanceSettings()
</script>

<template>
  <div v-if="submitted">
    <Alert
      v-if="signupRequiresApproval"
      yellow
    >
      {{ t('components.auth.SignupForm.message.awaitingReview') }}
    </Alert>
    <Alert
      v-else
      green
    >
      {{ t('components.auth.SignupForm.message.accountCreated') }}
    </Alert>
    <h2>
      {{ t('components.auth.SignupForm.header.login') }}
    </h2>
    <login-form
      style="max-width: 600px"
      button-classes="basic success"
      :show-signup="false"
    />
  </div>
  <Layout
    v-else
    form
    stack
    style="max-width: 600px"
    @submit.prevent="submit()"
  >
    <Alert
      v-if="!store.state.instance.settings.users.registration_enabled.value"
      red
    >
      {{ t('components.auth.SignupForm.message.registrationClosed') }}
    </Alert>
    <Alert
      v-else-if="signupRequiresApproval"
      yellow
    >
      {{ t('components.auth.SignupForm.message.requiresReview') }}
    </Alert>
    <template v-if="formCustomization?.help_text">
      <rendered-description
        :content="formCustomization.help_text"
        :fetch-html="fetchDescriptionHtml"
        :permissive="true"
      />
    </template>
    <Alert
      v-if="errors.length > 0"
      red
    >
      <h4 class="header">
        {{ t('components.auth.SignupForm.header.signupFailure') }}
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
    <Input
      id="username-field"
      ref="username"
      v-model="payload.username"
      :label="t('components.auth.SignupForm.label.username')"
      name="username"
      required
      type="text"
      autofocus
      :placeholder="labels.usernamePlaceholder"
    />
    <Input
      id="email-field"
      ref="email"
      v-model="payload.email"
      :label="t('components.auth.SignupForm.label.email')"
      autocomplete="email"
      name="email"
      required
      type="email"
      :placeholder="labels.emailPlaceholder"
    />
    <Input
      v-model="payload.password1"
      password
      autocomplete="new-password"
      :label="t('components.auth.SignupForm.label.password')"
      field-id="password-field"
    />
    <Input
      v-if="!store.state.instance.settings.users.registration_enabled.value && payload.invitation"
      id="invitation-code"
      v-model="payload.invitation"
      :label="t('components.auth.SignupForm.label.invitation')"
      required
      type="text"
      name="invitation"
      :placeholder="labels.placeholder"
    />
    <div
      v-for="(field, idx) in
      ( formCustomization && (formCustomization.fields.length ?? 0) > 0
        ? formCustomization.fields
        : []
      )"
      :key="idx"
      :class="[{required: field.required}, 'field']"
    >
      <!-- TODO: as string is probably leading to issues with editform. -->
      <Textarea
        v-if="field.input_type === 'long_text'"
        :id="`custom-field-${idx}`"
        v-model="payload.request_fields[field.label] as string"
        :label="field.label"
        :required="field.required || undefined"
        rows="5"
      />
      <Input
        v-else
        :id="`custom-field-${idx}`"
        v-model="payload.request_fields[field.label] as string"
        :label="field.label"
        type="text"
        :required="field.required"
      />
    </div>
    <Button
      primary
      auto
      type="submit"
    >
      {{ t('components.auth.SignupForm.button.create') }}
    </Button>
  </Layout>
</template>
