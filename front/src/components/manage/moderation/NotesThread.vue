<script setup lang="ts">
import type { Note } from '~/types'

import { useMarkdownRaw } from '~/composables/useMarkdown'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

import axios from 'axios'

import useErrorHandler from '~/composables/useErrorHandler'

import DangerousButton from '~/components/common/DangerousButton.vue'

import Alert from '~/components/ui/Alert.vue'
import Layout from '~/components/ui/Layout.vue'
import Spacer from '~/components/ui/Spacer.vue'

interface Events {
  (e: 'deleted', uuid: string): void
}
interface Props {
  notes: Note[]
}

const { t } = useI18n()

const emit = defineEmits<Events>()
defineProps<Props>()

const isLoading = ref(false)
const remove = async (note: Note) => {
  isLoading.value = true

  try {
    await axios.delete(`manage/moderation/notes/${note.uuid}/`)
    emit('deleted', note.uuid)
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}
</script>

<template>
  <div class="ui feed">
    <Alert
      v-for="note in notes"
      :key="note.uuid"
      blue
      class="event"
    >
      <div class="label">
        <i
          class="bi bi-chat-dots-fill"
          style="font-size: 22px;"
        />
      </div>
      <Spacer :size="16" />
      <Layout
        flex
        gap-16
        class="summary"
      >
        <actor-link
          :admin="true"
          :actor="note.author"
        />
        <div class="date">
          <human-date :date="note.creation_date" />
        </div>
      </Layout>
      <expandable-div :content="note.summary">
        <sanitized-html :html="useMarkdownRaw(note.summary ?? '')" />
      </expandable-div>
      <template #actions>
        <dangerous-button
          :is-loading="isLoading"
          low-height
          icon="bi-trash"
          :title="t('components.manage.moderation.NotesThread.modal.delete.header')"
          @confirm="remove(note)"
        >
          {{ t('components.manage.moderation.NotesThread.button.delete') }}

          <template #modal-content>
            {{ t('components.manage.moderation.NotesThread.modal.delete.content.warning') }}
          </template>
          <template #modal-confirm>
            {{ t('components.manage.moderation.NotesThread.button.delete') }}
          </template>
        </dangerous-button>
      </template>
    </Alert>
  </div>
</template>
