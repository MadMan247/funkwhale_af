<script setup lang="ts">
import type { BackendError } from '~/types'
import { onBeforeRouteLeave, type RouteLocationRaw, useRouter } from 'vue-router'

import { ref, reactive, computed } from 'vue'
import { useEventListener } from '@vueuse/core'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'

import Alert from '~/components/ui/Alert.vue'
import Input from '~/components/ui/Input.vue'
import Button from '~/components/ui/Button.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Layout from '~/components/ui/Layout.vue'
import Card from '~/components/ui/Card.vue'

interface Props {
  next?: RouteLocationRaw
  buttonClasses?: string
  showSignup?: boolean
  isCard?: true
}

const props = withDefaults(defineProps<Props>(), {
  next: '/library',
  buttonClasses: 'success',
  showSignup: true
})

const domain = location.hostname
const { t } = useI18n()
const store = useStore()
const router = useRouter()

// TODO (wvffle): Move to store logic when migrated to pinia
useEventListener(window, 'beforeunload', () => {
  store.dispatch('auth/tryFinishOAuthFlow')
})

onBeforeRouteLeave(() => {
  store.dispatch('auth/tryFinishOAuthFlow')
})

const credentials = reactive({
  username: '',
  password: ''
})

const labels = computed(() => ({
  usernamePlaceholder: t('components.auth.LoginForm.placeholder.username')
}))

const isLoading = ref(false)
const errors = ref([] as string[])
const submit = async () => {
  isLoading.value = true

  try {
    if (domain === store.getters['instance/domain']) {
      await store.dispatch('auth/login', { credentials })
      await router.push(props.next)
    } else {
      await store.dispatch('auth/oauthLogin', props.next)
    }
  } catch (error: any) {
    const backendError = error as BackendError

    if (backendError.response?.status === 400) {
      errors.value = ['invalid_credentials']
    } else {
      errors.value = backendError.backendErrors ?? [error.message ?? error]
    }
  }

  isLoading.value = false
}
</script>

<template>
  <component
    :is="isCard ? Card : Layout"
    v-bind="$attrs"
    form
    stack
    gap-32
    style="max-width: 600px"
    @submit.prevent="submit()"
  >
    <Alert
      v-if="errors.length > 0"
      red
      style="margin: 0px calc(0px - var(--fw-card-padding) - 1px);"
    >
      <h4 class="header">
        {{ t('components.auth.LoginForm.header.loginFailure') }}
      </h4>
      <component
        :is="errors.length>1 ? 'ul' : 'div'"
        class="list"
      >
        <component
          :is="errors.length>1 ? 'li' : 'div'"
          v-if="errors[0] == 'invalid_credentials' && store.state.instance.settings.moderation.signup_approval_enabled.value"
        >
          {{ t('components.auth.LoginForm.help.approvalRequired') }}
        </component>
        <component
          :is="errors.length>1 ? 'li' : 'div'"
          v-else-if="errors[0] == 'invalid_credentials'"
        >
          {{ t('components.auth.LoginForm.help.invalidCredentials') }}
        </component>
        <component
          :is="errors.length>1 ? 'li' : 'div'"
          v-else
        >
          {{ errors[0] }}
        </component>
      </component>
    </Alert>
    <Spacer h />
    <template v-if="domain === store.getters['instance/domain']">
      <Input
        id="username-field"
        ref="username"
        v-model="credentials.username"
        autocomplete="username"
        required
        name="username"
        type="text"
        autofocus
        :placeholder="labels.usernamePlaceholder"
      >
        <template #label>
          {{ t('components.auth.LoginForm.label.username') }}
          <template v-if="showSignup">
            <span class="middle pipe symbol" />
            <router-link :to="{ path: '/signup' }">
              {{ t('components.auth.LoginForm.link.createAccount') }}
            </router-link>
          </template>
        </template>
      </Input>
      <Input
        v-model="credentials.password"
        password
        name="password-field"
        autocomplete="current-password"
        field-id="password-field"
        required
      >
        <template #label>
          {{ t('components.auth.LoginForm.label.password') }}
          <span class="middle pipe symbol" />
          <router-link
            tabindex="1"
            :to="{ name: 'auth.password-reset', query: { email: credentials.username } }"
          >
            {{ t('components.auth.LoginForm.link.resetPassword') }}
          </router-link>
        </template>
      </Input>
    </template>
    <template v-else>
      <p>
        {{ t('components.auth.LoginForm.message.redirect', { domain: store.getters['instance/domain'] }) }}
      </p>
    </template>
    <Button
      v-if="!isCard"
      solid
      primary
      type="submit"
    >
      {{ t('components.auth.LoginForm.button.login') }}
    </Button>
    <Layout
      v-if="isCard"
      flex
    >
      <Spacer grow />
      <Button
        primary
        raised
        type="submit"
      >
        {{ t('components.auth.LoginForm.button.login') }}
      </Button>
    </Layout>
  </component>
</template>
