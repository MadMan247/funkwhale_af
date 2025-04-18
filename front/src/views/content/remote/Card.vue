<script setup lang="ts">
import type { Library } from '~/types'

import { useTimeoutFn } from '@vueuse/core'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'

import axios from 'axios'

import DangerousButton from '~/components/common/DangerousButton.vue'
import RadioButton from '~/components/radios/Button.vue'
import Card from '~/components/ui/Card.vue'
import OptionsButton from '~/components/ui/button/Options.vue'
import Popover from '~/components/ui/Popover.vue'
import PopoverItem from '~/components/ui/popover/PopoverItem.vue'
import Spacer from '~/components/ui/Spacer.vue'

import useErrorHandler from '~/composables/useErrorHandler'
import useReport from '~/composables/moderation/useReport'
import useLogger from '~/composables/useLogger'

interface Emits {
  (e: 'followed'): void
}

interface Props {
  initialLibrary: Library
  displayFollow?: boolean
  displayScan?: boolean
  displayCopyFid?: boolean
}

const emit = defineEmits<Emits>()
const props = withDefaults(defineProps<Props>(), {
  displayFollow: true,
  displayScan: true,
  displayCopyFid: true
})

const logger = useLogger()

const { report, getReportableObjects } = useReport()
const store = useStore()

const library = ref(props.initialLibrary)
const isLoadingFollow = ref(false)
const showScan = ref(false)
const latestScan = ref(props.initialLibrary.latest_scan)

const scanProgress = computed(() => latestScan.value && latestScan.value.processed_files && latestScan.value.total_files
  ? Math.min(latestScan.value.processed_files * 100 / latestScan.value.total_files, 100)
  : 0)
const scanStatus = computed(() => latestScan.value?.status ?? 'unknown')
const canLaunchScan = computed(() => scanStatus.value !== 'pending' && scanStatus.value !== 'scanning')
const radioPlayable = computed(() => (
  (library.value.actor.is_local || scanStatus.value === 'finished')
  && (library.value.privacy_level === 'everyone' || library.value.follow?.approved)
))

const { t } = useI18n()
const labels = computed(() => ({
  tooltips: {
    me: t('views.content.remote.Card.tooltip.private'),
    everyone: t('views.content.remote.Card.tooltip.public')
  }
}))

const launchScan = async () => {
  try {
    const response = await axios.post(`federation/libraries/${library.value.uuid}/scan/`)
    if (response.data.status !== 'skipped') {
      latestScan.value = response.data.scan
    }

    store.commit('ui/addMessage', {
      date: new Date(),
      content: response.data.status === 'skipped'
        ? t('views.content.remote.Card.message.scanSkipped')
        : t('views.content.remote.Card.message.scanLaunched')
    })
  } catch (error) {
    useErrorHandler(error as Error)
  }
}

const follow = async () => {
  isLoadingFollow.value = true
  try {
    const response = await axios.post('federation/follows/library/', { target: library.value.uuid })
    library.value.follow = response.data
    emit('followed')
  } catch (error) {
    logger.error(error)
    store.commit('ui/addMessage', {
      content: t('views.content.remote.Card.error.follow', { error }),
      date: new Date()
    })
  }

  isLoadingFollow.value = false
}

const unfollow = async () => {
  isLoadingFollow.value = true
  try {
    if (library.value.follow) {
      await axios.delete(`federation/follows/library/${library.value.follow.uuid}/`)
      library.value.follow = undefined
    }
  } catch (error) {
    store.commit('ui/addMessage', {
      content: t('views.content.remote.Card.error.unfollow', { error }),
      date: new Date()
    })
  }

  isLoadingFollow.value = false
}

const fetchScanStatus = async () => {
  try {
    if (!library.value.follow) {
      return
    }

    const response = await axios.get(`federation/follows/library/${library.value.follow.uuid}/`)
    latestScan.value = response.data.target.latest_scan

    if (scanStatus.value === 'pending' || scanStatus.value === 'scanning') {
      startFetching()
    } else {
      stopFetching()
    }
  } catch (error) {
    useErrorHandler(error as Error)
  }
}

const { start: startFetching, stop: stopFetching } = useTimeoutFn(fetchScanStatus, 5000, { immediate: false })

watch(showScan, (shouldShow) => {
  if (shouldShow) {
    if (scanStatus.value === 'pending' || scanStatus.value === 'scanning') {
      fetchScanStatus()
    }

    return
  }

  stopFetching()
})

const isOpen = ref(false)
</script>

<template>
  <Card
    :title="library.name"
    :to="{name: 'library.detail', params: {id: library.uuid}}"
    small
  >
    <template #topright>
      <span
        v-if="library.privacy_level === 'me'"
        :data-tooltip="labels.tooltips.me"
      >
        <i class="bi bi-lock-fill" />
      </span>
      <span
        v-else-if="library.privacy_level === 'everyone'"
        :data-tooltip="labels.tooltips.everyone"
      >
        <i class="bi bi-globe" />
      </span>
      <Popover v-model="isOpen">
        <template #default="{ toggleOpen }">
          <OptionsButton
            ghost
            @click="toggleOpen"
          />
        </template>
        <template #items>
          <PopoverItem
            v-for="obj in getReportableObjects({library, account: library.actor})"
            :key="obj.target.type + obj.target.id"
            @click.stop.prevent="report(obj)"
          >
            <i class="bi bi-share" /> {{ obj.label }}
          </PopoverItem>
        </template>
      </Popover>
    </template>

    <div class="content">
      <!-- TODO: Add `description` field to `Library` -->
      <!-- @vue-ignore -->
      <div class="description">
        {{
          // @ts-ignore
          library.description
        }}
      </div>
      <Spacer :size="8" />
      <div
        v-if="displayScan && latestScan"
        class="meta"
      >
        <template v-if="latestScan.status === 'pending'">
          <i class="bi bi-hourglass" />
          {{ t('views.content.remote.Card.label.scanPending') }}
        </template>
        <template v-if="latestScan.status === 'scanning'">
          <i class="loading spinner icon" />
          {{ t('views.content.remote.Card.label.scanProgress', {progress: scanProgress}) }}
        </template>
        <template v-else-if="latestScan.status === 'errored'">
          <i class="bi bi-exclamation-triangle" />
          {{ t('views.content.remote.Card.label.scanFailure') }}
        </template>
        <template v-else-if="latestScan.status === 'finished' && latestScan.errored_files === 0">
          <i class="bi bi-check-circle" />
          {{ t('views.content.remote.Card.label.scanSuccess') }}
        </template>
        <template v-else-if="latestScan.status === 'finished' && latestScan.errored_files && latestScan.errored_files > 0">
          <i class="bi bi-exclamation-circle" />
          {{ t('views.content.remote.Card.label.scanPartialSuccess') }}
        </template>
        <a
          href=""
          class="link right floated"
          @click.prevent="showScan = !showScan"
        >
          {{ t('views.content.remote.Card.link.scanDetails') }}
          <i
            v-if="showScan"
            class="bi bi-chevron-down"
          />
          <i
            v-else
            class="bi bi-chevron-right"
          />
        </a>
        <div v-if="showScan">
          <template v-if="latestScan.modification_date">
            {{ t('views.content.remote.Card.meta.lastUpdate') }}<human-date :date="latestScan.modification_date" /><br>
          </template>
          {{ t('views.content.remote.Card.meta.failedTracks', {tracks: latestScan.errored_files}) }}
        </div>
      </div>
      <div
        v-if="displayScan && canLaunchScan"
        class="clearfix"
      >
        <a
          href=""
          class="right floated link"
          @click.prevent="launchScan"
        >
          {{ t('views.content.remote.Card.link.scan') }}
          <i class="bi bi-send" />
        </a>
      </div>
    </div>
    <Spacer :size="8" />
    <div class="extra content">
      <actor-link
        :actor="library.actor"
      />
    </div>
    <Spacer :size="8" />
    <div
      v-if="displayCopyFid"
      class="extra content"
    >
      <div class="ui form">
        <div class="field">
          <Spacer />
          <copy-input
            :id="library.fid"
            :button-classes="'basic'"
            :value="library.fid"
            :label="t('views.content.remote.Card.label.sharingLink')"
          />
        </div>
      </div>
    </div>
    <template #footer>
      <span>
        <human-date :date="library.creation_date" />
      </span>
      <i class="bi bi-dot" />
      <span>
        {{ t('views.content.remote.Card.meta.tracks', library.uploads_count) }}
      </span>
    </template>

    <template #actions>
      <div
        v-if="displayFollow || radioPlayable"
        :class="['ui', {two: displayFollow && radioPlayable}, 'bottom', 'attached', 'buttons']"
      >
        <radio-button
          v-if="radioPlayable"
          :type="'library'"
          :object-id="library.uuid"
        />
        <template v-if="displayFollow">
          <button
            v-if="!library.follow"
            :class="['ui', 'success', {'loading': isLoadingFollow}, 'button']"
            @click="follow()"
          >
            {{ t('views.content.remote.Card.button.follow') }}
          </button>
          <template v-else-if="!library.follow.approved">
            <button
              class="ui disabled button"
            >
              <i class="hourglass icon" />
              {{ t('views.content.remote.Card.button.pending') }}
            </button>
            <button
              class="ui button"
              @click="unfollow"
            >
              {{ t('views.content.remote.Card.button.cancel') }}
            </button>
          </template>
          <template v-else-if="library.follow.approved">
            <dangerous-button
              :action="unfollow"
              :title="t('views.content.remote.Card.modal.unfollow.header')"
            >
              {{ t('views.content.remote.Card.button.unfollow') }}
              <template #modal-content>
                {{ t('views.content.remote.Card.modal.unfollow.content.warning') }}
              </template>
              <template #modal-confirm>
                {{ t('views.content.remote.Card.button.unfollow') }}
              </template>
            </dangerous-button>
          </template>
        </template>
      </div>
    </template>
  </Card>
</template>
