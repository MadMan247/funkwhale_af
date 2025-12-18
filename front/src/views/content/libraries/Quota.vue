<script setup lang="ts">
import type { ImportStatus } from '~/types'

import { compileTokens } from '~/utils/search'
import { humanSize } from '~/utils/filters'
import { computed, ref } from 'vue'

import useErrorHandler from '~/composables/useErrorHandler'

import axios from 'axios'
import { useI18n } from 'vue-i18n'

import DangerousButton from '~/components/common/DangerousButton.vue'

import Alert from '~/components/ui/Alert.vue'
import Layout from '~/components/ui/Layout.vue'
import Link from '~/components/ui/Link.vue'
import Spacer from '~/components/ui/Spacer.vue'

const { t } = useI18n()

const quotaStatus = ref()
const progress = computed(() => !quotaStatus.value
  ? 0
  : Math.min(quotaStatus.value.current * 100 / quotaStatus.value.max, 100)
)

const isLoading = ref(false)
const fetchData = async () => {
  isLoading.value = true

  try {
    const response = await axios.get('users/me/')
    quotaStatus.value = response.data.quota_status
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

fetchData()

const emit = defineEmits<{
  purged: [status: ImportStatus]
}>()

const purge = async (status: ImportStatus) => {
  try {
    await axios.post('uploads/action/', {
      action: 'delete',
      objects: 'all',
      filters: { import_status: status }
    })

    await fetchData()
    emit('purged', status)
  } catch (error) {
    useErrorHandler(error as Error)
  }
}

const purgeSkippedFiles = () => purge('skipped')
const purgePendingFiles = () => purge('pending')
const purgeErroredFiles = () => purge('errored')
</script>

<template>
  <Layout flex>
    <Loader v-if="isLoading" />
    <h3>{{ t('views.content.libraries.Quota.header.currentUsage') }}</h3>
    <div :class="['ui', {'success': progress < 60}, {'warning': progress >= 60 && progress < 96}, {'error': progress >= 95}, 'progress']">
      <div
        class="bar"
        :style="{width: `${progress}%`}"
      >
        <div class="progress">
          {{ t('views.content.libraries.Quota.label.percentUsed', {progress: humanSize(progress)}) }}
        </div>
      </div>
      <div
        v-if="quotaStatus"
        class="label"
      >
        {{ t('views.content.libraries.Quota.label.currentUsage', {max: humanSize(quotaStatus.max * 1000 * 1000), currentAmount: humanSize(quotaStatus.current * 1000 * 1000)}) }}
      </div>
    </div>
    <Layout
      v-if="quotaStatus"
      flex
    >
      <Alert
        v-if="quotaStatus.pending > 0"
        yellow
      >
        <div class="statistic">
          <div class="value">
            {{ humanSize(quotaStatus.pending * 1000 * 1000) }}
          </div>
          <div class="label">
            {{ t('views.content.libraries.Quota.label.pending') }}
          </div>
        </div>
        <Spacer />
        <Layout flex>
          <Link
            solid
            low-height
            :to="{name: 'profile.manageUploads', query: {query: compileTokens([{field: 'import_status', value: 'pending'}])}}"
          >
            {{ t('views.content.libraries.Quota.link.viewFiles') }}
          </Link>

          <dangerous-button
            low-height
            :action="purgePendingFiles"
            :title="t('views.content.libraries.Quota.modal.purgePending.header')"
          >
            {{ t('views.content.libraries.Quota.button.purge') }}
            <template #content>
              {{ t('views.content.libraries.Quota.modal.purgePending.content.description') }}
            </template>
            <template #confirm>
              {{ t('views.content.libraries.Quota.button.purge') }}
            </template>
          </dangerous-button>
        </Layout>
      </Alert>
      <Alert
        v-if="quotaStatus.skipped > 0"
        yellow
      >
        <div class="ui tiny statistic">
          <div class="value">
            {{ humanSize(quotaStatus.skipped * 1000 * 1000) }}
          </div>
          <div class="label">
            {{ t('views.content.libraries.Quota.label.skipped') }}
          </div>
        </div>
        <Spacer />
        <Layout flex>
          <Link
            solid
            low-height
            :to="{name: 'profile.manageUploads', query: {query: compileTokens([{field: 'import_status', value: 'skipped'}])}}"
          >
            {{ t('views.content.libraries.Quota.link.viewFiles') }}
          </Link>
          <dangerous-button
            low-height
            :action="purgeSkippedFiles"
            :title="t('views.content.libraries.Quota.modal.purgeSkipped.header')"
          >
            {{ t('views.content.libraries.Quota.button.purge') }}
            <template #content>
              {{ t('views.content.libraries.Quota.modal.purgeSkipped.content.description') }}
            </template>
            <template #confirm>
              {{ t('views.content.libraries.Quota.button.purge') }}
            </template>
          </dangerous-button>
        </Layout>
      </Alert>
      <Alert
        v-if="quotaStatus.errored > 0"
        red
      >
        <div class="ui tiny danger statistic">
          <div class="value">
            {{ humanSize(quotaStatus.errored * 1000 * 1000) }}
          </div>
          <div class="label">
            {{ t('views.content.libraries.Quota.label.errored') }}
          </div>
        </div>
        <Spacer />
        <Layout flex>
          <Link
            solid
            low-height
            :to="{name: 'profile.manageUploads', query: {query: compileTokens([{field: 'import_status', value: 'errored'}])}}"
          >
            {{ t('views.content.libraries.Quota.link.viewFiles') }}
          </Link>
          <dangerous-button
            low-height
            :action="purgeErroredFiles"
            :title="t('views.content.libraries.Quota.modal.purgeErrored.header')"
          >
            {{ t('views.content.libraries.Quota.button.purge') }}
            <template #content>
              {{ t('views.content.libraries.Quota.modal.purgeErrored.content.description') }}
            </template>
            <template #confirm>
              {{ t('views.content.libraries.Quota.button.purge') }}
            </template>
          </dangerous-button>
        </Layout>
      </Alert>
    </Layout>
  </Layout>
</template>

<style lang="scss" scoped>
.ui.progress {
    position: relative;
    display: -webkit-box;
    display: flex;
    width: 100%;
    height: 20px;
    border: none;
    margin: 1em 0 2.5em;
    box-shadow: none;
    background: rgba(0,0,0,.1);
    padding: 0;
    border-radius: .28571429rem
}

.ui.progress .bar {
    display: block;
    line-height: 1;
    position: relative;
    width: 0;
    min-width: 2em;
    background: #888;
    border-radius: .28571429rem;
    -webkit-transition: width .1s ease,background-color .1s ease;
    transition: width .1s ease,background-color .1s ease;
    overflow: hidden
}

.ui.progress .bar>.progress {
    white-space: nowrap;
    position: absolute;
    width: auto;
    font-size: .92857143em;
    top: 50%;
    right: .5em;
    left: auto;
    bottom: auto;
    color: var(--background-color);
    text-shadow: none;
    margin-top: -.5em;
    font-weight: 700;
    text-align: left
}

.ui.progress>.label {
    position: absolute;
    width: 100%;
    font-size: 1em;
    top: 100%;
    right: auto;
    left: 0;
    bottom: auto;
    font-weight: 700;
    text-shadow: none;
    margin-top: .2em;
    text-align: center;
    -webkit-transition: color .4s ease;
    transition: color .4s ease
}

.ui.progress.success .bar {
    background-color: var(--success-color)
}

.ui.progress.success .bar,.ui.progress.success .bar:after {
    -webkit-animation: none;
    animation: none
}

.ui.progress.warning .bar {
    background-color: var(--warning-color)
}

.ui.progress.warning .bar,.ui.progress.warning .bar:after {
    -webkit-animation: none;
    animation: none
}

.ui.progress.error .bar {
    background-color: var(--danger-color)
}

.ui.progress.error .bar,.ui.progress.error .bar:after {
    -webkit-animation: none;
    animation: none
}
</style>
