<script setup lang="ts">
import type { Report } from '~/types'

import { ref, computed, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'

import axios from 'axios'

import InstancePolicyModal from '~/components/manage/moderation/InstancePolicyModal.vue'
import ReportCategoryDropdown from '~/components/moderation/ReportCategoryDropdown.vue'
import NotesThread from '~/components/manage/moderation/NotesThread.vue'
import NoteForm from '~/components/manage/moderation/NoteForm.vue'
import DangerousButton from '~/components/common/DangerousButton.vue'

import useReportConfigs from '~/composables/moderation/useReportConfigs'
import useErrorHandler from '~/composables/useErrorHandler'
import useMarkdown from '~/composables/useMarkdown'
import useLogger from '~/composables/useLogger'

import Card from '~/components/ui/Card.vue'
import Layout from '~/components/ui/Layout.vue'
import Button from '~/components/ui/Button.vue'
import Link from '~/components/ui/Link.vue'

interface Events {
  (e: 'updated', updating: { type: string }): void
  (e: 'handled', isHandled: boolean): void
}

interface Props {
  initObj: Report
}

const emit = defineEmits<Events>()
const props = defineProps<Props>()

const configs = useReportConfigs()
const logger = useLogger()

const obj = ref(props.initObj)
const summary = useMarkdown(() => obj.value.summary ?? '')

const target = computed(() => obj.value.target
  ? obj.value.target
  : obj.value.target_state._target
)

const targetFields = computed(() => {
  if (!target.value) {
    return []
  }

  const payload = obj.value.target_state
  const fields = configs[target.value.type].moderatedFields
  return fields.map((fieldConfig) => {
    const getValueRepr = fieldConfig.getValueRepr ?? (i => i)
    return {
      id: fieldConfig.id,
      label: fieldConfig.label,
      value: payload[fieldConfig.id],
      repr: getValueRepr(payload[fieldConfig.id]) ?? ''
    }
  })
})

const { t } = useI18n()
const actions = computed(() => {
  if (!target.value) {
    return []
  }

  const typeConfig = configs[target.value.type]
  const deleteUrl = typeConfig.getDeleteUrl?.(target.value)
  return deleteUrl
    ? [{
        label: t('components.manage.moderation.ReportCard.button.delete'),
        modalHeader: t('components.manage.moderation.ReportCard.modal.delete.header'),
        modalContent: t('components.manage.moderation.ReportCard.modal.delete.content.warning'),
        modalConfirmLabel: t('components.manage.moderation.ReportCard.button.confirmDelete'),
        icon: 'x',
        iconColor: 'danger',
        show: (obj: Report) => { return !!obj.target },
        dangerous: true,
        handler: async () => {
          try {
            await axios.delete(deleteUrl)
            logger.info('Target deleted')
            obj.value.target = undefined
            resolveReport(true)
          } catch (error) {
            logger.error('Error while deleting target', error)
            useErrorHandler(error as Error)
          }
        }
      }]
    : []
})

const isLoading = ref(false)
const updating = reactive({ type: false })
const update = async (type: string) => {
  isLoading.value = true
  updating.type = true

  try {
    await axios.patch(`manage/moderation/reports/${obj.value.uuid}/`, { type })
    emit('updated', { type })
  } catch (error) {
    useErrorHandler(error as Error)
  }

  updating.type = false
  isLoading.value = false
}

const store = useStore()
const isCollapsed = ref(true)
const resolveReport = async (isHandled: boolean) => {
  isLoading.value = true

  try {
    await axios.patch(`manage/moderation/reports/${obj.value.uuid}/`, { is_handled: isHandled })
    emit('handled', isHandled)
    obj.value.is_handled = isHandled

    if (isHandled) {
      isCollapsed.value = true
    }

    store.commit('ui/incrementNotifications', {
      type: 'pendingReviewReports',
      count: isHandled ? -1 : 1
    })
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

const handleRemovedNote = (uuid: string) => {
  obj.value.notes = obj.value.notes.filter((note) => note.uuid !== uuid)
}
</script>

<template>
  <Card
    :title="t('components.manage.moderation.ReportCard.link.report', {id: obj.uuid.substring(0, 8)})"
    :width="isCollapsed ? '350px' : ''"
    :full="!isCollapsed"
    solid
    :red="!obj.is_handled && isCollapsed"
    :green="obj.is_handled && isCollapsed"
  >
    <template #topright>
      <collapse-link
        v-model="isCollapsed"
        class="right floated"
      />
    </template>
    <table class="ui very basic unstackable table">
      <tbody>
        <tr>
          <td>
            {{ t('components.manage.moderation.ReportCard.table.report.submittedBy') }}
          </td>
          <td>
            <div v-if="obj.submitter">
              <actor-link
                :admin="true"
                :actor="obj.submitter"
              />
            </div>
            <div v-else-if="obj.submitter_email">
              {{ obj.submitter_email }}
            </div>
          </td>
        </tr>
        <tr>
          <td>
            {{ t('components.manage.moderation.ReportCard.table.report.category') }}
          </td>
          <td>
            <report-category-dropdown
              v-model="obj.type"
              @update:model-value="update($event)"
            >
              &#32;
              <action-feedback :is-loading="updating.type" />
            </report-category-dropdown>
          </td>
        </tr>
        <tr>
          <td>
            {{ t('components.manage.moderation.ReportCard.table.report.creationDate') }}
          </td>
          <td>
            <human-date
              :date="obj.creation_date"
              :icon="true"
            />
          </td>
        </tr>
        <tr>
          <td>
            {{ t('components.manage.moderation.ReportCard.table.status.status') }}
          </td>
          <td v-if="obj.is_handled">
            <span v-if="obj.is_handled">
              <i class="success check icon" />
              {{ t('components.manage.moderation.ReportCard.table.status.resolved') }}
            </span>
          </td>
          <td v-else>
            <i class="danger x icon" />
            {{ t('components.manage.moderation.ReportCard.table.status.unresolved') }}
          </td>
        </tr>
        <tr>
          <td>
            {{ t('components.manage.moderation.ReportCard.table.status.assignedTo') }}
          </td>
          <td>
            <div v-if="obj.assigned_to">
              <actor-link
                :admin="true"
                :actor="obj.assigned_to"
              />
            </div>
            <span v-else>
              {{ t('components.manage.moderation.ReportCard.notApplicable') }}
            </span>
          </td>
        </tr>
        <tr>
          <td>
            {{ t('components.manage.moderation.ReportCard.table.status.resolutionDate') }}
          </td>
          <td>
            <human-date
              v-if="obj.handled_date"
              :date="obj.handled_date"
              :icon="true"
            />
            <span v-else>
              {{ t('components.manage.moderation.ReportCard.notApplicable') }}
            </span>
          </td>
        </tr>
        <tr>
          <td>
            {{ t('components.manage.moderation.ReportCard.table.status.internalNotes') }}
          </td>
          <td>
            <i class="comment icon" />
            {{ obj.notes.length }}
          </td>
        </tr>
      </tbody>
    </table>
    <template
      v-if="!isCollapsed"
    >
      <Layout flex>
        <div class="column">
          <h3>
            {{ t('components.manage.moderation.ReportCard.header.message') }}
          </h3>
          <expandable-div
            v-if="summary"
            class="summary"
            :content="obj.summary"
          >
            <sanitized-html :html="summary" />
          </expandable-div>
        </div>
        <aside class="column">
          <h3>
            {{ t('components.manage.moderation.ReportCard.header.reportedObject') }}
          </h3>
          <Alert
            v-if="!obj.target"
            red
          >
            {{ t('components.manage.moderation.ReportCard.warning.objectDeleted') }}
          </Alert>
          <Layout flex>
            <Link
              v-if="target && configs[target.type].urls.getDetail"
              solid
              secondary
              icon="bi-eye"
              low-height
              :to="configs[target.type].urls.getDetail?.(obj.target_state) ?? '/'"
            >
              {{ t('components.manage.moderation.ReportCard.link.publicPage') }}
            </Link>
            <Link
              v-if="target && configs[target.type].urls.getAdminDetail"
              solid
              secondary
              icon="bi-wrench"
              low-height
              :to="configs[target.type].urls.getAdminDetail?.(obj.target_state) ?? '/'"
            >
              {{ t('components.manage.moderation.ReportCard.link.moderation') }}
            </Link>
          </Layout>
          <table class="ui very basic unstackable table">
            <tbody>
              <tr v-if="target">
                <td>
                  {{ t('components.manage.moderation.ReportCard.table.object.type') }}
                </td>
                <td colspan="2">
                  <i :class="[configs[target.type].icon, 'icon']" />
                  {{ configs[target.type].label }}
                </td>
              </tr>
              <tr v-if="obj.target_owner && (!target || target.type !== 'account')">
                <td>
                  {{ t('components.manage.moderation.ReportCard.table.object.owner') }}
                </td>
                <td>
                  <actor-link
                    :admin="true"
                    :actor="obj.target_owner"
                  />
                </td>
                <td>
                  <instance-policy-modal
                    v-if="!obj.target_owner.is_local"
                    class="right floated mini basic"
                    type="actor"
                    :target="obj.target_owner.full_username"
                  />
                </td>
              </tr>
              <tr v-if="target && target.type === 'account'">
                <td>
                  {{ t('components.manage.moderation.ReportCard.table.object.account') }}
                </td>
                <td>
                  <actor-link
                    :admin="true"
                    :actor="obj.target_owner"
                  />
                </td>
                <td>
                  <instance-policy-modal
                    v-if="!obj.target_owner?.is_local"
                    class="right floated mini basic"
                    type="actor"
                    :target="obj.target_owner?.full_username ?? ''"
                  />
                </td>
              </tr>
              <tr v-if="obj.target_state.is_local">
                <td>
                  {{ t('components.manage.moderation.ReportCard.table.object.domain') }}
                </td>
                <td colspan="2">
                  <i class="home icon" />
                  {{ t('components.manage.moderation.ReportCard.table.object.local') }}
                </td>
              </tr>
              <tr v-else-if="obj.target_state.domain">
                <td>
                  <Link :to="{name: 'manage.moderation.domains.detail', params: { id: obj.target_state.domain }}">
                    {{ t('components.manage.moderation.ReportCard.table.object.domain') }}
                  </Link>
                </td>
                <td>
                  {{ obj.target_state.domain }}
                </td>
                <td>
                  <instance-policy-modal
                    class="right floated mini basic"
                    type="domain"
                    :target="obj.target_state.domain"
                  />
                </td>
              </tr>
              <tr
                v-for="field in targetFields"
                :key="field.id"
              >
                <td>{{ field.label }}</td>
                <td
                  v-if="field.repr"
                  colspan="2"
                >
                  {{ field.repr }}
                </td>
                <td
                  v-else
                  colspan="2"
                >
                  {{ t('components.manage.moderation.ReportCard.notApplicable') }}
                </td>
              </tr>
            </tbody>
          </table>
        </aside>
      </Layout>
      <h3>
        {{ t('components.manage.moderation.ReportCard.header.notes') }}
      </h3>
      <notes-thread
        :notes="obj.notes"
        @deleted="handleRemovedNote($event)"
      />
      <note-form
        :target="{type: 'report', uuid: obj.uuid}"
        @created="obj.notes.push($event)"
      />
      <h3>
        {{ t('components.manage.moderation.ReportCard.header.actions') }}
      </h3>
      <Layout flex>
        <Button
          v-if="obj.is_handled === false"
          :class="{loading: isLoading}"
          primary
          icon="bi-check"
          @click="resolveReport(true)"
        >
          {{ t('components.manage.moderation.ReportCard.button.resolve') }}
        </Button>
        <Button
          v-if="obj.is_handled === true"
          :class="{loading: isLoading}"
          secondary
          icon="bi-arrow-counterclockwise"
          @click="resolveReport(false)"
        >
          {{ t('components.manage.moderation.ReportCard.button.unresolve') }}
        </Button>
        <template
          v-for="action in actions"
          :key="action.label"
        >
          <dangerous-button
            v-if="action.dangerous && action.show(obj)"
            :is-loading="isLoading"
            :action="action.handler"
            :title="action.modalHeader"
            :icon="`${action.iconColor} ${action.icon}`"
          >
            {{ action.label }}
            <template #content>
              {{ action.modalContent }}
            </template>
            <template #confirm>
              {{ action.modalConfirmLabel }}
            </template>
          </dangerous-button>
        </template>
      </Layout>
    </template>
  </Card>
</template>
