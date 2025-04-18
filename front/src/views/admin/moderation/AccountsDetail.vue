<script setup lang="ts">
import type { InstancePolicy } from '~/types'

import { computed, ref, reactive } from 'vue'
// import { useCurrentElement } from '@vueuse/core'
import { humanSize } from '~/utils/filters'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'

import axios from 'axios'

import Layout from '~/components/ui/Layout.vue'
import Loader from '~/components/ui/Loader.vue'
import Button from '~/components/ui/Button.vue'
import Spacer from '~/components/ui/Spacer.vue'
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

// TODO: Find out if the following removal causes any regression #2440
// const el = useCurrentElement()
// watch(object, async () => {
//   await nextTick()
//   $(el.value).find('select.dropdown').dropdown()
// })

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
  <Layout
    main
    stack
    class="page-admin-account-detail"
  >
    <Loader
      v-if="isLoading"
    />
    <template v-if="object">
      <section
        v-title="object.full_username"
      >
        <Layout flex>
          <h2 class="ui header">
            <i class="bi-person-circle" />
            {{ object.full_username }}
            <div class="sub header">
              <template v-if="object.user">
                <span class="ui tiny accent label">
                  <i class="bi-house-fill" />
                  {{ t('views.admin.moderation.AccountsDetail.header.localAccount') }}
                </span>
                &nbsp;
              </template>
              <a
                :href="object.url || object.fid"
                target="_blank"
                rel="noopener noreferrer"
              >
                {{ t('views.admin.moderation.AccountsDetail.link.openProfile') }}&nbsp;
                <i class="bi bi-box-arrow-up-right" />
              </a>
            </div>
          </h2>
          <Spacer grow />
          <Layout stack>
            <a
              v-if="object.user && store.state.auth.profile && store.state.auth.profile.is_superuser"
              class="ui labeled icon button"
              :href="store.getters['instance/absoluteUrl'](`/api/admin/users/user/${object.user.id}`)"
              target="_blank"
              rel="noopener noreferrer"
            >
              <i class="bi bi-wrench" />
              {{ t('views.admin.moderation.AccountsDetail.link.django') }}&nbsp;
            </a>
            <a
              v-else-if="store.state.auth.profile && store.state.auth.profile.is_superuser"
              :href="store.getters['instance/absoluteUrl'](`/api/admin/federation/actor/${object.id}`)"
              target="_blank"
              rel="noopener noreferrer"
            >
              <i class="bi bi-wrench" />
              {{ t('views.admin.moderation.AccountsDetail.link.django') }}&nbsp;
            </a>
            <a
              :href="object.url || object.fid"
              target="_blank"
              rel="noopener noreferrer"
            >
              <i class="bi bi-box-arrow-up-right" />
              {{ t('views.admin.moderation.AccountsDetail.link.remoteProfile') }}&nbsp;
            </a>
          </Layout>
          <div class="ui column">
            <div
              v-if="!object.user"
              class="ui compact clearing placeholder segment component-placeholder"
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
                <header class="ui header">
                  <h3>
                    <i class="bi bi-shield-fill" />
                    {{ t('views.admin.moderation.AccountsDetail.header.noPolicy') }}
                  </h3>
                </header>
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
                :target="object.full_username"
                @cancel="showPolicyForm = false"
                @save="updatePolicy"
                @delete="policy = null; showPolicyForm = false"
              />
            </div>
          </div>
        </Layout>
      </section>
      <Layout flex>
        <div class="column">
          <section>
            <h3 class="ui header">
              <i class="bi bi-info-circle-fill" />
              {{ t('views.admin.moderation.AccountsDetail.header.accountData') }}
            </h3>
            <table class="ui very basic table">
              <tbody>
                <tr>
                  <td>
                    {{ t('views.admin.moderation.AccountsDetail.table.accountData.username') }}
                  </td>
                  <td>
                    {{ object.preferred_username }}
                  </td>
                </tr>
                <tr v-if="!object.user">
                  <td>
                    <router-link :to="{name: 'manage.moderation.domains.detail', params: {id: object.domain }}">
                      {{ t('views.admin.moderation.AccountsDetail.link.domain') }}
                    </router-link>
                  </td>
                  <td>
                    {{ object.domain }}
                  </td>
                </tr>
                <tr>
                  <td>
                    {{ t('views.admin.moderation.AccountsDetail.table.accountData.displayName') }}
                  </td>
                  <td>
                    {{ object.name }}
                  </td>
                </tr>
                <tr v-if="object.user">
                  <td>
                    {{ t('views.admin.moderation.AccountsDetail.table.accountData.email') }}
                  </td>
                  <td>
                    {{ object.user.email }}
                  </td>
                </tr>
                <tr v-if="object.user">
                  <td>
                    {{ t('views.admin.moderation.AccountsDetail.table.accountData.loginStatus.label') }}
                  </td>
                  <td>
                    <div
                      v-if="object.user.username != store.state.auth.profile?.username"
                      class="ui toggle checkbox"
                    >
                      <Input
                        id="is-active"
                        v-model="object.user.is_active"
                        type="checkbox"
                        @change="updateUser('is_active')"
                      />
                      <label for="is-active">
                        <span
                          v-if="object.user.is_active"
                        >{{ t('views.admin.moderation.AccountsDetail.table.accountData.loginStatus.enabled') }}</span>
                        <span
                          v-else
                        >{{ t('views.admin.moderation.AccountsDetail.table.accountData.loginStatus.disabled') }}</span>
                      </label>
                    </div>
                    <span
                      v-else-if="object.user.is_active"
                    >
                      {{ t('views.admin.moderation.AccountsDetail.table.accountData.loginStatus.enabled') }}
                    </span>
                    <span
                      v-else
                    >
                      {{ t('views.admin.moderation.AccountsDetail.table.accountData.loginStatus.disabled') }}
                    </span>
                  </td>
                </tr>
                <tr v-if="object.user">
                  <td>
                    {{ t('views.admin.moderation.AccountsDetail.table.accountData.permissions') }}
                  </td>
                  <td>
                    <select
                      v-model="permissions"
                      multiple
                      class="ui search selection dropdown"
                      @change="updateUser('permissions')"
                    >
                      <option
                        v-for="(p, key) in allPermissions"
                        :key="key"
                        :value="p.code"
                      >
                        {{ p.label }}
                      </option>
                    </select>
                    <action-feedback :is-loading="updating.has('permissions')" />
                  </td>
                </tr>
                <tr>
                  <td>
                    {{ t('views.admin.moderation.AccountsDetail.table.accountData.userType') }}
                  </td>
                  <td>
                    {{ object.type }}
                  </td>
                </tr>
                <tr v-if="!object.user">
                  <td>
                    {{ t('views.admin.moderation.AccountsDetail.table.accountData.lastChecked') }}
                  </td>
                  <td>
                    <human-date
                      v-if="object.last_fetch_date"
                      :date="object.last_fetch_date"
                    />
                    <span
                      v-else
                    >
                      {{ t('views.admin.moderation.AccountsDetail.notApplicable') }}
                    </span>
                  </td>
                </tr>
                <tr v-if="object.user">
                  <td>
                    {{ t('views.admin.moderation.AccountsDetail.table.accountData.signupDate') }}
                  </td>
                  <td>
                    <human-date :date="object.user.date_joined" />
                  </td>
                </tr>
                <tr v-if="object.user">
                  <td>
                    {{ t('views.admin.moderation.AccountsDetail.table.accountData.lastActivity') }}
                  </td>
                  <td>
                    <human-date :date="object.user.last_activity" />
                  </td>
                </tr>
              </tbody>
            </table>
          </section>
        </div>
        <div class="column">
          <section>
            <h3 class="ui header">
              <i class="bi bi-rss-fill" />
              {{ t('views.admin.moderation.AccountsDetail.header.activity') }}&nbsp;
              <span :data-tooltip="labels.statsWarning"><i class=" bi bi-question-circle-fill" /></span>
            </h3>
            <div
              v-if="isLoadingStats"
              class="ui placeholder"
            >
              <div class="full line" />
              <div class="short line" />
              <div class="medium line" />
              <div class="long line" />
            </div>
            <table
              v-else
              class="ui very basic table"
            >
              <tbody>
                <tr v-if="!object.user">
                  <td>
                    {{ t('views.admin.moderation.AccountsDetail.table.activity.firstSeen') }}
                  </td>
                  <td>
                    <human-date :date="object.creation_date" />
                  </td>
                </tr>
                <tr>
                  <td>
                    {{ t('views.admin.moderation.AccountsDetail.table.activity.emittedMessages') }}
                  </td>
                  <td>
                    {{ stats.outbox_activities }}
                  </td>
                </tr>
                <tr>
                  <td>
                    {{ t('views.admin.moderation.AccountsDetail.table.activity.receivedFollows') }}
                  </td>
                  <td>
                    {{ stats.received_library_follows }}
                  </td>
                </tr>
                <tr>
                  <td>
                    {{ t('views.admin.moderation.AccountsDetail.table.activity.emittedFollows') }}
                  </td>
                  <td>
                    {{ stats.emitted_library_follows }}
                  </td>
                </tr>
                <tr>
                  <td>
                    <router-link :to="{name: 'manage.moderation.reports.list', query: {q: getQuery('target', `account:${object.full_username}`) }}">
                      {{ t('views.admin.moderation.AccountsDetail.link.linkedReports') }}
                    </router-link>
                  </td>
                  <td>
                    {{ stats.reports }}
                  </td>
                </tr>
                <tr>
                  <td>
                    <router-link :to="{name: 'manage.moderation.requests.list', query: {q: getQuery('submitter', `${object.full_username}`) }}">
                      {{ t('views.admin.moderation.AccountsDetail.link.requests') }}
                    </router-link>
                  </td>
                  <td>
                    {{ stats.requests }}
                  </td>
                </tr>
              </tbody>
            </table>
          </section>
        </div>
        <div class="column">
          <section>
            <h3 class="ui header">
              <i class="bi bi-music-note-beamed" />
              {{ t('views.admin.moderation.AccountsDetail.header.audioContent') }}&nbsp;
              <span :data-tooltip="labels.statsWarning"><i class="question circle icon" /></span>
            </h3>
            <div
              v-if="isLoadingStats"
              class="ui placeholder"
            >
              <div class="full line" />
              <div class="short line" />
              <div class="medium line" />
              <div class="long line" />
            </div>
            <table
              v-else
              class="ui very basic table"
            >
              <tbody>
                <tr v-if="!object.user">
                  <td>
                    {{ t('views.admin.moderation.AccountsDetail.table.audioContent.cachedSize') }}
                  </td>
                  <td>
                    {{ humanSize(stats.media_downloaded_size) }}
                  </td>
                </tr>
                <tr v-if="object.user">
                  <td>
                    {{ t('views.admin.moderation.AccountsDetail.table.audioContent.uploadQuota') }}
                    <span :data-tooltip="labels.uploadQuota"><i class="question circle icon" /></span>
                  </td>
                  <td>
                    <Input
                      v-model.number="object.user.upload_quota"
                      step="100"
                      name="quota"
                      type="number"
                      @change="updateUser('upload_quota', true)"
                    />
                    <div class="ui basic label">
                      {{ t('views.admin.moderation.AccountsDetail.table.audioContent.megabyte') }}
                    </div>
                    <action-feedback
                      class="ui basic label"
                      size="tiny"
                      :is-loading="updating.has('upload_quota')"
                    />
                  </td>
                </tr>
                <tr>
                  <td>
                    {{ t('views.admin.moderation.AccountsDetail.table.audioContent.totalSize') }}
                  </td>
                  <td>
                    {{ humanSize(stats.media_total_size) }}
                  </td>
                </tr>
                <tr>
                  <td>
                    <router-link :to="{name: 'manage.channels', query: {q: getQuery('account', object.full_username) }}">
                      {{ t('views.admin.moderation.AccountsDetail.link.channels') }}
                    </router-link>
                  </td>
                  <td>
                    {{ stats.channels }}
                  </td>
                </tr>
                <tr>
                  <td>
                    <router-link :to="{name: 'manage.library.libraries', query: {q: getQuery('account', object.full_username) }}">
                      {{ t('views.admin.moderation.AccountsDetail.link.libraries') }}
                    </router-link>
                  </td>
                  <td>
                    {{ stats.libraries }}
                  </td>
                </tr>
                <tr>
                  <td>
                    <router-link :to="{name: 'manage.library.uploads', query: {q: getQuery('account', object.full_username) }}">
                      {{ t('views.admin.moderation.AccountsDetail.link.uploads') }}
                    </router-link>
                  </td>
                  <td>
                    {{ stats.uploads }}
                  </td>
                </tr>
                <tr>
                  <td>
                    {{ t('views.admin.moderation.AccountsDetail.link.artists') }}
                  </td>
                  <td>
                    {{ stats.artists }}
                  </td>
                </tr>
                <tr>
                  <td>
                    {{ t('views.admin.moderation.AccountsDetail.link.albums') }}
                  </td>
                  <td>
                    {{ stats.albums }}
                  </td>
                </tr>
                <tr>
                  <td>
                    {{ t('views.admin.moderation.AccountsDetail.link.tracks') }}
                  </td>
                  <td>
                    {{ stats.tracks }}
                  </td>
                </tr>
              </tbody>
            </table>
          </section>
        </div>
      </Layout>
    </template>
  </Layout>
</template>
