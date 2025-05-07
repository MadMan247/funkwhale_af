<script setup lang="ts">
import type { InstancePolicy } from '~/types'

import { computed, ref, reactive } from 'vue'
import { humanSize } from '~/utils/filters'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'

import axios from 'axios'

import Header from '~/components/ui/Header.vue'
import Layout from '~/components/ui/Layout.vue'
import Spacer from '~/components/ui/Spacer.vue'
import HumanDate from '~/components/common/HumanDate.vue'
import Link from '~/components/ui/Link.vue'
import Button from '~/components/ui/Button.vue'
import Heading from '~/components/ui/Heading.vue'
import Loader from '~/components/ui/Loader.vue'
import Alert from '~/components/ui/Alert.vue'
import Input from '~/components/ui/Input.vue'

import InstancePolicyForm from '~/components/manage/moderation/InstancePolicyForm.vue'
import InstancePolicyCard from '~/components/manage/moderation/InstancePolicyCard.vue'

import useErrorHandler from '~/composables/useErrorHandler'
import useLogger from '~/composables/useLogger'

interface Props {
  id: number
}

const props = defineProps<Props>()

const store = useStore()
const { t } = useI18n()

const logger = useLogger()

const labels = computed(() => ({
  statsWarning: t('views.admin.moderation.AccountsDetail.warning.stats'),
  uploadQuota: t('views.admin.moderation.AccountsDetail.tooltip.uploadQuota')
}))

const allPermissions = computed(() => [
  { code: 'library', label: t('views.admin.moderation.AccountsDetail.option.permission.library') },
  { code: 'moderation', label: t('views.admin.moderation.AccountsDetail.option.permission.moderation') },
  { code: 'settings', label: t('views.admin.moderation.AccountsDetail.option.permission.settings') }
])

const isLoadingPolicy = ref(false)
const policy = ref()
const fetchPolicy = async (id: number) => {
  isLoadingPolicy.value = true

  try {
    const response = await axios.get(`manage/moderation/instance-policies/${id}/`)
    policy.value = response.data
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoadingPolicy.value = false
}

const permissions = ref([] as string[])
const isLoading = ref(false)
const object = ref()
const fetchData = async () => {
  isLoading.value = true

  try {
    const response = await axios.get(`manage/accounts/${props.id}/`)
    object.value = response.data

    if (response.data.instance_policy) {
      fetchPolicy(response.data.instance_policy)
    }

    if (response.data.user) {
      for (const { code } of allPermissions.value) {
        if (response.data.user.permissions[code]) {
          permissions.value.push(code)
        }
      }
    }
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

const isLoadingStats = ref(false)
const stats = ref()
const fetchStats = async () => {
  isLoadingStats.value = true

  try {
    const response = await axios.get(`manage/accounts/${props.id}/stats/`)
    stats.value = response.data
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoadingStats.value = false
}

fetchStats()
fetchData()

const getQuery = (field: string, value: string) => `${field}:"${value}"`

const updating = reactive(new Set<string>())
const updateUser = async (attr: string, toNull = false) => {
  let newValue = object.value.user[attr]
  if (toNull && !newValue) {
    newValue = null
  }

  updating.add(attr)

  const params = {
    [attr]: newValue
  }

  if (attr === 'permissions') {
    params.permissions = allPermissions.value.reduce((acc, { code }) => {
      acc[code] = permissions.value.includes(code)
      return acc
    }, {} as Record<string, boolean>)
  }

  try {
    await axios.patch(`manage/users/users/${object.value.user.id}/`, params)
    logger.info(`${attr} was updated successfully to ${newValue}`)
  } catch (error) {
    logger.error(`Error while setting ${attr} to ${newValue}`, error)
    // TODO: Use error handler
  }

  updating.delete(attr)
}

const showPolicyForm = ref(false)
const updatePolicy = (newPolicy: InstancePolicy) => {
  policy.value = newPolicy
  showPolicyForm.value = false
}
</script>

<template>
  <Loader v-if="isLoading" />
  <Header
    v-if="object"
    v-title="object?.full_username"
    :h1="object?.full_username"
    page-heading
  >
    <template #image>
      <i class="channel-image bi-person-circle" />
    </template>
    <Spacer />
    <Layout
      flex
      class="header-buttons"
    >
      <Link
        solid
        primary
        low-height
        icon="bi-box-arrow-up-right"
        :to="object?.url || object?.fid"
        target="_blank"
      >
        {{ t('views.admin.moderation.AccountsDetail.link.openProfile') }}
      </Link>
      <Link
        v-if="object?.user && store.state.auth.profile?.is_superuser"
        solid
        primary
        low-height
        icon="bi-wrench"
        :to="store.getters['instance/absoluteUrl'](`/api/admin/users/user/${object?.user?.id}`)"
        target="_blank"
      >
        {{ t('views.admin.moderation.AccountsDetail.link.django') }}
      </Link>
      <Link
        v-if="!object?.user"
        solid
        primary
        low-height
        :to="store.getters['instance/absoluteUrl'](`/api/admin/federation/actor/${object?.id}`)"
        icon="bi-wrench"
        target="_blank"
      >
        {{ t('views.admin.moderation.AccountsDetail.link.django') }}
      </Link>
    </Layout>
  </Header>

  <Alert
    v-if="!object?.user"
    :blue="!policy"
    red="policy"
  >
    <template v-if="isLoadingPolicy">
      <div class="paragraph">
        <div class="line" />
        <div class="line" />
        <div class="line" />
        <div class="line" />
        <div class="line" />
      </div>
    </template>
    <template v-else-if="!policy && !showPolicyForm">
      <Heading
        :h3="t('views.admin.moderation.AccountsDetail.header.noPolicy')"
        icon="bi-shield-fill"
      />
      <p>
        {{ t('views.admin.moderation.AccountsDetail.description.policy') }}
      </p>
      <Button
        primary
        @click="showPolicyForm = true"
      >
        {{ t('views.admin.moderation.AccountsDetail.button.addPolicy') }}
      </Button>
    </template>
    <instance-policy-card
      v-else-if="policy && !showPolicyForm"
      :object="policy"
      @update="showPolicyForm = true"
    >
      <header class="ui header">
        <h3>
          {{ t('views.admin.moderation.AccountsDetail.header.activePolicy') }}
        </h3>
      </header>
    </instance-policy-card>
    <instance-policy-form
      v-else-if="showPolicyForm"
      :object="policy"
      type="actor"
      :target="object?.full_username"
      @cancel="showPolicyForm = false"
      @save="updatePolicy"
      @delete="policy = null; showPolicyForm = false"
    />
  </Alert>

  <Spacer />
  <Layout
    flex
    gap-64
  >
    <Layout
      stack
      style="flex: 1; gap: 0;"
    >
      <Heading
        :h3="t('views.admin.moderation.AccountsDetail.header.accountData')"
        class="category"
      />
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.moderation.AccountsDetail.table.accountData.username') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ object?.preferred_username }}</span>
      </Layout>
      <Layout
        v-if="!object?.user"
        flex
        class="details"
      >
        <router-link
          class="label"
          :to="{ name: 'manage.moderation.domains.detail', params: { id: object?.domain } }"
        >
          {{ t('views.admin.moderation.AccountsDetail.link.domain') }}
        </router-link>
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
        <span class="label">
          {{ t('views.admin.moderation.AccountsDetail.table.accountData.displayName') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ object?.name }}</span>
      </Layout>
      <Layout
        v-if="object?.user"
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.moderation.AccountsDetail.table.accountData.email') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ object?.user?.email }}</span>
      </Layout>
      <Layout
        v-if="object?.user"
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.moderation.AccountsDetail.table.accountData.signupDate') }}
        </span>
        <Spacer
          h
          grow
        />
        <HumanDate :date="object?.user?.date_joined" />
      </Layout>
    </Layout>

    <Layout
      stack
      style="flex: 1; gap: 0;"
    >
      <Heading
        :h3="t('views.admin.moderation.AccountsDetail.header.activity')"
        class="category"
      >
        <span
          :data-tooltip="labels.statsWarning"
          style="margin-left: 8px"
        >
          <i class=" bi bi-question-circle-fill" /></span>
      </Heading>
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.moderation.AccountsDetail.table.activity.firstSeen') }}
        </span>
        <Spacer
          h
          grow
        />
        <HumanDate :date="object?.creation_date" />
      </Layout>
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.moderation.AccountsDetail.table.activity.emittedMessages') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ stats?.outbox_activities }}</span>
      </Layout>
      <Layout
        v-if="object?.user"
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.moderation.AccountsDetail.table.activity.receivedFollows') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ stats?.received_library_follows }}</span>
      </Layout>
      <Layout
        v-if="object?.user"
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.moderation.AccountsDetail.table.activity.emittedFollows') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ stats?.emitted_library_follows }}</span>
      </Layout>
      <Layout
        v-if="object?.user"
        flex
        class="details"
      >
        <router-link :to="{name: 'manage.moderation.reports.list', query: {q: getQuery('target', `account:${object?.full_username}`) }}">
          {{ t('views.admin.moderation.AccountsDetail.link.linkedReports') }}
        </router-link>
        <Spacer
          h
          grow
        />
        <span class="value">{{ stats?.reports }}</span>
      </Layout>
      <Layout
        v-if="object?.user"
        flex
        class="details"
      >
        <router-link :to="{name: 'manage.moderation.requests.list', query: {q: getQuery('submitter', `${object?.full_username}`) }}">
          {{ t('views.admin.moderation.AccountsDetail.link.requests') }}
        </router-link>
        <Spacer
          h
          grow
        />
        <span class="value">{{ stats?.requests }}</span>
      </Layout>
    </Layout>

    <Layout
      stack
      style="flex: 1; gap: 0;"
    >
      <Heading
        :h3="t('views.admin.moderation.AccountsDetail.header.audioContent')"
        class="category"
      >
        <span
          :data-tooltip="labels.statsWarning"
          style="margin-left: 8px"
        >
          <i class=" bi bi-question-circle-fill" /></span>
      </Heading>
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.moderation.AccountsDetail.table.audioContent.cachedSize') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ humanSize(stats?.media_downloaded_size) }}</span>
      </Layout>
      <Layout
        v-if="object?.user"
        flex
        no-gap
        class="details"
      >
        <span class="label">
          {{ t('views.admin.moderation.AccountsDetail.table.audioContent.uploadQuota') }}
        </span>
        <span
          :data-tooltip="labels.uploadQuota"
          style="margin-left: 8px"
        >
          <i class="bi bi-question-circle" />
        </span>
        <Spacer
          h
          grow
        />
        <Input
          v-model.number="object.user.upload_quota"
          step="100"
          name="quota"
          type="number"
          style="width: 100px"
          @change="updateUser('upload_quota', true)"
        />
        <span class="ui basic label">
          {{ t('views.admin.moderation.AccountsDetail.table.audioContent.megabyte') }}
        </span>
        <action-feedback
          class="ui basic label"
          size="tiny"
          :is-loading="updating.has('upload_quota')"
        />
      </Layout>
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.moderation.AccountsDetail.table.audioContent.totalSize') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ humanSize(stats?.media_total_size) }}</span>
      </Layout>
    </Layout>
  </Layout>
</template>

<style scoped lang="scss">

.channel-image {
  width: 200px;
  height: 200px;
  font-size: 160px;
  border: none;
  display: block;
  text-align: center;
  align-content: center;
  border-radius: 50%;
  @include light-theme {
    background-color: var(--fw-gray-200);
  }
  @include dark-theme {
    background-color: var(--fw-gray-800);
  }
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
