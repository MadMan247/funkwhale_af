<script setup lang="ts">
import type { ContentCategory, Channel, BackendError } from '~/types'
import type { paths, components } from '~/generated/types'

import { slugify } from 'transliteration'
import { reactive, computed, ref, watchEffect, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDataStore } from '~/ui/stores/data'
import { useStore } from '~/store'

import axios from 'axios'
import AttachmentInput from '~/components/common/AttachmentInput.vue'
import ExternalLinksBuilder from '~/components/common/ExternalLinksBuilder.vue'

import Layout from '~/components/ui/Layout.vue'
import Alert from '~/components/ui/Alert.vue'
import Input from '~/components/ui/Input.vue'
import Textarea from '~/components/ui/Textarea.vue'
import Pills from '~/components/ui/Pills.vue'
import Loader from '../ui/Loader.vue'

interface Props {
  object?: Channel | null
  step?: number
}

interface ChannelMetadata {
  language?: string
  itunes_category?: string
  itunes_subcategory?: string | null
  owner_email?: string
  owner_name?: string
}

const emit = defineEmits<{
  category: [contentCategory: ContentCategory]
  submittable: [value: boolean]
  loading: [value: boolean]
  errored: [errors: string[]]
  created: [channel: Channel]
  updated: [channel: Channel]
}>()
const props = withDefaults(defineProps<Props>(), {
  object: null,
  step: 1
})

const { t } = useI18n()
const dataStore = useDataStore()
const store = useStore()

const newValues = reactive({
  name: props.object?.artist?.name ?? '',
  username: props.object?.actor.preferred_username ?? '',
  tags: props.object?.artist?.tags ?? [] as string[],
  description: props.object?.artist?.description?.text ?? '',
  cover: props.object?.artist?.cover?.uuid ?? null,
  content_category: props.object?.artist?.content_category ?? 'podcast',
  metadata: {
    language: (props.object?.metadata as ChannelMetadata)?.language ?? '',
    itunes_category: (props.object?.metadata as ChannelMetadata)?.itunes_category ?? '',
    itunes_subcategory: (props.object?.metadata as ChannelMetadata)?.itunes_subcategory ?? null,
    owner_email: (props.object?.metadata as ChannelMetadata)?.owner_email ?? '',
    owner_name: (props.object?.metadata as ChannelMetadata)?.owner_name ?? ''
  },
  links: props.object?.artist.links ?? [] as components['schemas']['Link'][]
})

// If props has an object, then this form edits, else it creates
// TODO: rename to `process : 'creating' | 'editing'`
const creating = computed(() => props.object === null)
const categoryChoices = computed(() => [
  {
    value: 'podcast',
    label: t('components.audio.ChannelForm.label.podcast'),
    helpText: t('components.audio.ChannelForm.help.podcast')
  },
  {
    value: 'music',
    label: t('components.audio.ChannelForm.label.discography'),
    helpText: t('components.audio.ChannelForm.help.discography')
  }
])

interface ITunesCategory {
  value: string
  label: string
  children: []
}

interface MetadataChoices {
  itunes_category?: ITunesCategory[] | null
  language: {
    value: string
    label: string
  }[]
}

const metadataChoices = ref({ itunes_category: null } as MetadataChoices)
const itunesSubcategories = computed(() => {
  for (const element of metadataChoices.value.itunes_category ?? []) {
    // TODO: Backend: Define schema for `metadata` field
    if (element.value === newValues.metadata.itunes_category) {
      return element.children ?? []
    }
  }

  return []
})

const labels = computed(() => ({
  namePlaceholder: t('components.audio.ChannelForm.placeholder.name'),
  usernamePlaceholder: t('components.audio.ChannelForm.placeholder.username')
}))

const submittable = computed(() => !!(
  newValues.content_category === 'podcast'
    ? newValues.name && newValues.username && newValues.metadata.itunes_category && newValues.metadata.language
    : newValues.name && newValues.username
))

watch(() => newValues.name, (name) => {
  if (creating.value) {
    newValues.username = slugify(name)
  }
})

watch(() => newValues.metadata.itunes_category, () => {
  newValues.metadata.itunes_subcategory = null
})

const isLoading = ref(false)
const errors = ref([] as string[])
const externalLinksBuilderRef = ref()

const showExternalLinks = computed(() => {
  return store.state.instance.settings.music?.display_external_links?.value ?? true
})

// @ts-expect-error Re-check emits
watchEffect(() => emit('category', newValues.content_category))
watchEffect(() => emit('loading', isLoading.value))
watchEffect(() => emit('submittable', submittable.value))

// TODO (wvffle): Add loader / Use Suspense
const fetchMetadataChoices = async () => {
  try {
    const response = await axios.get<paths['/api/v2/channels/metadata-choices/']['get']['responses']['200']['content']['application/json']>('channels/metadata-choices/')
    // TODO: Fix schema generation so we don't need to typecast here!
    metadataChoices.value = response.data as unknown as MetadataChoices
  } catch (error) {
    errors.value = (error as BackendError).backendErrors
  }
}

fetchMetadataChoices()

const submit = async () => {
  isLoading.value = true

  const payload = {
    ...newValues,
    description: newValues.description
      ? {
          content_type: 'text/markdown',
          text: newValues.description
        }
      : null,
    links: externalLinksBuilderRef.value?.getLinks() ?? []
  }
  try {
    const request = () => creating.value
      ? axios.post('channels/', payload)
      : axios.patch(`channels/${props.object?.uuid}`, payload)

    const response = await request()
    if (creating.value) emit('created', response.data)
    else emit('updated', response.data)
  } catch (error) {
    errors.value = (error as BackendError).backendErrors
    emit('errored', errors.value)
  }

  isLoading.value = false
}

defineExpose({
  submit
})
</script>

<template>
  <Layout
    form
    class="ui form"
    @submit.prevent.stop="submit"
  >
    <Alert
      v-if="errors?.length > 0"
      red
    >
      <h4 class="header">
        {{ t('components.audio.ChannelForm.header.error') }}
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
    <template v-if="metadataChoices">
      <fieldset
        v-if="creating && step === 1"
        class="ui grouped channel-type required field"
      >
        <legend>
          {{ t('components.audio.ChannelForm.legend.purpose') }}
        </legend>
        <div class="ui hidden divider" />
        <div class="field">
          <div
            v-for="(choice, key) in categoryChoices"
            :key="key"
            :class="['ui', 'radio', 'checkbox', {selected: choice.value == newValues.content_category}]"
          >
            <input
              :id="`category-${choice.value}`"
              v-model="newValues.content_category"
              type="radio"
              name="channel-category"
              :value="choice.value"
            >
            <label :for="`category-${choice.value}`">
              <span :class="['right floated', 'placeholder', 'image', 'shifted', {circular: choice.value === 'music'}]" />
              <strong>{{ choice.label }}</strong>
              <div class="ui small hidden divider" />
              {{ choice.helpText }}
            </label>
          </div>
        </div>
      </fieldset>

      <template v-if="!creating || step === 2">
        <div class="ui required field">
          <Input
            v-model="newValues.name"
            type="text"
            required
            :placeholder="labels.namePlaceholder"
            :label="t('components.audio.ChannelForm.label.name')"
          />
        </div>
        <div class="ui required field">
          <Input
            v-model="newValues.username"
            type="text"
            :required="creating"
            :disabled="!creating"
            :placeholder="labels.usernamePlaceholder"
            :label="t('components.audio.ChannelForm.label.username')"
          />
          <template v-if="creating">
            <div class="ui small hidden divider" />
            <p>
              {{ t('components.audio.ChannelForm.help.username') }}
            </p>
          </template>
        </div>
        <div class="six wide column">
          <attachment-input
            v-model="newValues.cover"
            :image-class="newValues.content_category === 'podcast' ? '' : 'circular'"
            @delete="newValues.cover = null"
          >
            {{ t('components.audio.ChannelForm.label.image') }}
          </attachment-input>
        </div>
        <Pills
          :get="model => { newValues.tags = model.currents.map(({ label }) => label) }"
          :set="model => ({
            currents: newValues.tags.map(tag => ({ type: 'custom' as const, label: tag })),
            others: dataStore.tags().value.map(({ name }) => ({ type: 'custom' as const, label: name }))
          })"
          :label="t('components.audio.ChannelForm.label.tags')"
        />
        <div v-if="newValues.content_category === 'podcast'">
          <label for="channel-language">
            {{ t('components.audio.ChannelForm.label.language') }}
          </label>

          <select
            id="channel-language"
            v-model="newValues.metadata.language"
            name="channel-language"
            required
            class="ui search selection dropdown"
          >
            <option
              v-for="(v, key) in metadataChoices.language"
              :key="key"
              :value="v.value"
            >
              {{ v.label }}
            </option>
          </select>
        </div>
        <div class="ui field">
          <Textarea
            v-model="newValues.description"
            :label="t('components.audio.ChannelForm.label.description')"
            initial-lines="3"
          />
        </div>
        <div
          v-if="showExternalLinks"
          class="ui field"
        >
          <ExternalLinksBuilder
            ref="externalLinksBuilderRef"
            :links="newValues.links"
          />
        </div>
        <template v-if="newValues.content_category === 'podcast'">
          <div class="ui required field">
            <label for="channel-itunes-category">
              {{ t('components.audio.ChannelForm.label.category') }}
            </label>

            <select
              id="itunes-category"
              v-model="newValues.metadata.itunes_category"
              name="itunes-category"
              required
              class="ui dropdown"
            >
              <option
                v-for="(v, key) in metadataChoices.itunes_category"
                :key="key"
                :value="v.value"
              >
                {{ v.label }}
              </option>
            </select>
          </div>
          <div class="ui field">
            <label for="channel-itunes-category">
              {{ t('components.audio.ChannelForm.label.subcategory') }}
            </label>

            <select
              id="itunes-category"
              v-model="newValues.metadata.itunes_subcategory"
              name="itunes-category"
              :disabled="!newValues.metadata.itunes_category"
              class="ui dropdown"
            >
              <option
                v-for="(v, key) in itunesSubcategories"
                :key="key"
                :value="v"
              >
                {{ v }}
              </option>
            </select>
          </div>
        </template>
        <template v-if="newValues.content_category === 'podcast'">
          <Alert blue>
            <span>
              <i class="bi bi-info-circle-fill" />
              {{ t('components.audio.ChannelForm.help.podcastFields') }}
            </span>
          </Alert>
          <div class="ui field">
            <!-- @vue-ignore -->
            <Input
              id="channel-itunes-email"
              v-model="newValues.metadata.owner_email as string"
              name="channel-itunes-email"
              type="email"
              :label="t('components.audio.ChannelForm.label.email')"
            />
          </div>
          <div class="ui field">
            <!-- @vue-ignore -->
            <Input
              id="channel-itunes-name"
              v-model="newValues.metadata.owner_name as string"
              name="channel-itunes-name"
              maxlength="255"
              :label="t('components.audio.ChannelForm.label.owner')"
            />
          </div>
        </template>
      </template>
    </template>
    <Loader v-else />
  </Layout>
</template>
