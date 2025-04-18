<script setup lang="ts">
import type { BackendError } from '~/types'

import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

import Input from '~/components/ui/Input.vue'
import Button from '~/components/ui/Button.vue'
import Layout from '~/components/ui/Layout.vue'
import Link from '~/components/ui/Link.vue'

import axios from 'axios'

interface Props {
  defaultEmail: string
}

const props = defineProps<Props>()

const { t } = useI18n()

const router = useRouter()

const labels = computed(() => ({
  placeholder: t('views.auth.PasswordReset.placeholder.email'),
  reset: t('views.auth.PasswordReset.title')
}))

const email = ref(props.defaultEmail)
const errors = ref([] as string[])
const isLoading = ref(false)
const submit = async () => {
  isLoading.value = true
  errors.value = []

  try {
    await axios.post('auth/password/reset/', { email: email.value })
    router.push({ name: 'auth.password-reset-confirm' })
  } catch (error) {
    errors.value = (error as BackendError).backendErrors
  }

  isLoading.value = false
}
</script>

<template>
  <main
    v-title="labels.reset"
    class="main"
  >
    <h2>
      {{ t('views.auth.PasswordReset.header.reset') }}
    </h2>
    <Layout
      form
      stack
      style="max-width: 600px"
      @submit.prevent="submit()"
    >
      <div
        v-if="errors.length > 0"
        role="alert"
        class="ui negative message"
      >
        <h4 class="header">
          {{ t('views.auth.PasswordReset.header.failure') }}
        </h4>
        <ul class="list">
          <li
            v-for="(error, key) in errors"
            :key="key"
          >
            {{ error }}
          </li>
        </ul>
      </div>
      <p>
        {{ t('views.auth.PasswordReset.help.form') }}
      </p>
      <Input
        id="account-email"
        ref="emailInput"
        v-model="email"
        :label="t('views.auth.PasswordReset.label.email')"
        required
        type="email"
        name="email"
        autofocus
        :placeholder="labels.placeholder"
      />
      <Layout flex>
        <Button
          :class="['ui', {'loading': isLoading}, 'success', 'button']"
          type="submit"
          primary
          auto
        >
          {{ t('views.auth.PasswordReset.button.requestReset') }}
        </Button>
        <Link
          :to="{path: '/login'}"
          solid
          secondary
          button-width
        >
          {{ t('views.auth.PasswordReset.link.back') }}
        </Link>
      </Layout>
    </Layout>
  </main>
</template>
