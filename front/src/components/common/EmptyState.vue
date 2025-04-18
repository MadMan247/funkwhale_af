<script setup lang="ts">
import { useI18n } from 'vue-i18n'

import Button from '~/components/ui/Button.vue'
import Alert from '~/components/ui/Alert.vue'
import Spacer from '~/components/ui/Spacer.vue'

interface Events {
  (e: 'refresh'): void
}

interface Props {
  refresh?: boolean
}

const { t } = useI18n()

const emit = defineEmits<Events>()
withDefaults(defineProps<Props>(), {
  refresh: false
})
</script>

<template>
  <Alert
    blue
    align-items="center"
  >
    <h4 class="ui header">
      <div class="content">
        <slot name="title">
          <i class="bi bi-search" />
          {{ t('components.common.EmptyState.header.noResults') }}
        </slot>
      </div>
    </h4>
    <div class="inline center aligned text">
      <slot />
      <Spacer :size="16" />
      <Button
        v-if="refresh"
        primary
        @click="emit('refresh')"
      >
        {{ t('components.common.EmptyState.button.refresh') }}
      </Button>
    </div>
  </Alert>
</template>
