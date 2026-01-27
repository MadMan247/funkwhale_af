<script setup lang="ts">
import type { BackendError, Application, PrivacyLevelEnum } from '~/types'
import type { $ElementType } from 'utility-types'

import axios from 'axios'

import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useStore } from '~/store'

import useSharedLabels from '~/composables/locale/useSharedLabels'
import useLogger from '~/composables/useLogger'

import DangerousButton from '~/components/common/DangerousButton.vue'
import SubsonicTokenForm from '~/components/auth/SubsonicTokenForm.vue'
import AttachmentInput from '~/components/common/AttachmentInput.vue'
import PasswordInput from '~/components/forms/PasswordInput.vue'

import Input from '~/components/ui/Input.vue'
import Layout from '~/components/ui/Layout.vue'
import Slider from '~/components/ui/Slider.vue'
import Alert from '~/components/ui/Alert.vue'
import Header from '~/components/ui/Header.vue'
import Button from '~/components/ui/Button.vue'
import Link from '~/components/ui/Link.vue'
import Textarea from '~/components/ui/Textarea.vue'
import Section from '~/components/ui/Section.vue'
import Table from '~/components/ui/Table.vue'

const SETTINGS_ORDER: FieldId[] = ['summary', 'privacy_level']

type Field = { id: 'summary', type: 'content', value: { text: string, content_type: 'text/markdown' } }
  | { id: 'privacy_level', type: 'dropdown', choices: PrivacyLevelEnum[], value: string }
type FieldId = $ElementType<Field, 'id'>

interface Settings {
  success: boolean
  errors: string[]
  order: FieldId[]
  fields: Record<FieldId, Field>
}

const { t } = useI18n()
const sharedLabels = useSharedLabels()
const logger = useLogger()
const router = useRouter()
const store = useStore()

const settings = reactive({
  success: false,
  errors: [] as string[],
  fields: {
    summary: {
      id: 'summary',
      type: 'content',
      value: store.state.auth.profile?.summary ?? { text: '', content_type: 'text/markdown' }
    },
    privacy_level: {
      id: 'privacy_level',
      type: 'dropdown',
      value: store.state.auth.profile?.privacy_level,
      choices: ['me', 'instance', 'followers', 'everyone']
    }
  }
} as Settings)

const orderedSettingsFields = SETTINGS_ORDER.map(id => settings.fields[id])

const labels = computed(() => ({
  title: t('components.auth.Settings.title')
}))

const isLoading = ref(false)
const submitSettings = async () => {
  settings.success = false
  settings.errors = []
  isLoading.value = true

  const payload = {} as Record<FieldId, string | null | { text: string }>
  for (const id of SETTINGS_ORDER) {
    const field = settings.fields[id]
    payload[id] = field.type === 'content' && !field.value.text
      ? null
      : field.value
  }

  try {
    await axios.patch(`users/${store.state.auth.username}/`, payload)

    logger.info('Updated settings successfully')
    settings.success = true

    const me = await axios.get('users/me/')
    store.dispatch('auth/updateProfile', me.data)
  } catch (error) {
    logger.error('Error while updating settings')
    settings.errors.push(...(error as BackendError).backendErrors)
  }

  isLoading.value = false
}

const apps = ref([] as Application[])
const isLoadingApps = ref(false)
const fetchApps = async () => {
  apps.value = []
  isLoadingApps.value = true

  try {
    const response = await axios.get('oauth/grants/')
    apps.value = response.data as Application[]
  } catch (error) {
    logger.error('Error while fetching Apps')
    settings.errors.push(...(error as BackendError).backendErrors)
  }

  isLoadingApps.value = false
}

const ownedApps = ref([] as Application[])
const fetchOwnedApps = async () => {
  ownedApps.value = []
  // TODO: Add loader

  try {
    const response = await axios.get('oauth/apps/')
    ownedApps.value = response.data.results as Application[]
  } catch (error) {
    logger.error('Error while fetching owned Apps')
    settings.errors.push(...(error as BackendError).backendErrors)
  }
}

const isRevoking = reactive(new Set())
const revokeApp = async (id: string) => {
  isRevoking.add(id)

  try {
    await axios.delete(`oauth/grants/${id}/`)
    apps.value = apps.value.filter(app => app.client_id !== id)
  } catch (error) {
    logger.error('Error while revoking App')
    settings.errors.length = 0
    settings.errors.push(...(error as BackendError).backendErrors)
  }

  isRevoking.delete(id)
}

const isDeleting = reactive(new Set())
const deleteApp = async (id: string) => {
  isDeleting.add(id)

  try {
    await axios.delete(`oauth/apps/${id}/`)
    ownedApps.value = ownedApps.value.filter(app => app.client_id !== id)
  } catch (error) {
    logger.error('Error while deleting App')
    settings.errors.length = 0
    settings.errors.push(...(error as BackendError).backendErrors)
  }

  isDeleting.delete(id)
}

const avatar = ref({ uuid: null, ...(store.state.auth.profile?.avatar ?? {}) })
// TODO (wvffle): Maybe should be reactive?
const initialAvatar = avatar.value.uuid ?? undefined
const avatarErrors = ref([] as string[])
const isLoadingAvatar = ref(false)
const submitAvatar = async (uuid: string | null) => {
  if (!uuid) return

  isLoadingAvatar.value = true

  try {
    const response = await axios.patch(`users/${store.state.auth.username}/`, { avatar: uuid })
    avatar.value = response.data.avatar
    store.commit('auth/avatar', response.data.avatar)
  } catch (error) {
    avatarErrors.value = (error as BackendError).backendErrors
  }

  avatarErrors.value = []
  isLoadingAvatar.value = false
}

const passwordError = ref('')
const credentials = reactive({
  oldPassword: '',
  newPassword: ''
})
const isLoadingPassword = ref(false)
const submitPassword = async () => {
  isLoadingPassword.value = true
  passwordError.value = ''

  try {
    await axios.post('auth/registration/change-password/', {
      old_password: credentials.oldPassword,
      new_password1: credentials.newPassword,
      new_password2: credentials.newPassword
    })

    logger.info('Password successfully changed')
    return router.push({
      name: 'profile.content',
      params: { username: store.state.auth.username }
    })
  } catch (error) {
    if ((error as BackendError).response?.status === 400) {
      passwordError.value = 'invalid_credentials'
    } else {
      passwordError.value = 'unknown_error'
    }
  }

  isLoadingPassword.value = false
}

const deleteAccountPassword = ref('')
const isDeletingAccount = ref(false)
const accountDeleteErrors = ref([] as string[])
const deleteAccount = async () => {
  isDeletingAccount.value = true
  accountDeleteErrors.value = []

  try {
    const payload = {
      confirm: true,
      password: deleteAccountPassword.value
    }

    await axios.delete('users/me/', { data: payload })

    store.commit('ui/addMessage', {
      content: t('components.auth.Settings.message.confirmDelete'),
      date: new Date()
    })

    store.dispatch('auth/logout')
  } catch (error) {
    accountDeleteErrors.value = (error as BackendError).backendErrors
  }

  deleteAccountPassword.value = ''
  isDeletingAccount.value = false
}

const isChangingEmail = ref(false)
const emailPassword = ref('')
const newEmail = ref('')
const changeEmailErrors = ref([] as string[])
const changeEmail = async () => {
  isChangingEmail.value = true
  changeEmailErrors.value = []

  try {
    await axios.post('users/users/change-email/', {
      password: emailPassword.value,
      email: newEmail.value
    })

    newEmail.value = ''
  } catch (error) {
    changeEmailErrors.value = (error as BackendError).backendErrors
  }

  emailPassword.value = ''
  isChangingEmail.value = false
}

fetchApps()
fetchOwnedApps()
store.dispatch('moderation/fetchContentFilters')
store.dispatch('moderation/fetchActorFilters')
</script>

<template>
  <Layout
    v-title="labels.title"
    main
    stack
    gap-84
  >
    <Header
      :h1="t('components.auth.Settings.header.accountSettings')"
      page-heading
    />
    <Layout
      form
      @submit.prevent="submitSettings()"
    >
      <Alert
        v-if="settings.success"
        green
      >
        <h4 class="header">
          {{ t('components.auth.Settings.header.settingsUpdated') }}
        </h4>
      </Alert>
      <Alert
        v-if="settings.errors.length > 0"
        red
        role="alert"
      >
        <h4 class="header">
          {{ t('components.auth.Settings.header.updateFailure') }}
        </h4>
        <ul class="list">
          <li
            v-for="(error, key) in settings.errors"
            :key="key"
          >
            {{ error }}
          </li>
        </ul>
      </Alert>
      <div
        v-for="f in orderedSettingsFields"
        :key="f.id + sharedLabels.fields[f.id].help"
        class="field"
      >
        <Textarea
          v-if="f.type === 'content'"
          v-model="f.value.text"
          :label="sharedLabels.fields[f.id].label"
          :placeholder="sharedLabels.fields[f.id].help"
        />
        <template v-else>
          <label :for="f.id">{{ sharedLabels.fields[f.id].label }}</label>
          <p v-if="sharedLabels.fields[f.id].help">
            {{ sharedLabels.fields[f.id].help }}
          </p>
          <Slider
            v-if="f.type === 'dropdown'"
            v-model="f.value"
            :options="Object.fromEntries(f.choices.map(c => [c, sharedLabels.fields[f.id].choices?.[c] || c]))"
          />
        </template>
      </div>
      <Button
        primary
        :is-loading="isLoading"
        type="submit"
      >
        {{ t('components.auth.Settings.button.updateSettings') }}
      </Button>
    </Layout>
    <Section
      large-section-heading
      :h2="t('components.auth.Settings.header.avatar')"
    >
      <Layout form>
        <Alert
          v-if="avatarErrors.length > 0"
          red
          role="alert"
        >
          <h4 class="header">
            {{ t('components.auth.Settings.header.avatarFailure') }}
          </h4>
          <ul class="list">
            <li
              v-for="(error, key) in avatarErrors"
              :key="key"
            >
              {{ error }}
            </li>
          </ul>
        </Alert>
        <attachment-input
          v-model="avatar.uuid"
          :initial-value="initialAvatar"
          @update:model-value="submitAvatar($event)"
          @delete="avatar = {uuid: null}"
        >
          {{ t('components.auth.Settings.label.avatar') }}
        </attachment-input>
      </Layout>
    </Section>

    <Section
      large-section-heading
      :h2="t('components.auth.Settings.header.changePassword')"
    >
      <div class="ui message">
        {{ t('components.auth.Settings.description.changePassword.paragraph1') }}&nbsp;{{ t('components.auth.Settings.description.changePassword.paragraph2') }}
      </div>
      <Layout
        form
        @submit.prevent="submitPassword()"
      >
        <Alert
          v-if="passwordError"
          role="alert"
        >
          <h4 class="header">
            {{ t('components.auth.Settings.header.passwordFailure') }}
          </h4>
          <ul class="list">
            <li v-if="passwordError == 'invalid_credentials'">
              {{ t('components.auth.Settings.help.changePassword') }}
            </li>
          </ul>
        </Alert>
        <!-- TODO: Use  -->
        <div class="field">
          <label for="old-password-field">{{ t('components.auth.Settings.label.currentPassword') }}</label>
          <password-input
            v-model="credentials.oldPassword"
            field-id="old-password-field"
            required
          />
        </div>
        <div class="field">
          <label for="new-password-field">{{ t('components.auth.Settings.label.newPassword') }}</label>
          <password-input
            v-model="credentials.newPassword"
            field-id="new-password-field"
            required
          />
        </div>
        <dangerous-button
          :class="['ui', {'loading': isLoadingPassword}, {disabled: !credentials.newPassword || !credentials.oldPassword}, 'warning', 'button']"
          :action="submitPassword"
          :title="t('components.auth.Settings.modal.changePassword.header')"
        >
          {{ t('components.auth.Settings.button.password') }}
          <template #content>
            <div>
              <p>
                {{ t('components.auth.Settings.modal.changePassword.content.warning') }}
              </p>
              <ul>
                <li>
                  {{ t('components.auth.Settings.modal.changePassword.content.logout') }}
                </li>
                <li>
                  {{ t('components.auth.Settings.modal.changePassword.content.subsonic') }}
                </li>
              </ul>
            </div>
          </template>
          <template #confirm>
            <div>
              {{ t('components.auth.Settings.button.disableSubsonic') }}
            </div>
          </template>
        </dangerous-button>
      </Layout>
      <div class="ui hidden divider" />
      <subsonic-token-form />
    </Section>

    <Section
      id="content-filters"
      large-section-heading
      icon="bi-eye-slash"
      :h2="t('components.auth.Settings.header.contentFilters')"
    >
      <p>
        {{ t('components.auth.Settings.description.contentFilters') }}
      </p>

      <Button
        primary
        icon="bi-arrow-clockwise"
        @click="store.dispatch('moderation/fetchContentFilters'); store.dispatch('moderation/fetchActorFilters')"
      >
        {{ t('components.auth.Settings.button.refresh') }}
      </Button>
      <h3 class="ui header">
        {{ t('components.auth.Settings.header.hiddenArtists') }}
      </h3>
      <Table :grid-template-columns="['auto', 'auto', 'auto']">
        <template #header>
          <label>{{ t('components.auth.Settings.table.artists.header.name') }}</label>
          <label>{{ t('components.auth.Settings.table.artists.header.creationDate') }}</label>
          <label>{{ t('components.auth.Settings.table.artists.header.action') }}</label>
        </template>
        <template
          v-for="filter in store.getters['moderation/artistFilters']()"
          :key="filter.uuid"
        >
          <router-link :to="{name: 'library.artists.detail', params: {id: filter.target.id }}">
            {{ filter.target.name }}
          </router-link>
          <human-date :date="filter.creation_date" />
          <Button
            destructive
            square
            icon="bi-trash"
            @click="async () => {
              await store.dispatch('moderation/deleteContentFilter', filter.uuid)
            }"
          />
        </template>
      </Table>
      <h3 class="ui header">
        {{ t('components.auth.Settings.header.hiddenActors') }}
      </h3>
      <Table :grid-template-columns="['auto', 'auto']">
        <template #header>
          <label>{{ t('components.auth.Settings.table.artists.header.name') }}</label>
          <label>{{ t('components.auth.Settings.table.artists.header.action') }}</label>
        </template>
        <template
          v-for="filter in store.getters['moderation/actorFilters']()"
          :key="filter.fid"
        >
          <actor-link :actor="filter" />
          <Button
            destructive
            square
            icon="bi-trash"
            @click="async () => {
              await store.dispatch('moderation/deleteActorFilter', filter.full_username)
            }"
          />
        </template>
      </table>
    </Section>
    <Section
      id="grants"
      :h2="t('components.auth.Settings.header.authorizedApps')"
      large-section-heading
      icon="bi-unlock-fill"
      class="ui text container"
    >
      <p>
        {{ t('components.auth.Settings.description.authorizedApps') }}
      </p>
      <Button
        primary
        icon="bi-arrow-clockwise"
        :is-loading="isLoadingApps"
        @click="fetchApps()"
      >
        {{ t('components.auth.Settings.button.refresh') }}
      </Button>
      <table
        v-if="apps.length > 0"
        class="ui compact very basic unstackable table"
      >
        <thead>
          <tr>
            <th>
              {{ t('components.auth.Settings.table.authorizedApps.header.application') }}
            </th>
            <th>
              {{ t('components.auth.Settings.table.authorizedApps.header.permissions') }}
            </th>
            <th />
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="app in apps"
            :key="app.client_id"
          >
            <td>
              {{ app.name }}
            </td>
            <td>
              {{ app.scopes }}
            </td>
            <td>
              <dangerous-button
                :class="['ui', 'tiny', 'danger', { loading: isRevoking.has(app.client_id) }, 'button']"
                :title="t('components.auth.Settings.modal.revokeApp.header', {app: app.name})"
                @confirm="revokeApp(app.client_id)"
              >
                {{ t('components.auth.Settings.button.revoke') }}
                <template #content>
                  {{ t('components.auth.Settings.modal.revokeApp.content.warning') }}
                </template>
                <template #confirm>
                  {{ t('components.auth.Settings.button.revokeAccess') }}
                </template>
              </dangerous-button>
            </td>
          </tr>
        </tbody>
      </table>
      <empty-state v-else>
        <template #title>
          {{ t('components.auth.Settings.header.noApps') }}
        </template>
        {{ t('components.auth.Settings.help.noApps') }}
      </empty-state>
    </Section>
    <Section
      id="apps"
      large-section-heading
      icon="bi-code-slash"
      :h2="t('components.auth.Settings.header.yourApps')"
      class="ui text container"
    >
      <p>
        {{ t('components.auth.Settings.description.yourApps') }}
      </p>
      <Link
        solid
        primary
        icon="bi-plus-lg"
        :to="{name: 'settings.applications.new'}"
      >
        {{ t('components.auth.Settings.link.newApp') }}
      </Link>
      <Table
        v-if="ownedApps.length > 0"
        :grid-template-columns="['auto', 'auto', 'auto', '136px']"
      >
        <template #header>
          <label>
            {{ t('components.auth.Settings.table.yourApps.header.application') }}
          </label>
          <label>
            {{ t('components.auth.Settings.table.yourApps.header.scopes') }}
          </label>
          <label>
            {{ t('components.auth.Settings.table.yourApps.header.creationDate') }}
          </label>
          <label>
            {{ t('components.auth.Settings.table.artists.header.action') }}
          </label>
        </template>
        <template
          v-for="app in ownedApps"
          :key="app.client_id"
        >
          <div>
            <router-link :to="{name: 'settings.applications.edit', params: {id: app.client_id}}">
              {{ app.name }}
            </router-link>
          </div>
          <div>
            {{ app.scopes }}
          </div>
          <div>
            <human-date :date="app.created" />
          </div>
          <Layout
            stack
            gap-8
          >
            <Link
              solid
              primary
              icon="bi-pencil-fill"
              class="ui tiny success button"
              :to="{name: 'settings.applications.edit', params: {id: app.client_id}}"
            >
              {{ t('components.auth.Settings.button.edit') }}
            </Link>
            <DangerousButton
              :is-loading="isDeleting.has(app.client_id)"
              class="tiny"
              :title="t('components.auth.Settings.modal.deleteApp.header', {app: app.name})"
              @confirm="deleteApp(app.client_id)"
            >
              {{ t('components.auth.Settings.button.remove') }}
              <template #content>
                {{ t('components.auth.Settings.modal.deleteApp.content.warning') }}
              </template>
              <template #confirm>
                {{ t('components.auth.Settings.button.removeApp') }}
              </template>
            </DangerousButton>
          </Layout>
        </template>
      </Table>
      <empty-state v-else>
        <template #title>
          {{ t('components.auth.Settings.header.noPersonalApps') }}
        </template>
        {{ t('components.auth.Settings.help.noPersonalApps') }}
      </empty-state>
    </Section>

    <Section
      id="plugins"
      large-section-heading
      icon="bi-code"
      :h2="t('components.auth.Settings.header.plugins')"
      class="ui text container"
    >
      <p>
        {{ t('components.auth.Settings.description.plugins') }}
      </p>
      <Link
        primary
        solid
        :to="{name: 'settings.plugins'}"
        icon="bi-puzzle-fill"
      >
        {{ t('components.auth.Settings.link.managePlugins') }}
      </Link>
    </Section>
    <Section
      large-section-heading
      icon="bi-envelope-at"
      :h2="t('components.auth.Settings.header.changeEmail')"
    >
      <p>
        {{ t('components.auth.Settings.description.changeEmail') }}
      </p>
      <p>
        {{ t('components.auth.Settings.message.currentEmail', { email: store.state.auth.profile?.email }) }}
      </p>
      <Layout
        form
        @submit.prevent="changeEmail"
      >
        <Alert
          v-if="changeEmailErrors.length > 0"
          red
          role="alert"
        >
          <h4 class="header">
            {{ t('components.auth.Settings.header.emailFailure') }}
          </h4>
          <ul class="list">
            <li
              v-for="(error, key) in changeEmailErrors"
              :key="key"
            >
              {{ error }}
            </li>
          </ul>
        </Alert>
        <div class="field">
          <label for="new-email">{{ t('components.auth.Settings.label.newEmail') }}</label>
          <Input
            id="new-email"
            v-model="newEmail"
            required
            type="email"
          />
        </div>
        <div class="field">
          <label for="current-password-field-email">{{ t('components.auth.Settings.label.password') }}</label>
          <password-input
            v-model="emailPassword"
            field-id="current-password-field-email"
            required
          />
        </div>
        <Button
          primary
          type="submit"
        >
          {{ t('components.auth.Settings.button.update') }}
        </Button>
      </Layout>
    </Section>
    <Section
      large-section-heading
      :h2="t('components.auth.Settings.header.deleteAccount')"
      icon="bi-trash"
    >
      <p>
        {{ t('components.auth.Settings.description.deleteAccount') }}
      </p>
      <Alert
        yellow
        role="alert"
      >
        {{ t('components.auth.Settings.warning.deleteAccount') }}
      </Alert>
      <Layout form>
        <Alert
          v-if="accountDeleteErrors.length > 0"
          red
          role="alert"
        >
          <h4 class="header">
            {{ t('components.auth.Settings.header.accountFailure') }}
          </h4>
          <ul class="list">
            <li
              v-for="(error, key) in accountDeleteErrors"
              :key="key"
            >
              {{ error }}
            </li>
          </ul>
        </Alert>
        <div class="field">
          <label for="current-password-field">{{ t('components.auth.Settings.label.currentPassword') }}</label>
          <password-input
            v-model="deleteAccountPassword"
            field-id="current-password-field"
            required
          />
        </div>
        <dangerous-button
          :is-loading="isDeletingAccount"
          :disabled="!deleteAccountPassword || undefined"
          :class="{danger: deleteAccountPassword}"
          :action="deleteAccount"
          :title="t('components.auth.Settings.modal.deleteAccount.header')"
        >
          {{ t('components.auth.Settings.button.deleteAccount') }}
          <template #content>
            {{ t('components.auth.Settings.modal.deleteAccount.content.warning') }}
          </template>
          <template #confirm>
            {{ t('components.auth.Settings.button.deleteAccountConfirm') }}
          </template>
        </dangerous-button>
      </Layout>
    </Section>
  </Layout>
</template>
