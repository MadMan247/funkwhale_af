<script setup lang="ts">
import type { InstancePolicy } from '~/types'

import { humanSize } from '~/utils/filters'
import { useI18n } from 'vue-i18n'
import { computed, ref } from 'vue'
import { get } from 'lodash-es'
import { useStore } from '~/store'

import axios from 'axios'

import InstancePolicyForm from '~/components/manage/moderation/InstancePolicyForm.vue'
import InstancePolicyCard from '~/components/manage/moderation/InstancePolicyCard.vue'

import useErrorHandler from '~/composables/useErrorHandler'

import Header from '~/components/ui/Header.vue'
import Layout from '~/components/ui/Layout.vue'
import Spacer from '~/components/ui/Spacer.vue'
import HumanDate from '~/components/common/HumanDate.vue'
import Link from '~/components/ui/Link.vue'
import Button from '~/components/ui/Button.vue'
import Heading from '~/components/ui/Heading.vue'
import Loader from '~/components/ui/Loader.vue'
import Alert from '~/components/ui/Alert.vue'
import OptionsButton from '~/components/ui/button/Options.vue'
import Popover from '~/components/ui/Popover.vue'
import PopoverItem from '~/components/ui/popover/PopoverItem.vue'

interface Props {
  id: number
  allowListEnabled: boolean
}

const props = defineProps<Props>()

const store = useStore()
const { t } = useI18n()

const labels = computed(() => ({
  statsWarning: t('views.admin.moderation.DomainsDetail.warning.stats')
}))

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

const isLoading = ref(false)
const object = ref()
const externalUrl = computed(() => `https://${object.value?.name}`)
const fetchData = async () => {
  isLoading.value = true

  try {
    const response = await axios.get(`manage/federation/domains/${props.id}/`)
    object.value = response.data
    if (response.data.instance_policy) {
      fetchPolicy(response.data.instance_policy)
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
    const response = await axios.get(`manage/federation/domains/${props.id}/stats/`)
    stats.value = response.data
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoadingStats.value = false
}

fetchStats()
fetchData()

const refreshNodeInfo = (data: any) => {
  object.value.nodeinfo = data
  object.value.nodeinfo_fetch_date = new Date()
}

const getQuery = (field: string, value: string) => `${field}:"${value}"`

const showPolicyForm = ref(false)
const updatePolicy = (newPolicy: InstancePolicy) => {
  policy.value = newPolicy
  showPolicyForm.value = false
}

const isLoadingAllowList = ref(false)
const setAllowList = async (value: boolean) => {
  isLoadingAllowList.value = true

  try {
    const response = await axios.patch(`manage/federation/domains/${props.id}/`, { allowed: value })
    object.value = response.data
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoadingAllowList.value = false
}
</script>

<template>
  <Loader v-if="isLoading" />
  <Header
    v-if="object"
    v-title="object?.name"
    :h1="object?.name"
    page-heading
  >
    <template #image>
      <i class="channel-image bi bi-cloud-fill" />
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
        :to="externalUrl"
        target="_blank"
      >
        {{ t('views.admin.moderation.DomainsDetail.link.website') }}
      </Link>
      <Link
        v-if="store.state.auth.profile?.is_superuser"
        solid
        primary
        low-height
        icon="bi-wrench"
        :to="store.getters['instance/absoluteUrl'](`/api/admin/federation/domain/${object.name}`)"
        target="_blank"
      >
        {{ t('views.admin.moderation.DomainsDetail.link.django') }}
      </Link>
      <Spacer grow />
      <Popover v-if="allowListEnabled">
        <template #default="{ toggleOpen }">
          <OptionsButton
            is-square-small
            @click="toggleOpen()"
          />
        </template>
        <template #items>
          <PopoverItem
            icon="bi-list-check"
            @click="setAllowList(!object.allowed)"
          >
            <span v-if="object.allowed">
              {{ t('views.admin.moderation.DomainsDetail.button.removeFromAllowList') }}
            </span>
            <span v-else>
              {{ t('views.admin.moderation.DomainsDetail.button.addToAllowList') }}
            </span>
          </PopoverItem>
        </template>
      </Popover>
    </Layout>
  </Header>

  <Alert blue>
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
        :h3="t('views.admin.moderation.DomainsDetail.header.noPolicy')"
        icon="bi-shield-lock"
      />
      <p>
        {{ t('views.admin.moderation.DomainsDetail.description.policy') }}
      </p>
      <Button
        primary
        @click="showPolicyForm = true"
      >
        {{ t('views.admin.moderation.DomainsDetail.button.addPolicy') }}
      </Button>
    </template>
    <instance-policy-card
      v-else-if="policy && !showPolicyForm"
      :object="policy"
      @update="showPolicyForm = true"
    >
      <header class="ui header">
        <h3>
          {{ t('views.admin.moderation.DomainsDetail.header.activePolicy') }}
        </h3>
      </header>
    </instance-policy-card>
    <instance-policy-form
      v-else-if="showPolicyForm"
      :object="policy"
      type="domain"
      :target="object.name"
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
        :h3="t('views.admin.moderation.DomainsDetail.header.instanceData')"
        class="category"
      />
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.moderation.DomainsDetail.table.instanceData.inAllowList.label') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">
          <span v-if="object?.allowed">
            {{ t('views.admin.moderation.DomainsDetail.table.instanceData.inAllowList.true') }}
          </span>
          <span v-else>
            {{ t('views.admin.moderation.DomainsDetail.table.instanceData.inAllowList.false') }}
          </span>
        </span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.moderation.DomainsDetail.table.instanceData.lastChecked') }}
        </span>
        <Spacer
          h
          grow
        />
        <HumanDate
          v-if="object?.nodeinfo_fetch_date"
          :date="object?.nodeinfo_fetch_date"
        />
        <span v-else>
          {{ t('views.admin.moderation.DomainsDetail.notApplicable') }}
        </span>
      </Layout>
      <Layout
        v-if="object?.nodeinfo && object?.nodeinfo.status === 'ok'"
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.moderation.DomainsDetail.table.instanceData.software.label') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">
          {{ t('views.admin.moderation.DomainsDetail.table.instanceData.software.value', {
            name: get(object,
                      'nodeinfo.payload.software.name', t('views.admin.moderation.DomainsDetail.notApplicable')), version:
                        get(object,
                            'nodeinfo.payload.software.version', t('views.admin.moderation.DomainsDetail.notApplicable'))}) }}
        </span>
      </Layout>
      <Layout
        v-if="object?.nodeinfo && object?.nodeinfo.status === 'error'"
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.moderation.DomainsDetail.table.instanceData.nodeInfoStatus.label') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">
          {{ t('views.admin.moderation.DomainsDetail.table.instanceData.nodeInfoStatus.value', {
            name: get(object,
                      'nodeinfo.payload.software.name', t('views.admin.moderation.DomainsDetail.notApplicable')), version:
                        get(object,
                            'nodeinfo.payload.software.version', t('views.admin.moderation.DomainsDetail.notApplicable'))}) }}
        </span>
        <span :data-tooltip="object.nodeinfo.error"><i class="bi bi-question-circle" /></span>
      </Layout>
      <ajax-button
        method="get"
        :url="'manage/federation/domains/' + object?.name + '/nodeinfo/'"
        @action-done="refreshNodeInfo"
      >
        {{ t('views.admin.moderation.DomainsDetail.button.refreshNodeInfo') }}
      </ajax-button>
    </Layout>

    <Layout
      stack
      style="flex: 1; gap: 0;"
    >
      <Heading
        :h3="t('views.admin.moderation.DomainsDetail.header.activity')"
        class="category"
      >
        <span
          :data-tooltip="labels.statsWarning"
          style="margin-left: 8px;"
        >
          <i class="bi bi-question-circle" /></span>
      </Heading>
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.moderation.DomainsDetail.table.activity.firstSeen') }}
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
        <Link
          class="label"
          :to="{ name: 'manage.moderation.accounts.list', query: { q: 'domain:' + object?.name } }"
        >
          {{ t('views.admin.moderation.DomainsDetail.link.knownAccounts') }}
        </Link>
        <Spacer
          h
          grow
        />
        <span class="value">{{ stats?.actors }}</span>
      </Layout>
    </Layout>

    <Layout
      stack
      style="flex: 1; gap: 0;"
    >
      <Heading
        :h3="t('views.admin.moderation.DomainsDetail.header.audioContent')"
        class="category"
      >
        <span
          :data-tooltip="labels.statsWarning"
          style="margin-left: 8px;"
        >
          <i class="bi bi-question-circle" /></span>
      </Heading>
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.moderation.DomainsDetail.table.audioContent.cachedSize') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ humanSize(stats?.media_downloaded_size) }}</span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.moderation.DomainsDetail.table.audioContent.totalSize') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ humanSize(stats?.media_total_size) }}</span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <span class="label">
          <router-link :to="{ name: 'manage.channels', query: { q: getQuery('domain', object.name) } }">
            {{ t('views.admin.moderation.DomainsDetail.link.channels') }}
          </router-link>
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ stats?.channels }}</span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <span class="label">
          <router-link :to="{ name: 'manage.library.libraries', query: { q: getQuery('domain', object.name) } }">
            {{ t('views.admin.moderation.DomainsDetail.link.libraries') }}
          </router-link>
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ stats?.libraries }}</span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <span class="label">
          <router-link :to="{ name: 'manage.library.uploads', query: { q: getQuery('domain', object.name) } }">
            {{ t('views.admin.moderation.DomainsDetail.link.uploads') }}
          </router-link>
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ stats?.uploads }}</span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <span class="label">
          <router-link :to="{ name: 'manage.library.artists', query: { q: getQuery('domain', object.name) } }">
            {{ t('views.admin.moderation.DomainsDetail.link.artists') }}
          </router-link>
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ stats?.artists }}</span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <span class="label">
          <router-link :to="{ name: 'manage.library.albums', query: { q: getQuery('domain', object.name) } }">
            {{ t('views.admin.moderation.DomainsDetail.link.albums') }}
          </router-link>
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ stats?.albums }}</span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <span class="label">
          <router-link :to="{ name: 'manage.library.tracks', query: { q: getQuery('domain', object.name) } }">
            {{ t('views.admin.moderation.DomainsDetail.link.tracks') }}
          </router-link>
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ stats?.tracks }}</span>
      </Layout>
    </Layout>
  </Layout>
</template>

<style scoped lang="scss">
@import '~/style/funkwhale.scss';

.channel-image {
  width: 200px;
  height: 200px;
  font-size: 160px;
  border: none;
  display: block;
  text-align: center;
  align-content: center;

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
