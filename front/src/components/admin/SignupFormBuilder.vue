<script setup lang="ts">
import type { Form } from '~/types'

import SignupForm from '~/components/auth/SignupForm.vue'
import Button from '~/components/ui/Button.vue'
import Layout from '~/components/ui/Layout.vue'
import Nav from '~/components/ui/Nav.vue'
import Table from '~/components/ui/Table.vue'
import Input from '~/components/ui/Input.vue'
import Select from '~/components/ui/Select.vue'
import Toggle from '~/components/ui/Toggle.vue'

import { useVModel } from '@vueuse/core'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { arrayMove } from '~/utils'

interface Events {
  (e: 'update:modelValue', value: Form): void
}

interface Props {
  modelValue: Form
  signupApprovalEnabled?: boolean
}

const emit = defineEmits<Events>()
const props = withDefaults(defineProps<Props>(), {
  signupApprovalEnabled: false
})

const value = useVModel(props, 'modelValue', emit, { deep: true })

const maxFields = ref(10)

const { t } = useI18n()
const labels = computed(() => ({
  delete: t('components.admin.SignupFormBuilder.label.delete'),
  up: t('components.admin.SignupFormBuilder.label.moveUp'),
  down: t('components.admin.SignupFormBuilder.label.moveDown')
}))

if (!value.value?.fields) {
  value.value = {
    help_text: {
      text: '',
      content_type: 'text/markdown'
    },
    fields: []
  }
}

const addField = () => {
  value.value.fields.push({
    label: t('components.admin.SignupFormBuilder.label.additionalField', { fieldNumber: value.value.fields.length + 1 }),
    required: true,
    input_type: 'short_text'
  })
}

const remove = (idx: number) => {
  value.value.fields.splice(idx, 1)
}

const move = (idx: number, increment: number) => {
  if (idx + increment >= value.value.fields.length) return
  if (idx === 0 && increment < 0) return
  arrayMove(value.value.fields, idx, idx + increment)
}

const inputTypeOptions = ref({
  short_text: t('components.admin.SignupFormBuilder.table.additionalFields.type.short'),
  long_text: t('components.admin.SignupFormBuilder.table.additionalFields.type.long')
})

const navTabs = computed(() => [
  { title: t('components.admin.SignupFormBuilder.button.edit'), name: 'edit' },
  { title: t('components.admin.SignupFormBuilder.button.preview'), name: 'preview' }
])
</script>

<template>
  <Layout stack>
    <Nav
      v-slot="{ tabpanels }"
      v-model="navTabs"
      tab-query-field="tab"
    >
      <Layout
        v-if="tabpanels[0]?.isActive"
        stack
      >
        <Layout flex>
          <label for="help-text">
            {{ t('components.admin.SignupFormBuilder.label.helpText') }}
          </label>
          <span>{{ t('components.admin.SignupFormBuilder.help.helpText') }}</span>
        </Layout>
        <ContentForm
          v-if="value.help_text"
          v-model="value.help_text.text"
          field-id="help-text"
          :permissive="true"
        />

        <Layout flex>
          <label>
            {{ t('components.admin.SignupFormBuilder.label.additionalFields') }}
          </label>
          <span>
            {{ t('components.admin.SignupFormBuilder.help.additionalFields') }}
          </span>
        </Layout>
        <Table
          v-if="value.fields?.length > 0"
          :grid-template-columns="['auto', '180px', '80px', '120px']"
          is-table
        >
          <template #header>
            <th>
              {{ t('components.admin.SignupFormBuilder.table.additionalFields.header.label') }}
            </th>
            <th>
              {{ t('components.admin.SignupFormBuilder.table.additionalFields.header.type') }}
            </th>
            <th>
              {{ t('components.admin.SignupFormBuilder.table.additionalFields.header.required') }}
            </th>
            <th><span class="visually-hidden">{{ t('components.admin.SignupFormBuilder.table.additionalFields.header.actions') }}</span></th>
          </template>

          <template
            v-for="(field, fieldIdx) in value.fields"
            :key="fieldIdx"
          >
            <Input
              v-model="field.label"
              type="text"
              required
            />
            <Select
              v-model:current="field.input_type"
              :options="inputTypeOptions"
            />
            <Toggle
              v-model="field.required"
            />
            <Layout
              flex
              no-gap
            >
              <Button
                icon="bi-arrow-up"
                :disabled="fieldIdx === 0"
                :title="labels.up"
                ghost
                min-content
                @click="move(fieldIdx, -1)"
              />
              <Button
                icon="bi-arrow-down"
                :disabled="fieldIdx >= value.fields.length - 1"
                :title="labels.down"
                ghost
                min-content
                @click="move(fieldIdx, 1)"
              />
              <Button
                icon="bi-x"
                :title="labels.delete"
                ghost
                min-content
                @click="remove(fieldIdx)"
              />
            </Layout>
          </template>
        </Table>
        <Button
          v-if="value.fields?.length < maxFields"
          secondary
          icon="bi-plus"
          @click.stop.prevent="addField"
        >
          {{ t('components.admin.SignupFormBuilder.button.add') }}
        </Button>
      </Layout>
      <Layout
        v-if="tabpanels[1]?.isActive"
        stack
      >
        <SignupForm
          :customization="value"
          :signup-approval-enabled="signupApprovalEnabled"
          :fetch-description-html="true"
        />
      </Layout>
    </Nav>
  </Layout>
</template>
