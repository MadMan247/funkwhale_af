<script setup lang="ts">
import type { Library, Plugin, BackendError } from '~/types'

import axios from 'axios'
import { clone } from 'lodash-es'
import useMarkdown, { useMarkdownRaw } from '~/composables/useMarkdown'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

import Layout from '~/components/ui/Layout.vue'
import Input from '~/components/ui/Input.vue'
import Toggle from '~/components/ui/Toggle.vue'
import Alert from '~/components/ui/Alert.vue'
import Button from '~/components/ui/Button.vue'

interface Props {
  plugin: Plugin
  libraries: Library[]
}

const { t } = useI18n()

const props = defineProps<Props>()

const description = useMarkdown(() => props.plugin.description ?? '')
const enabled = ref(props.plugin.enabled)
const values = clone(props.plugin.values ?? {})

const errors = ref([] as string[])
const isLoading = ref(false)
const submit = async () => {
  isLoading.value = true
  errors.value = []

  try {
    await axios.post(`plugins/${props.plugin.name}/${enabled.value ? 'enable' : 'disable'}`)
    await axios.post(`plugins/${props.plugin.name}`, values)
  } catch (error) {
    errors.value = (error as BackendError).backendErrors
  }

  isLoading.value = false
}

const scan = async () => {
  isLoading.value = true
  errors.value = []

  try {
    await axios.post(`plugins/${props.plugin.name}/scan`, values)
  } catch (error) {
    errors.value = (error as BackendError).backendErrors
  }

  isLoading.value = false
}

const submitAndScan = async () => {
  await submit()
  await scan()
}
</script>

<template>
  <Layout
    form
    :class="['ui form', {loading: isLoading}]"
    @submit.prevent="submit"
  >
    <h3>{{ plugin.label }}</h3>
    <sanitized-html
      v-if="plugin.description"
      :html="description"
    />
    <template v-if="plugin.homepage">
      <a
        :href="plugin.homepage"
        target="_blank"
      >
        <i class="external icon" />
        {{ t('components.auth.Plugin.link.documentation') }}
      </a>
    </template>
    <Alert
      v-if="errors.length > 0"
      red
    >
      <h4 class="header">
        {{ t('components.auth.Plugin.header.failure') }}
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
    <div class="field">
      <Toggle
        v-model="enabled"
        big
        :label="t('components.auth.Plugin.label.pluginEnabled')"
      />
    </div>
    <div
      v-if="plugin.source"
      class="field"
    >
      <label for="plugin-library">{{ t('components.auth.Plugin.label.library') }}</label>
      <select
        id="plugin-library"
        v-model="values['library']"
      >
        <option
          v-for="l in libraries"
          :key="l.uuid"
          :value="l.uuid"
        >
          {{ l.name }}
        </option>
      </select>
      <div>
        {{ t('components.auth.Plugin.description.library') }}
      </div>
    </div>
    <template v-if="(plugin.conf?.length ?? 0) > 0">
      <template
        v-for="field in plugin.conf"
        :key="field.name"
      >
        <div
          v-if="field.type === 'text'"
          class="field"
        >
          <Input
            :id="`plugin-${field.name}`"
            v-model="values[field.name]"
            :label="field.label || field.name"
            type="text"
          />
          <sanitized-html
            v-if="field.help"
            :html="useMarkdownRaw(field.help)"
          />
        </div>
        <div
          v-if="field.type === 'long_text'"
          class="field"
        >
          <textarea
            :id="`plugin-${field.name}`"
            v-model="values[field.name]"
            :label="field.label || field.name"
            type="text"
            rows="5"
          />
          <sanitized-html
            v-if="field.help"
            :html="useMarkdownRaw(field.help)"
          />
        </div>
        <div
          v-if="field.type === 'url'"
          class="field"
        >
          <Input
            :id="`plugin-${field.name}`"
            v-model="values[field.name]"
            :label="field.label || field.name"
            type="url"
          />
          <sanitized-html
            v-if="field.help"
            :html="useMarkdownRaw(field.help)"
          />
        </div>
        <div
          v-if="field.type === 'password'"
          class="field"
        >
          <Input
            :id="`plugin-${field.name}`"
            v-model="values[field.name]"
            :label="field.label || field.name"
            password
          />
          <sanitized-html
            v-if="field.help"
            :html="useMarkdownRaw(field.help)"
          />
        </div>
        <div
          v-if="field.type === 'boolean'"
          class="field"
        >
          <Toggle
            v-model="values[field.name]"
            :label="field.label || field.name"
          />
        </div>
      </template>
    </template>
    <Button
      type="submit"
      primary
      :class="[{'loading': isLoading}]"
    >
      {{ t('components.auth.Plugin.button.save') }}
    </Button>
    <Button
      v-if="plugin.source"
      primary
      :class="[{'loading': isLoading}]"
      @click.prevent="submitAndScan"
    >
      {{ t('components.auth.Plugin.button.scan') }}
    </Button>
  </Layout>
</template>
