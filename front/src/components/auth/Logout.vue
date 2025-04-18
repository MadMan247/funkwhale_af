<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'

import Button from '~/components/ui/Button.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Alert from '~/components/ui/Alert.vue'
import Link from '~/components/ui/Link.vue'

const store = useStore()
const { t } = useI18n()

const labels = computed(() => ({
  title: t('components.auth.Logout.title')
}))
</script>

<template>
  <main
    v-title="labels.title"
    class="main"
  >
    <div
      v-if="store.state.auth.authenticated"
      class="ui small text container"
    >
      <h2>
        {{ t('components.auth.Logout.header.confirm') }}
      </h2>
      <p>
        {{ t('components.auth.Logout.message.loggedIn', { username: store.state.auth.username }) }}
      </p>
      <Spacer />
      <Button
        solid
        primary
        @click="store.dispatch('auth/logout')"
      >
        {{ t('components.auth.Logout.button.logout') }}
      </Button>
    </div>
    <Alert
      v-else
      yellow
    >
      <h2>
        {{ t('components.auth.Logout.header.unauthenticated') }}
      </h2>
      <template #actions>
        <Link
          solid
          primary
          to="/login"
        >
          {{ t('components.auth.Logout.link.login') }}
        </Link>
      </template>
    </Alert>
  </main>
</template>
