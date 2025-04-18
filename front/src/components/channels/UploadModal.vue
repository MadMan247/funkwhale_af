<script setup lang="ts">
import Modal from '~/components/ui/Modal.vue'
import ChannelUploadForm from '~/components/channels/UploadForm.vue'
import Popover from '~/components/ui/Popover.vue'
import PopoverItem from '~/components/ui/popover/PopoverItem.vue'
import Button from '~/components/ui/Button.vue'
import { humanSize } from '~/utils/filters'
import { useRouter } from 'vue-router'
import { useStore } from '~/store'
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const store = useStore()
const router = useRouter()
router.beforeEach(() => store.commit('channels/showUploadModal', { show: false }))

const update = (value: boolean) => store.commit('channels/showUploadModal', { show: value })

const { t } = useI18n()

const { filter } = defineProps<{ filter: 'podcast' | 'music' }>()

const uploadForm = ref()

const statusData = ref()
const statusInfo = computed(() => {
  if (!statusData.value) {
    return []
  }

  const info = []
  if (statusData.value.totalSize) {
    info.push(humanSize(statusData.value.totalSize))
  }

  if (statusData.value.totalFiles) {
    info.push(t('components.channels.UploadModal.meta.files', statusData.value.totalFiles))
  }

  if (statusData.value.progress) {
    info.push(`${statusData.value.progress}%`)
  }

  if (statusData.value.speed) {
    info.push(`${humanSize(statusData.value.speed)}/s`)
  }

  return info
})

const step = ref(1)
const isLoading = ref(false)

const open = ref(false)

const title = computed(() =>
  [t('components.channels.UploadModal.header'),
    t('components.channels.UploadModal.header.publish'),
    t('components.channels.UploadModal.header.uploadFiles'),
    t('components.channels.UploadModal.header.uploadDetails'),
    t('components.channels.UploadModal.header.processing')
  ][step.value]
)
</script>

<template>
  <Modal
    v-model="store.state.channels.showUploadModal"
    :title="title"
    class="small"
  >
    <div class="scrolling content">
      <channel-upload-form
        ref="uploadForm"
        :filter="filter"
        :channel="store.state.channels.uploadModalConfig.channel ?? null"
        @step="step = $event"
        @loading="isLoading = $event"
        @status="statusData = $event"
      />
    </div>
    <div class="actions">
      <div class="left floated text left align">
        <template v-if="statusData && step >= 2">
          {{ statusInfo.join(' · ') }}
        </template>
        <div class="ui very small hidden divider" />
        <template v-if="statusData && statusData.quotaStatus">
          {{ t('components.channels.UploadModal.meta.quota', humanSize((statusData.quotaStatus.remaining - statusData.uploadedSize) * 1000 * 1000)) }}
        </template>
      </div>
      <div class="ui hidden clearing divider mobile-only" />
      <Button
        v-if="step === 1"
        color="secondary"
        variant="outline"
        @click="update(false)"
      >
        {{ t('components.channels.UploadModal.button.cancel') }}
      </Button>
      <Button
        v-else-if="step < 3"
        color="secondary"
        variant="outline"
        @click.stop.prevent="uploadForm.step -= 1"
      >
        {{ t('components.channels.UploadModal.button.previous') }}
      </Button>
      <Button
        v-else-if="step === 3"
        color="secondary"
        @click.stop.prevent="uploadForm.step -= 1"
      >
        {{ t('components.channels.UploadModal.button.update') }}
      </Button>
      <Button
        v-if="step === 1"
        color="secondary"
        @click.stop.prevent="uploadForm.step += 1"
      >
        {{ t('components.channels.UploadModal.button.next') }}
      </Button>
      <div class="ui primary buttons">
        <Button
          :is-loading="isLoading"
          type="submit"
          :disabled="!statusData?.canSubmit"
          @click.prevent.stop="uploadForm.publish"
        >
          {{ t('components.channels.UploadModal.button.publish') }}
        </Button>

        <Popover v-model="open">
          <template #default="{ toggleOpen }">
            <Button
              color="primary"
              icon="bi-chevron-down"
              :disabled="!statusData?.canSubmit"
              @click.stop="toggleOpen()"
            />
          </template>
          <template #items>
            <PopoverItem @click="update(false)">
              {{ t('components.channels.UploadModal.button.finishLater') }}
            </PopoverItem>
          </template>
        </Popover>
      </div>

      <Button
        v-if="step === 4"
        color="secondary"
        @click="update(false)"
      >
        {{ t('components.channels.UploadModal.button.close') }}
      </Button>
    </div>
  </Modal>
</template>
