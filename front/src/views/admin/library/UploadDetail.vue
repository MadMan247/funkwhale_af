<script setup lang="ts">
import type { PrivacyLevel, ImportStatus } from '~/types'

import { humanSize, truncate } from '~/utils/filters'
import { useRouter } from 'vue-router'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'

import time from '~/utils/time'
import axios from 'axios'

import ImportStatusModal from '~/components/library/ImportStatusModal.vue'
import DangerousButton from '~/components/common/DangerousButton.vue'
import Header from '~/components/ui/Header.vue'
import Layout from '~/components/ui/Layout.vue'
import Spacer from '~/components/ui/Spacer.vue'
import HumanDate from '~/components/common/HumanDate.vue'
import Link from '~/components/ui/Link.vue'
import Button from '~/components/ui/Button.vue'
import Heading from '~/components/ui/Heading.vue'
import OptionsButton from '~/components/ui/button/Options.vue'
import Popover from '~/components/ui/Popover.vue'
import PopoverItem from '~/components/ui/popover/PopoverItem.vue'
import Loader from '~/components/ui/Loader.vue'
import Pill from '~/components/ui/Pill.vue'

import useSharedLabels from '~/composables/locale/useSharedLabels'
import useErrorHandler from '~/composables/useErrorHandler'

interface Props {
  id: number
}

const props = defineProps<Props>()

const router = useRouter()
const store = useStore()
const { t } = useI18n()

const sharedLabels = useSharedLabels()

const isLoading = ref(false)
const object = ref()
const showUploadDetailModal = ref(false)
const open = ref(false)

const privacyLevels = computed(() =>
  sharedLabels.fields.privacy_level.shortChoices[object.value?.library?.privacy_level as PrivacyLevel]
)
const importStatus = computed(() =>
  sharedLabels.fields.import_status.choices[object.value?.import_status as ImportStatus]?.label
)

const fetchData = async () => {
  isLoading.value = true

  try {
    const response = await axios.get(`manage/library/uploads/${props.id}/`)
    object.value = response.data
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

fetchData()

const remove = async () => {
  isLoading.value = true

  try {
    await axios.delete(`manage/uploads/${props.id}/`)
    router.push({ name: 'manage.library.uploads' })
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

const getQuery = (field: string, value: string) => `${field}:"${value}"`
const displayName = (object: any) => object?.filename ?? object?.source ?? object?.uuid
</script>

<template>
  <Loader v-if="isLoading" />
  <Header
    v-if="object"
    v-title="displayName(object)"
    :h1="truncate(displayName(object))"
    page-heading
  >
    <template #image>
      <i class="avatar circular bi bi-file-earmark-music" />
    </template>
    <div class="sub header">
      <template v-if="object?.is_local">
        <Pill>
          <i class="bi bi-house-fill" />
          {{ t('views.admin.library.UploadDetail.header.local') }}
        </Pill>
      </template>
      <template v-else>
        <Pill>
          <i class="bi bi-box-arrow-up-right" />
          {{ t('views.admin.library.UploadDetail.header.federated') }}
        </Pill>
      </template>
    </div>

    <Layout
      flex
      class="header-buttons"
    >
      <Link
        v-if="store.state.auth.profile?.is_superuser"
        solid
        primary
        :to="store.getters['instance/absoluteUrl'](`/api/admin/music/upload/${object?.id}`)"
        target="_blank"
        rel="noopener noreferrer"
      >
        <i class="bi bi-wrench" />
        {{ t('views.admin.library.UploadDetail.link.django') }}
      </Link>
      <Link
        v-if="object?.audio_file"
        solid
        primary
        :to="store.getters['instance/absoluteUrl'](object?.audio_file)"
        target="_blank"
        rel="noopener noreferrer"
      >
        <i class="bi bi-download" />
        {{ t('views.admin.library.UploadDetail.button.download') }}
      </Link>
      <dangerous-button
        :is-loading="isLoading"
        :action="remove"
        :title="t('views.admin.library.UploadDetail.modal.delete.header')"
      >
        {{ t('views.admin.library.UploadDetail.button.delete') }}
        <template #modal-content>
          {{ t('views.admin.library.UploadDetail.modal.delete.content.warning') }}
        </template>
        <template #modal-confirm>
          {{ t('views.admin.library.UploadDetail.button.delete') }}
        </template>
      </dangerous-button>
      <Spacer grow />
      <Popover v-model="open">
        <template #default="{ toggleOpen }">
          <OptionsButton
            :title="t('views.admin.library.UploadDetail.button.more')"
            is-square-small
            @click="toggleOpen()"
          />
        </template>

        <template #items>
          <PopoverItem
            v-if="store.state.auth.profile?.is_superuser"
            :to="store.getters['instance/absoluteUrl'](`/api/admin/music/upload/${object?.id}`)"
            icon="bi-wrench"
            target="_blank"
          >
            {{ t('views.admin.library.UploadDetail.link.django') }}
          </PopoverItem>
          <PopoverItem
            :to="object?.url || object?.fid"
            icon="bi-box-arrow-up-right"
            target="_blank"
          >
            {{ t('views.admin.library.UploadDetail.link.remoteProfile') }}
          </PopoverItem>
        </template>
      </Popover>
    </Layout>
  </Header>

  <Layout
    flex
    gap-64
  >
    <Layout
      stack
      style="flex: 1; gap: 0;"
    >
      <Heading
        :h3="t('views.admin.library.UploadDetail.header.uploadData')"
        class="category"
      />
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.library.UploadDetail.table.upload.name') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ displayName(object) }}</span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <Link
          class="label"
          :to="{ name: 'manage.library.uploads', query: { q: getQuery('privacy_level', object?.library?.privacy_level) } }"
        >
          {{ t('views.admin.library.UploadDetail.link.visibility') }}
        </Link>
        <Spacer
          h
          grow
        />
        <span class="value">{{ privacyLevels }}</span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <Link
          class="label"
          :to="{ name: 'manage.moderation.accounts.detail', params: { id: object?.library?.actor?.full_username } }"
        >
          {{ t('views.admin.library.UploadDetail.link.account') }}
        </Link>
        <Spacer
          h
          grow
        />
        <span class="value">{{ object?.library?.actor?.preferred_username }}</span>
      </Layout>
      <Layout
        v-if="!object?.is_local"
        flex
        class="details"
      >
        <Link
          class="label"
          :to="{ name: 'manage.moderation.domains.detail', params: { id: object?.domain } }"
        >
          {{ t('views.admin.library.UploadDetail.link.domain') }}
        </Link>
        <Spacer
          h
          grow
        />
        <span class="value">{{ object?.domain }}</span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <Link
          class="label"
          :to="{ name: 'manage.library.uploads', query: { q: getQuery('status', object?.import_status) } }"
        >
          {{ t('views.admin.library.UploadDetail.link.importStatus') }}
        </Link>
        <Spacer
          h
          grow
        />
        <span class="value">
          {{ importStatus }}
          <Button
            :title="sharedLabels.fields.import_status.label"
            icon="bi-question-circle"
            @click="showUploadDetailModal = true"
          />
        </span>
      </Layout>
    </Layout>
    <Layout
      stack
      style="flex: 1; gap: 0;"
    >
      <Heading
        :h3="t('views.admin.library.UploadDetail.header.activity')"
        class="category"
      />
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.library.UploadDetail.table.activity.firstSeen') }}
        </span>
        <Spacer
          h
          grow
        />
        <human-date :date="object?.creation_date" />
      </Layout>
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.library.UploadDetail.table.activity.accessedDate') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">
          <human-date
            v-if="object?.accessed_date"
            :date="object?.accessed_date"
          />
          <span v-else>
            {{ t('views.admin.library.UploadDetail.notApplicable') }}
          </span>
        </span>
      </Layout>
    </Layout>
    <Layout
      stack
      style="flex: 1; gap: 0;"
    >
      <Heading
        :h3="t('views.admin.library.UploadDetail.header.audioContent')"
        class="category"
      />
      <Layout
        v-if="object?.track"
        flex
        class="details"
      >
        <Link
          class="label"
          :to="{ name: 'manage.library.tracks.detail', params: { id: object?.track?.id } }"
        >
          {{ t('views.admin.library.UploadDetail.table.audioContent.track') }}
        </Link>
        <Spacer
          h
          grow
        />
        <span class="value">{{ object?.track?.title }}</span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.library.UploadDetail.table.audioContent.cachedSize') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">
          <template v-if="object?.audio_file">
            {{ humanSize(object?.size) }}
          </template>
          <span v-else>
            {{ t('views.admin.library.UploadDetail.notApplicable') }}
          </span>
        </span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.library.UploadDetail.table.audioContent.size') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ humanSize(object?.size) }}</span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.library.UploadDetail.table.audioContent.bitrate.label') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">
          <template v-if="object?.bitrate">
            {{ t('views.admin.library.UploadDetail.table.audioContent.bitrate.value', { bitrate: humanSize(object?.bitrate) }) }}
          </template>
          <span v-else>
            {{ t('views.admin.library.UploadDetail.notApplicable') }}
          </span>
        </span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.library.UploadDetail.table.audioContent.duration') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">
          <template v-if="object?.duration">
            {{ time.parse(object?.duration) }}
          </template>
          <span v-else>
            {{ t('views.admin.library.UploadDetail.notApplicable') }}
          </span>
        </span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <Link
          class="label"
          :to="{ name: 'manage.library.uploads', query: { q: getQuery('type', object?.mimetype) } }"
        >
          {{ t('views.admin.library.UploadDetail.link.type') }}
        </Link>
        <Spacer
          h
          grow
        />
        <span class="value">
          <template v-if="object?.mimetype">
            {{ object?.mimetype }}
          </template>
          <span v-else>
            {{ t('views.admin.library.UploadDetail.notApplicable') }}
          </span>
        </span>
      </Layout>
    </Layout>
  </Layout>
  <import-status-modal
    v-model:show="showUploadDetailModal"
    :upload="object"
  />
</template>

<style scoped lang="scss">
  .avatar {
    font-size: 64px;
  }

  h3.category {
    margin-bottom: 16px;
  }

  .details {
    padding: 0 16px;
    height: 72px;
    align-items: center;
    border-top: 1px solid;
    min-width: 280px;

    @include light-theme {
      border-color: var(--fw-gray-300);
    }
    @include dark-theme {
      border-color: var(--fw-gray-800);
    }

    .label {
      font-weight: 800;

      @include light-theme {
        color: var(--fw-gray-600);
      }

      @include dark-theme {
        color: var(--fw-gray-500);
      }
    }

    a.label,
    a.value {
      text-decoration: underline;
    }

    &:last-child {
      border-bottom: 1px solid;
    }
  }
</style>
