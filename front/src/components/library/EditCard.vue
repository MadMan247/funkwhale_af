<script setup lang="ts">
import type { ConfigField } from '~/composables/moderation/useEditConfigs'
import type { Review, ReviewState, ReviewStatePayload } from '~/types'
import type { Change } from 'diff'

import { diffWordsWithSpace } from 'diff'
import { useRouter } from 'vue-router'
import { computed, ref } from 'vue'
import { useStore } from '~/store'
import { useI18n } from 'vue-i18n'

import axios from 'axios'

import useEditConfigs from '~/composables/moderation/useEditConfigs'
import useErrorHandler from '~/composables/useErrorHandler'

import DangerousButton from '~/components/common/DangerousButton.vue'

import Button from '~/components/ui/Button.vue'
import Card from '~/components/ui/Card.vue'
import Spacer from '~/components/ui/Spacer.vue'

interface Events {
  (e: 'approved', isApproved: boolean): void
  (e: 'deleted'): void
}

interface Props {
  obj: Review
  currentState?: ReviewState
}

const { t } = useI18n()

const emit = defineEmits<Events>()
const props = withDefaults(defineProps<Props>(), {
  currentState: () => ({})
})

const configs = useEditConfigs()
const router = useRouter()
const store = useStore()

const canApprove = computed(() => !props.obj.is_applied && store.state.auth.availablePermissions.library)
const canDelete = computed(() => {
  if (props.obj.is_applied || props.obj.is_approved) return false
  if (!store.state.auth.authenticated) return false

  return props.obj.created_by.full_username === store.state.auth.fullUsername
    || store.state.auth.availablePermissions.library
})

const previousState = computed(() => props.obj.is_applied
  // mutation was applied, we use the previous state that is stored
  // on the mutation itself
  ? props.obj.previous_state
  // mutation is not applied yet, so we use the current state that was
  // passed to the component, if any
  : props.currentState
)

const detailUrl = computed(() => {
  if (!props.obj.target) return ''

  const name = props.obj.target.type === 'track'
    ? 'library.tracks.edit.detail'
    : props.obj.target.type === 'album'
      ? 'library.albums.edit.detail'
      : props.obj.target.type === 'artist'
        ? 'library.artists.edit.detail'
        : undefined

  return router.resolve({
    name,
    params: {
      id: props.obj.target.id,
      editId: props.obj.uuid
    }
  }).href
})

const updatedFields = computed(() => {
  if (!props.obj?.target) return []

  const payload = props.obj.payload
  const fields = Object.keys(payload)

  const state = previousState.value

  return fields.map((id) => {
    const config = configs[props.obj.target!.type].fields.find((field) => id === field.id)
    const getValueRepr = config?.getValueRepr ?? (v => v)

    const result = {
      id,
      config,
      new: payload[id],
      newRepr: getValueRepr(payload[id]) ?? '',
      old: undefined,
      oldRepr: '',
      diff: []
    } as {
      id: string
      config: ConfigField
      old?: ReviewStatePayload
      new: ReviewStatePayload
      oldRepr: string
      newRepr: string
      diff: Change[]
    }

    if (state?.[id]) {
      const oldState = state[id]
      result.old = oldState
      result.oldRepr = getValueRepr('value' in oldState
        ? oldState.value
        : oldState
      ) ?? ''

      // we compute the diffs between the old and new values
      result.diff = diffWordsWithSpace(result.oldRepr, result.newRepr)
    }

    return result
  })
})

const isLoading = ref(false)
const remove = async () => {
  isLoading.value = true

  try {
    await axios.delete(`mutations/${props.obj.uuid}/`)
    emit('deleted')
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

const approve = async (approved: boolean) => {
  const url = approved
    ? `mutations/${props.obj.uuid}/approve/`
    : `mutations/${props.obj.uuid}/reject/`

  isLoading.value = true

  try {
    await axios.post(url)
    emit('approved', approved)
    store.commit('ui/incrementNotifications', { count: -1, type: 'pendingReviewEdits' })
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

const alertProps = computed(() => {
  return {
    green: props.obj.is_approved && props.obj.is_applied || undefined,
    red: props.obj.is_approved === false || undefined,
    yellow: props.obj.is_applied === false || undefined
  } as const
})
</script>

<template>
  <Card
    :alert-props="alertProps"
    :to="detailUrl"
    :title="t('components.library.EditCard.header.modification', {id: obj.uuid.substring(0, 8)})"
  >
    <div class="content">
      <div class="meta">
        <router-link
          v-if="obj.target && obj.target.type === 'track'"
          :to="{ name: 'library.tracks.detail', params: { id: obj.target.id } }"
          :class="/* TODO: find out: what is isInteractive? */ undefined"
        >
          <i class="bi bi-file-music-fill" />
          {{ t('components.library.EditCard.link.track', {id: obj.target.id, name: obj.target.repr}) }}
        </router-link>
      </div>
    </div>
    <div
      v-if="obj.summary"
      class="content"
    >
      {{ obj.summary }}
    </div>

    <template #alert>
      <span class="right floated">
        <span v-if="obj.is_approved && obj.is_applied">
          <i class="green bi bi-check" />
          {{ t('components.library.EditCard.status.applied') }}
        </span>
        <span v-else-if="obj.is_approved">
          <i class="green bi bi-check" />
          {{ t('components.library.EditCard.status.approved') }}
        </span>
        <span v-else-if="obj.is_approved === null">
          <i class="yellow bi bi-hourglass" />
          {{ t('components.library.EditCard.status.pending') }}
        </span>
        <span v-else-if="obj.is_approved === false">
          <i class="destructive bi bi-x" />
          {{ t('components.library.EditCard.status.rejected') }}
        </span>
      </span>
      <table
        v-if="obj.type === 'update'"
      >
        <thead>
          <tr>
            <th>
              {{ t('components.library.EditCard.table.update.header.field') }}
            </th>
            <th>
              {{ t('components.library.EditCard.table.update.header.oldValue') }}
            </th>
            <th>
              {{ t('components.library.EditCard.table.update.header.newValue') }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="field in updatedFields"
            :key="field.id"
          >
            <td>{{ field.id }}</td>

            <td v-if="field.diff">
              <template v-if="field.config?.type === 'attachment' && field.oldRepr">
                <img
                  class="image"
                  alt=""
                  :src="store.getters['instance/absoluteUrl'](`api/v1/attachments/${field.oldRepr}/proxy?next=medium_square_crop`)"
                >
              </template>
              <template v-else>
                <span
                  v-for="(part, key) in field.diff.filter(p => !p.added)"
                  :key="key"
                  :class="['diff', {removed: part.removed}]"
                >
                  {{ part.value }}
                </span>
              </template>
            </td>
            <td v-else>
              {{ t('components.library.EditCard.table.update.notApplicable') }}
            </td>

            <td
              v-if="field.diff"
              :title="field.newRepr"
            >
              <template v-if="field.config?.type === 'attachment' && field.newRepr">
                <img
                  class="ui image"
                  alt=""
                  :src="store.getters['instance/absoluteUrl'](`api/v1/attachments/${field.newRepr}/proxy?next=medium_square_crop`)"
                >
              </template>
              <template v-else>
                <span
                  v-for="(part, key) in field.diff.filter(p => !p.removed)"
                  :key="key"
                  :class="['diff', {added: part.added}]"
                >
                  {{ part.value }}
                </span>
              </template>
            </td>
            <td
              v-else
              :title="field.newRepr"
            >
              <template v-if="field.config?.type === 'attachment' && field.newRepr">
                <img
                  class="ui image"
                  alt=""
                  :src="store.getters['instance/absoluteUrl'](`api/v1/attachments/${field.newRepr}/proxy?next=medium_square_crop`)"
                >
              </template>
              <template v-else>
                {{ field.newRepr }}
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </template>

    <div
      v-if="obj.created_by"
      class="extra content"
    >
      <Spacer :size="8" />
      <actor-link :actor="obj.created_by" />
    </div>

    <template #footer>
      <human-date
        :date="obj.creation_date"
        :icon="true"
      />
    </template>

    <template
      v-if="canDelete || canApprove"
      #action
    >
      <Button
        v-if="canApprove && obj.is_approved !== true"
        primary
        :is-loading="isLoading"
        @click="approve(true)"
      >
        {{ t('components.library.EditCard.button.approve') }}
      </Button>
      <Button
        v-if="canApprove && obj.is_approved === null"
        destructive
        :is-loading="isLoading"
        @click="approve(false)"
      >
        {{ t('components.library.EditCard.button.reject') }}
      </Button>
      <!--TODO: Make Dangerous Button hand through isLoading prop -->
      <dangerous-button
        v-if="canDelete"
        :is-loading="isLoading"
        :action="remove"
        :title="t('components.library.EditCard.modal.delete.header')"
      >
        {{ t('components.library.EditCard.button.delete') }}
        <template #content>
          {{ t('components.library.EditCard.modal.content.warning') }}
        </template>
        <template #confirm>
          {{ t('components.library.EditCard.button.delete') }}
        </template>
      </dangerous-button>
    </template>
  </Card>
</template>

<style scoped>
table {
  width: 100%;
  font-size: 12px;

  th, td {
      padding: 8px;
      text-align: left;
    }
  .image {
    width: 100%;
  }
}
</style>
