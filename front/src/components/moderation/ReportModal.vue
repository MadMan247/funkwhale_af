<script setup lang="ts">
import type { BackendError } from '~/types'

import axios from 'axios'
import ReportCategoryDropdown from '~/components/moderation/ReportCategoryDropdown.vue'
import { computed, ref, watchEffect } from 'vue'
import { useStore } from '~/store'
import { useI18n } from 'vue-i18n'

import ContentForm from '../common/ContentForm.vue'

import Modal from '~/components/ui/Modal.vue'
import Button from '~/components/ui/Button.vue'
import Alert from '~/components/ui/Alert.vue'

interface ReportType {
  anonymous: boolean
  type: string
}

const store = useStore()
const target = computed(() => store.state.moderation.reportModalTarget)

const forward = ref(false)
const summary = ref('')
const category = ref('')
const submitterEmail = ref('')

const reportTypes = ref([] as ReportType[])
const allowedCategories = computed(() => {
  if (store.state.auth.authenticated) {
    return []
  }

  return reportTypes.value
    .filter((type) => type.anonymous === true)
    .map((type) => type.type)
})

const canSubmit = computed(() => store.state.auth.authenticated || allowedCategories.value.length > 0)

const targetDomain = computed(() => {
  if (!target.value._obj) {
    return
  }

  const fid = target.value.type === 'channel' && target.value._obj.actor
    ? target.value._obj.actor.fid
    : target.value._obj.fid

  return !fid
    ? store.getters['instance/domain']
    : new URL(fid).hostname
})

const isLocal = computed(() => store.getters['instance/domain'] === targetDomain.value)

const errors = ref([] as string[])

const show = computed({
  get: () => store.state.moderation.showReportModal,
  set: (value: boolean) => {
    store.commit('moderation/showReportModal', value)
    errors.value = []
  }
})

const isLoading = ref(false)

// TODO (wvffle): MOVE ALL use*() METHODS SOMEWHERE TO THE TOP
const { t } = useI18n()

const submit = async () => {
  isLoading.value = true

  const payload = {
    target: { ...target.value, _obj: undefined },
    summary: summary.value,
    type: category.value,
    forward: forward.value,
    submitter_email: !store.state.auth.authenticated
      ? submitterEmail.value
      : undefined
  }

  try {
    const response = await axios.post('moderation/reports/', payload)
    show.value = false

    store.commit('moderation/contentFilter', response.data)
    store.commit('ui/addMessage', {
      content: t('components.moderation.ReportModal.message.submissionSuccess'),
      date: new Date()
    })

    summary.value = ''
    category.value = ''
  } catch (error) {
    errors.value = (error as BackendError).backendErrors
  }

  isLoading.value = false
}

const isLoadingReportTypes = ref(false)
watchEffect(async () => {
  if (!store.state.moderation.showReportModal || store.state.auth.authenticated) {
    return
  }

  isLoadingReportTypes.value = true

  try {
    const response = await axios.get('instance/nodeinfo/2.1/')
    reportTypes.value = response.data.metadata.reportTypes ?? []
  } catch (error) {
    store.commit('ui/addMessage', {
      content: t('components.moderation.ReportModal.error.nodeinfoFetch', { error: `${error}` }),
      date: new Date()
    })
  }

  isLoadingReportTypes.value = false
})
</script>

<template>
  <Modal
    v-model="show"
    :title="target ? t('components.moderation.ReportModal.header.modal') : errors.length > 0 ? t('components.moderation.ReportModal.header.submissionFailure') : ''"
    :cancel="t('components.moderation.ReportModal.button.cancel')"
    is-destructive
  >
    <h2
      v-if="target"
      class="ui header"
    >
      <div class="ui sub header">
        {{ target.typeLabel }}
        <span class="middle hyphen symbol" />
        {{ target.label }}
      </div>
    </h2>
    <div class="scrolling content">
      <div class="description">
        <Alert
          v-if="errors.length > 0"
          red
        >
          <ul class="list">
            <li
              v-for="(error, key) in errors"
              :key="key"
            >
              {{ error }}
            </li>
          </ul>
        </Alert>
      </div>
      <p>
        {{ t('components.moderation.ReportModal.description.modal') }}
      </p>
      <form
        v-if="canSubmit"
        id="report-form"
        class="ui form"
        @submit.prevent="submit"
      >
        <div class="fields">
          <report-category-dropdown
            v-model="category"
            class="ui required eight wide field"
            :required="true"
            :empty="true"
            :restrict-to="allowedCategories"
            :label="true"
          />
          <div
            v-if="!store.state.auth.authenticated"
            class="ui eight wide required field"
          >
            <label for="report-submitter-email">
              {{ t('components.moderation.ReportModal.label.email') }}
            </label>
            <input
              id="report-submitter-email"
              v-model="submitterEmail"
              type="email"
              name="report-submitter-email"
              required
            >
            <p>
              {{ t('components.moderation.ReportModal.description.email') }}
            </p>
          </div>
        </div>
        <div class="ui field">
          <label for="report-summary">
            {{ t('components.moderation.ReportModal.label.message') }}
          </label>
          <p>
            {{ t('components.moderation.ReportModal.description.message') }}
          </p>
          <content-form
            v-model="summary"
            field-id="report-summary"
            :rows="8"
          />
        </div>
        <div
          v-if="!isLocal"
          class="ui field"
        >
          <div class="ui checkbox">
            <input
              id="report-forward"
              v-model="forward"
              type="checkbox"
            >
            <label for="report-forward">
              <strong>
                {{ t('components.moderation.ReportModal.label.forwardToDomain', {domain: targetDomain}) }}
              </strong>
              <p>
                {{ t('components.moderation.ReportModal.description.forwardToDomain') }}
              </p>
            </label>
          </div>
        </div>
        <div class="ui hidden divider" />
      </form>
      <div
        v-else-if="isLoadingReportTypes"
        class="ui inline active loader"
      />
      <div
        v-else
        role="alert"
        class="ui warning message"
      >
        <h4 class="header">
          {{ t('components.moderation.ReportModal.header.disabled') }}
        </h4>
      </div>
    </div>
    <template #actions>
      <Button
        v-if="canSubmit"
        destructive
        :is-loading="isLoading"
        type="submit"
        form="report-form"
      >
        {{ t('components.moderation.ReportModal.button.submit') }}
      </Button>
    </template>
  </Modal>
</template>
