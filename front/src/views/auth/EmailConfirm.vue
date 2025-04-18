<script setup lang="ts">
import type { BackendError } from '~/types'

import { computed, ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

import Alert from '~/components/ui/Alert.vue'
import Input from '~/components/ui/Input.vue'

import axios from 'axios'

interface Props {
  defaultKey: string
}

const props = defineProps<Props>()

const { t } = useI18n()

const labels = computed(() => ({
  confirm: t('views.auth.EmailConfirm.title')
}))

const errors = ref([] as string[])
const key = ref(props.defaultKey)
const isLoading = ref(false)
const success = ref(false)
const submit = async () => {
  isLoading.value = true
  errors.value = []

  try {
    await axios.post('auth/registration/verify-email/', { key: key.value })
    success.value = true
  } catch (error) {
    errors.value = (error as BackendError).backendErrors
  }

  isLoading.value = false
}

onMounted(() => {
  if (key.value) submit()
})
</script>

<template>
  <main
    v-title="labels.confirm"
    class="main"
  >
    <h2>{{ labels.confirm }}</h2>
    <form
      v-if="!success"
      class="ui form"
      @submit.prevent="submit()"
    >
      <Alert
        v-if="errors.length > 0"
        red
      >
        <h4 class="header">
          {{ t('views.auth.EmailConfirm.header.failure') }}
        </h4>
        <ul class="list">
          <li
            v-for="(error, i) in errors"
            :key="i"
          >
            {{ error }}
          </li>
        </ul>
      </Alert>
      <div class="field">
        <label for="confirmation-code">{{ t('views.auth.EmailConfirm.label.confirmationCode') }}</label>
        <Input
          id="confirmation-code"
          v-model="key"
          name="confirmation-code"
          type="text"
          required
        />
      </div>
      <router-link :to="{path: '/login'}">
        {{ t('views.auth.EmailConfirm.link.back') }}
      </router-link>
      <Button
        :class="['ui', {'loading': isLoading}, 'right', 'floated', 'success', 'button']"
        type="submit"
      >
        {{ labels.confirm }}
      </Button>
    </form>
    <Alert
      v-else
      green
    >
      <h4 class="header">
        {{ t('views.auth.EmailConfirm.header.success') }}
      </h4>
      <p>
        {{ t('views.auth.EmailConfirm.message.success') }}
      </p>
      <router-link :to="{name: 'login'}">
        {{ t('views.auth.EmailConfirm.link.login') }}
      </router-link>
    </Alert>
  </main>
</template>
