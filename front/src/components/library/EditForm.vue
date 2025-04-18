<script setup lang="ts">
import type { EditObject, EditObjectType } from '~/composables/moderation/useEditConfigs'
import type { BackendError, License, ReviewState } from '~/types'

import { computed, reactive, ref } from 'vue'
import { isEqual, clone } from 'lodash-es'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'
import { useRoute } from 'vue-router'

import axios from 'axios'

import Layout from '~/components/ui/Layout.vue'
import Button from '~/components/ui/Button.vue'
import Link from '~/components/ui/Link.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Input from '~/components/ui/Input.vue'
import Textarea from '~/components/ui/Textarea.vue'
import Pills from '~/components/ui/Pills.vue'
import Alert from '~/components/ui/Alert.vue'

import AttachmentInput from '~/components/common/AttachmentInput.vue'
import useEditConfigs from '~/composables/moderation/useEditConfigs'
import EditList from '~/components/library/EditList.vue'
import EditCard from '~/components/library/EditCard.vue'

interface Props {
  objectType: EditObjectType
  object: EditObject
  licenses?: License[]
}

const props = withDefaults(defineProps<Props>(), {
  licenses: () => []
})

const { t } = useI18n()
const configs = useEditConfigs()
const store = useStore()
const route = useRoute()

const config = computed(() => configs[props.objectType])
const currentState = computed(() => config.value.fields.reduce((state: ReviewState, field) => {
  state[field.id] = { value: field.getValue(props.object) }
  return state
}, {}))

const canEdit = computed(() => {
  if (!store.state.auth.authenticated) return false

  const isOwner = props.object.attributed_to
    && store.state.auth.fullUsername === props.object.attributed_to.full_username

  return isOwner || store.state.auth.availablePermissions.library
})

const labels = computed(() => ({
  summaryPlaceholder: t('components.library.EditForm.placeholder.summary')
}))

const mutationsUrl = computed(() => props.objectType === 'track'
  ? `tracks/${props.object.id}/mutations/`
  : props.objectType === 'album'
    ? `albums/${props.object.id}/mutations/`
    : props.objectType === 'artist'
      ? `artists/${props.object.id}/mutations/`
      : ''
)

const mutationPayload = computed(() => {
  const changedFields = config.value.fields.filter(f => {
    return !isEqual(values[f.id], initialValues[f.id])
  })

  if (changedFields.length === 0) {
    return {}
  }

  const data = {
    type: 'update',
    payload: {} as Record<string, unknown>,
    summary: summary.value
  }

  for (const field of changedFields) {
    data.payload[field.id] = values[field.id]
  }

  return data
})

const showPendingReview = ref(true)
const editListFilters = computed(() => showPendingReview.value
  ? { is_approved: 'null' }
  : {}
)

const values = reactive({} as Record<string, any>)
const initialValues = reactive({} as Record<string, any>)
for (const { id, getValue } of config.value?.fields) {
  values[id] = clone(getValue(props.object))
  initialValues[id] = clone(values[id])
}

const submittedMutation = ref()
const summary = ref('')

const errors = ref([] as string[])
const isLoading = ref(false)
const submit = async () => {
  const url = mutationsUrl.value
  if (!url) return

  isLoading.value = true
  errors.value = []

  try {
    const response = await axios.post(url, {
      ...mutationPayload.value,
      is_approved: canEdit.value
        ? true
        : undefined
    })

    submittedMutation.value = response.data
  } catch (error) {
    errors.value = (error as BackendError).backendErrors
  }

  isLoading.value = false
}

const fieldValuesChanged = (fieldId: string) => {
  return !isEqual(values[fieldId], initialValues[fieldId])
}

const resetField = (fieldId: string) => {
  values[fieldId] = clone(initialValues[fieldId])
}
</script>

<template>
  <Alert
    v-if="submittedMutation"
    green
  >
    <h4 class="header">
      {{ t('components.library.EditForm.header.success') }}
    </h4>
    <edit-card
      :obj="submittedMutation"
      :current-state="currentState"
    />
    <Button
      solid
      primary
      @click.prevent="submittedMutation = null"
    >
      {{ t('components.library.EditForm.button.new') }}
    </Button>

    <!-- TODO: Implement link back to all types of object -->
    <Link
      v-if="route.path.includes('album')"
      solid
      secondary
      raised
      :to="{ name: 'library.albums.detail', params: { id: object.id } }"
    >
      {{ t('components.library.EditForm.button.backToAlbum') }}
    </Link>
  </Alert>
  <Layout
    v-else
    gap-32
  >
    <!-- Previous edits -->

    <edit-list
      :filters="editListFilters"
      :url="mutationsUrl"
      :current-state="currentState"
    >
      <div>
        <!--TODO: Use Section component with conditional headlines and action buttons-->
        <template v-if="showPendingReview">
          {{ t('components.library.EditForm.header.unreviewed') }}
          <Button
            class="right floated"
            secondary
            thin-font
            @click.prevent="showPendingReview = false"
          >
            {{ t('components.library.EditForm.button.showAll') }}
          </Button>
        </template>
        <template v-else>
          {{ t('components.library.EditForm.header.recentEdits') }}
          <Button
            class="right floated"
            secondary
            thin-font
            @click.prevent="showPendingReview = true"
          >
            {{ t('components.library.EditForm.button.showUnreviewed') }}
          </Button>
        </template>
      </div>
      <template #empty-state>
        <empty-state>
          {{ t('components.library.EditForm.empty.suggestEdit') }}
        </empty-state>
      </template>
    </edit-list>

    <!-- Add new edits -->

    <form
      class="ui form"
      style="display: contents;"
      @submit.prevent="submit()"
    >
      <Alert
        v-if="errors.length > 0"
        red
        role="alert"
      >
        <h4 class="header">
          {{ t('components.library.EditForm.header.failure') }}
        </h4>
        <ul class="list">
          <li
            v-for="(error, key) in errors"
            :key="key"
          >
            {{ error }}
          </li>
        </ul>
      </Alert>
      <Alert
        v-if="!canEdit"
        red
      >
        {{ t('components.library.EditForm.message.noPermission') }}
      </Alert>
      <Layout
        v-for="fieldConfig in (values ? config.fields : [])"
        :key="fieldConfig.id"
        stack
        gap-8
        class="ui field"
      >
        <template v-if="fieldConfig.type === 'text'">
          <Input
            :id="fieldConfig.id"
            v-model="values[fieldConfig.id]"
            :type="fieldConfig.inputType || 'text'"
            :required="fieldConfig.required"
            :name="fieldConfig.id"
            :label="fieldConfig.label"
          />
        </template>
        <template v-else-if="fieldConfig.type === 'license'">
          <label :for="fieldConfig.id">{{ fieldConfig.label }}</label>
          <select
            :id="fieldConfig.id"
            ref="license"
            v-model="values[fieldConfig.id]"
            :required="fieldConfig.required"
            class="ui fluid search dropdown"
          >
            <option :value="null">
              {{ t('components.library.EditForm.notApplicable') }}
            </option>
            <option
              v-for="{ code, name } in licenses"
              :key="code"
              :value="code"
            >
              {{ name }}
            </option>
          </select>
        </template>
        <template v-else-if="fieldConfig.type === 'content'">
          <Textarea
            :id="fieldConfig.id"
            v-model="values[fieldConfig.id].text"
            :label="fieldConfig.label"
            initial-lines="3"
          />
        </template>
        <!-- TODO: Style Attachment Input -->
        <template v-else-if="fieldConfig.type === 'attachment'">
          <attachment-input
            :id="fieldConfig.id"
            v-model="values[fieldConfig.id]"
            :initial-value="initialValues[fieldConfig.id]"
            :required="fieldConfig.required"
            :name="fieldConfig.id"
            @delete="values[fieldConfig.id] = initialValues[fieldConfig.id]"
          >
            <span>{{ fieldConfig.label }}</span>
          </attachment-input>
        </template>
        <template v-else-if="fieldConfig.type === 'tags'">
          <!-- TODO: Make Tags work -->
          <Pills
            :id="fieldConfig.id"
            ref="tags"
            :get="model => { values[fieldConfig.id] = model.currents.map(({ label }) => label) }"
            :set="model => ({
              ...model,
              currents: (values[fieldConfig.id] as string[]).map(tag => ({ type: 'custom' as const, label: tag })),
            })"
            :label="fieldConfig.label"
            required="fieldConfig.required"
          >
            <Button
              icon="bi-x"
              form="noop"
              @click.prevent="values[fieldConfig.id] = []"
            >
              {{ t('components.library.EditForm.button.clear') }}
            </Button>
          </Pills>
        </template>
        <Button
          low-height
          secondary
          align-self="end"
          icon="bi-arrow-counterclockwise"
          form="noop"
          :disabled="fieldValuesChanged(fieldConfig.id) ? undefined : true"
          @click.prevent="resetField(fieldConfig.id)"
        >
          {{ t('components.library.EditForm.button.reset') }}
        </Button>
      </Layout>
      <Spacer />
      <Textarea
        id="change-summary"
        v-model="summary"
        name="change-summary"
        initial-lines="3"
        :label="t('components.library.EditForm.label.summary')"
        :placeholder="labels.summaryPlaceholder"
      >
        <Link
          v-if="objectType === 'track'"
          low-height
          secondary
          :to="{ name: 'library.tracks.detail', params: { id: object.id } }"
        >
          {{ t('components.library.EditForm.button.cancel') }}
        </Link>
      </Textarea>
      <Button
        :is-loading="isLoading"
        primary
        :disabled="isLoading || !mutationPayload"
      >
        <span v-if="canEdit">
          {{ t('components.library.EditForm.button.submit') }}
        </span>
        <span v-else>
          {{ t('components.library.EditForm.button.suggest') }}
        </span>
      </Button>
    </form>
  </Layout>
</template>
