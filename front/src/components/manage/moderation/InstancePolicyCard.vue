<script setup lang="ts">
import type { InstancePolicy } from '~/types'
import { useI18n } from 'vue-i18n'

import useMarkdown from '~/composables/useMarkdown'

import Button from '~/components/ui/Button.vue'

interface Events {
  (e: 'update'): void
}

interface Props {
  object: InstancePolicy
}

const { t } = useI18n()

const emit = defineEmits<Events>()
const props = defineProps<Props>()

const summary = useMarkdown(() => props.object.summary)
</script>

<template>
  <div>
    <slot />
    <p>
      <i class="bi bi-clock" /><human-date :date="object.creation_date" /> &nbsp;
      <i class="bi bi-person" />{{ object.actor }}  &nbsp;
      <template v-if="object.is_active">
        <i class="bi bi-play" />
        {{ t('components.manage.moderation.InstancePolicyCard.status.enabled') }}
      </template>
      <template v-if="!object.is_active">
        <i class="bi bi-pause" />
        {{ t('components.manage.moderation.InstancePolicyCard.status.paused') }}
      </template>
    </p>
    <div>
      <p><strong>{{ t('components.manage.moderation.InstancePolicyCard.header.rule') }}</strong></p>
      <p v-if="object.block_all">
        <i class="bi bi-ban" />
        {{ t('components.manage.moderation.InstancePolicyCard.label.blockAll') }}
      </p>
      <div
        v-else
        class="ui list"
      >
        <div
          v-if="object.silence_activity"
          class="ui item"
        >
          <i class="bi bi-rss-fill" />
          <div class="content">
            {{ t('components.manage.moderation.InstancePolicyCard.label.muteActivity') }}
          </div>
        </div>
        <div
          v-if="object.silence_notifications"
          class="ui item"
        >
          <i class="bi bi-bell-fill" />
          <div class="content">
            {{ t('components.manage.moderation.InstancePolicyCard.label.muteNotifications') }}
          </div>
        </div>
        <div
          v-if="object.reject_media"
          class="ui item"
        >
          <i class="bi bi-file-earmark-fill" />
          <div class="content">
            {{ t('components.manage.moderation.InstancePolicyCard.label.rejectMedia') }}
          </div>
        </div>
      </div>
    </div>
    <div v-if="summary">
      <div class="ui hidden divider" />
      <p><strong>{{ t('components.manage.moderation.InstancePolicyCard.label.reason') }}</strong></p>
      <sanitized-html :html="summary" />
    </div>
    <div class="ui hidden divider" />
    <Button
      destructive
      icon="bi-pencil"
      @click="emit('update')"
    >
      {{ t('components.manage.moderation.InstancePolicyCard.button.edit') }}
    </Button>
  </div>
</template>
