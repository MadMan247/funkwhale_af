<script setup lang="ts">
import type { BackendError, SettingsGroup, SettingsDataEntry, FunctionRef, Form, SettingsField } from '~/types'
import axios from 'axios'
import SignupFormBuilder from '~/components/admin/SignupFormBuilder.vue'
import useFormData from '~/composables/useFormData'
import { ref, computed, reactive } from 'vue'
import { useStore } from '~/store'
import useLogger from '~/composables/useLogger'
import { useI18n } from 'vue-i18n'

import Section from '~/components/ui/Section.vue'
import Layout from '~/components/ui/Layout.vue'
import Toggle from '~/components/ui/Toggle.vue'
import Input from '~/components/ui/Input.vue'
import Alert from '~/components/ui/Alert.vue'
import Button from '~/components/ui/Button.vue'
import Spacer from '~/components/ui/Spacer.vue'

const { t } = useI18n()

interface Props {
  group: SettingsGroup
  settingsData: SettingsDataEntry[]
}

const props = defineProps<Props>()

const values = reactive({} as Record<string, unknown | Form | string>)
const result = ref<boolean | null>(null)
const errors = ref([] as string[])

const logger = useLogger()
const store = useStore()

// TODO (wvffle): Use VueUse
const fileRefs = reactive({} as Record<string, HTMLInputElement>)
const setFileRef = (identifier: string) => (el: FunctionRef) => {
  logger.debug(el)
  fileRefs[identifier] = el as HTMLInputElement
}

const settings = computed(() => {
  const byIdentifier = props.settingsData.reduce((acc, entry) => {
    acc[entry.identifier] = entry
    return acc
  }, {} as Record<string, SettingsDataEntry>)

  return props.group.settings.map(entry => ({
    ...byIdentifier[entry.name],
    fieldType: entry.fieldType,
    fieldParams: entry.fieldParams || {}
  } as SettingsDataEntry & Pick<SettingsField, 'fieldType' | 'fieldParams'>))
})

const fileSettings = computed(() => settings.value.filter(setting => setting.field?.widget.class === 'ImageWidget'))

for (const setting of settings.value) {
  if (setting.identifier != null) {
    values[setting.identifier] = setting.value
  }
}

const isLoading = ref(false)
const save = async () => {
  errors.value = []
  result.value = null

  let postData: unknown = values
  let contentType = 'application/json'

  if (fileSettings.value.length > 0) {
    const fileSettingsIDs = fileSettings.value.map((setting) => setting.identifier)
    const data: Record<string, string | File> = {}
    for (const setting of settings.value) {
      if (setting.identifier == null) {
        return data
      }

      if (fileSettingsIDs.includes(setting.identifier)) {
        const input = fileRefs[setting.identifier]
        const { files } = (input as HTMLInputElement)

        logger.debug('ref', input, files)

        if (files && files.length > 0 && files[0] != null) {
          data[setting.identifier] = files[0]
        }
      } else {
        data[setting.identifier] = values[setting.identifier] as string
      }
    }

    contentType = 'multipart/form-data'
    postData = useFormData(data)
  }

  try {
    const response = await axios.post('instance/admin/settings/bulk/', postData, {
      headers: { 'Content-Type': contentType }
    })

    result.value = true
    for (const setting of response.data) {
      values[setting.identifier] = setting.value
    }

    await store.dispatch('instance/fetchSettings')
  } catch (error) {
    errors.value = (error as BackendError).backendErrors
  }

  isLoading.value = false
}
</script>

<template>
  <!-- TODO: type the different values in `settings` (use generics) -->
  <!-- eslint-disable vue/valid-v-model -->
  <Section
    align-left
    :h2="group.label"
    large-section-heading
  >
    <form
      :id="group.id"
      class="ui form component-settings-group"
      style="grid-column: 1 / -1;"
      @submit.prevent="save"
    >
      <Spacer :size="16" />
      <div
        v-for="(setting, key) in settings"
        :key="key"
        :class="[$style.field, 'ui', 'field']"
      >
        <template v-if="setting.field.widget.class !== 'CheckboxInput'">
          <label :for="setting.identifier">{{ setting.verbose_name }}</label>
          <p v-if="setting.help_text">
            {{ setting.help_text }}
          </p>
        </template>
        <content-form
          v-if="setting.fieldType === 'markdown'"
          v-bind="setting.fieldParams"
          v-model="values[setting.identifier]"
        />
        <signup-form-builder
          v-else-if="setting.fieldType === 'formBuilder'"
          v-model="values[setting.identifier] as Form"
          :signup-approval-enabled="!!values.moderation__signup_approval_enabled"
        />
        <Input
          v-else-if="setting.field.widget.class === 'PasswordInput'"
          v-model="values[setting.identifier] as string"
          password
          type="password"
          class="ui input"
        />
        <Input
          v-else-if="setting.field.widget.class === 'TextInput'"
          v-model="values[setting.identifier] as string"
          type="text"
          class="ui input"
        />
        <Input
          v-else-if="setting.field.class === 'IntegerField'"
          v-model.number="values[setting.identifier] as number"
          type="number"
          class="ui input"
        />
        <textarea
          v-else-if="setting.field.widget.class === 'Textarea'"
          v-model="values[setting.identifier] as string"
          type="text"
          class="ui input"
        />
        <!-- eslint-enable vue/valid-v-model -->
        <div
          v-else-if="setting.field.widget.class === 'CheckboxInput'"
        >
          <Toggle
            v-model="values[setting.identifier] as boolean"
            big
            :label="setting.verbose_name"
          />
          <Spacer :size="8" />
          <p v-if="setting.help_text">
            {{ setting.help_text }}
          </p>
        </div>
        <select
          v-else-if="setting.field.class === 'MultipleChoiceField'"
          :id="setting.identifier"
          v-model="values[setting.identifier]"
          multiple
          class="ui search selection dropdown"
          style="height: 150px;"
        >
          <option
            v-for="v in setting.additional_data?.choices"
            :key="v[0]"
            :value="v[0]"
          >
            {{ v[1] }}
          </option>
        </select>
        <select
          v-else-if="setting.field.class === 'ChoiceField'"
          :id="setting.identifier"
          v-model="values[setting.identifier]"
          class="ui search selection dropdown"
        >
          <option
            v-for="v in setting.additional_data?.choices"
            :key="v[0]"
            :value="v[0]"
          >
            {{ v[1] }}
          </option>
        </select>
        <div v-else-if="setting.field.widget.class === 'ImageWidget'">
          <!-- TODO: Implement image input https://dev.funkwhale.audio/funkwhale/funkwhale/-/issues/2512 -->

          <!-- @vue-ignore -->
          <Input
            :id="setting.identifier"
            :ref="setFileRef(setting.identifier)"
            type="file"
          />

          <div v-if="values[setting.identifier]">
            <h3 class="ui header">
              {{ t('components.admin.SettingsGroup.header.image') }}
            </h3>
            <img
              v-if="values[setting.identifier]"
              class="ui image"
              alt=""
              :src="store.getters['instance/absoluteUrl'](values[setting.identifier])"
            >
          </div>
        </div>
        <Spacer />
      </div>
      <Layout flex>
        <Spacer grow />
        <Button
          type="submit"
          :class="[{'loading': isLoading}]"
          primary
        >
          {{ t('components.admin.SettingsGroup.button.save') }}
        </Button>
      </Layout>
      <Spacer />
      <Alert
        v-if="errors.length > 0"
        red
      >
        <h4 class="header">
          {{ t('components.admin.SettingsGroup.header.error', {label: group.label}) }}
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
        v-if="result"
        green
      >
        {{ t('components.admin.SettingsGroup.message.success') }}
      </Alert>
    </form>
  </Section>
  <hr :class="$style.separator">
  <Spacer size-64 />
  <!-- eslint-enable vue/valid-v-model -->
</template>

<style module>
  .field > div {
    display: flex;
    flex-direction: column;
  }
  .separator:last-of-type {
    display: none;
  }
</style>
