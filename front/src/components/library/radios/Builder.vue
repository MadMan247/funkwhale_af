<script setup lang="ts">
import axios from 'axios'
import { computed, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

import TrackTable from '~/components/audio/track/Table.vue'
import RadioButton from '~/components/radios/Button.vue'
import useErrorHandler from '~/composables/useErrorHandler'
import { invalidate, useDataStore } from '~/ui/stores/data'

import Alert from '~/components/ui/Alert.vue'
import Button from '~/components/ui/Button.vue'
import Header from '~/components/ui/Header.vue'
import Heading from '~/components/ui/Heading.vue'
import Input from '~/components/ui/Input.vue'
import Layout from '~/components/ui/Layout.vue'
import Pills from '~/components/ui/Pills.vue'
import Section from '~/components/ui/Section.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Textarea from '~/components/ui/Textarea.vue'
import Toggle from '~/components/ui/Toggle.vue'

export interface BuilderFilter {
  type: string
  label: string
  help_text: string
  fields: FilterField[]
}

export interface FilterField {
  name: string
  placeholder: string
  type: 'list'
  subtype: 'number'
  autocomplete?: string
  autocomplete_qs: string
  autocomplete_fields: {
    remoteValues?: unknown
  }
}

export interface FilterConfig extends Record<string, unknown> {
  type: string
  not: boolean
  names: string[]
}

interface Filter {
  hash: number
  config: FilterConfig
  filter: BuilderFilter
}

interface Props {
  id?: number
}

const props = withDefaults(defineProps<Props>(), {
  id: 0
})

const { t } = useI18n()
const router = useRouter()
const dataStore = useDataStore()

const labels = computed(() => ({
  title: t('components.library.radios.Builder.title'),
  placeholder: {
    description: t('components.library.radios.Builder.placeholder.description'),
    name: t('components.library.radios.Builder.placeholder.name')
  }
}))

const filters = reactive<Filter[]>([])
const checkResult = ref()
const fetchCandidates = async () => {
  // TODO (wvffle): Add loader

  try {
    const response = await axios.post('radios/radios/validate/', {
      filters: [{
        type: 'group',
        filters: filters.map(filter => ({
          ...filter.config,
          type: filter.filter.type
        }))
      }]
    })

    checkResult.value = response.data.filters[0]
  } catch (error) {
    useErrorHandler(error as Error)
  }
}

// NOTE: Whenever we modify filters array, we refetch the candidates automatically
watch(filters, fetchCandidates, {
  deep: true
})

const checkErrors = computed(() => checkResult.value?.errors ?? [])

const isPublic = ref(true)
const radioName = ref('')
const radioDesc = ref('')
const canSave = computed(() => radioName.value.length > 0 && checkErrors.value.length === 0)

const currentFilterType = ref()
const availableFilters = reactive<BuilderFilter[]>([])
const currentFilter = computed(() => availableFilters.find(filter => filter.type === currentFilterType.value))

const fetchFilters = async () => {
  // TODO (wvffle): Add loader
  try {
    const response = await axios.get('radios/radios/filters/')
    availableFilters.length = 0
    availableFilters.push(...response.data)
  } catch (error) {
    useErrorHandler(error as Error)
  }
}

let filterId = Number.MIN_SAFE_INTEGER
const isLoading = ref(false)
const fetchData = async () => {
  isLoading.value = true

  try {
    const response = await axios.get(`radios/radios/${props.id}/`)
    filters.length = 0
    filters.push(...response.data.config.map((config: FilterConfig) => ({
      config,
      filter: availableFilters.find(available => available.type === config.type),
      hash: filterId++
    })))

    radioName.value = response.data.name
    radioDesc.value = response.data.description
    isPublic.value = response.data.is_public
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

fetchFilters().then(() => fetchData())

/**
 * Create a new filter
 */
const add = async (type: string) => {
  if (!currentFilter.value) return
  filters.push({
    config: {
      type,
      options: {},
      not: false,
      names: []
    },
    filter: currentFilter.value,
    hash: +new Date()
  })
}

const success = ref(false)
const save = async () => {
  success.value = false
  isLoading.value = true

  try {
    const data = {
      name: radioName.value,
      description: radioDesc.value,
      is_public: isPublic.value,
      config: filters.map(filter => ({
        ...filter.config,
        type: filter.filter.type
      }))
    }

    const response = props.id
      ? await axios.put(`radios/radios/${props.id}/`, data)
      : await axios.post('radios/radios/', data)

    success.value = true

    // Invalidate all radios in the cache
    dataStore.cachedResources.forEach(res => {
      if (res.name === 'radios/radios') invalidate(res)
    })

    if (!props.id) {
      router.push({
        name: 'library.radios.detail',
        params: {
          id: response.data.id
        }
      })
    }
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

// ------------- Get and set filter selections --------------


</script>

<template>
  <Layout
    v-title="labels.title"
    main
    stack
    gap-64
  >
    <Header
      :h1="t('components.library.radios.Builder.header.builder')"
      page-heading
      icon="bi-boombox large"
    >
      <Layout form>
        <p>
          {{ t('components.library.radios.Builder.description.builder') }}
        </p>
        <Alert
          v-if="success"
          green
        >
          <h4 class="header">
            <template v-if="radioName">
              {{ t('components.library.radios.Builder.header.updated') }}
            </template>
            <template v-else>
              {{ t('components.library.radios.Builder.header.created') }}
            </template>
          </h4>
        </Alert>
        <Input
          id="name"
          v-model="radioName"
          :label="t('components.library.radios.Builder.label.name')"
          name="name"
          type="text"
          :placeholder="labels.placeholder.name"
        />
        <Textarea
          id="description"
          v-model="radioDesc"
          :label="t('components.library.radios.Builder.label.description')"
          rows="2"
          type="text"
          :placeholder="labels.placeholder.description"
        />
        <Toggle
          id="public"
          v-model="isPublic"
          type="checkbox"
          :label="t('components.library.radios.Builder.label.public')"
        />
        <Button
          :disabled="!canSave"
          :class="['ui', 'success', {loading: isLoading}, 'button']"
          primary
          @click="save"
        >
          {{ t('components.library.radios.Builder.button.save') }}
        </Button>
        <radio-button
          v-if="id"
          type="custom"
          :custom-radio-id="id"
        />
      </Layout>
    </Header>

    <Section>
      <!-- Add -->

      <Layout
        flex
      >
        <Heading
          :h3="t('components.library.radios.Builder.label.filter')"
          caption
          style="align-self: center;"
        />
        <Spacer grow />
        <Layout
          flex
        >
          <Button
            v-for="f in availableFilters"
            :key="f.label"
            :value="f.type"
            icon="bi-plus"
            low-height
            thin-font
            :disabled="f.type !== 'tag'"
            @click="() => { currentFilterType = f.type; add(f.type); }"
          >
            {{ f.label }}
          </Button>
        </Layout>
      </Layout>

      <!-- List of filters -->

      <!-- TODO: Use new Table component. -->

      <table v-if="filters.length>0">
        <thead>
          <tr>
            <th>
              {{ t('components.library.radios.Builder.table.filter.header.name') }}
            </th>
            <th style="opacity: 0;">
              {{ t('components.library.radios.Builder.table.filter.header.exclude') }}
            </th>
            <th style="opacity: 0;">
              {{ t('components.library.radios.Builder.table.filter.header.config') }}
            </th>
            <!-- TODO: Re-implement candidates checking for each filter -->
            <!-- <th>
              {{ t('components.library.radios.Builder.table.filter.header.candidates') }}
            </th> -->
            <th style="opacity: 0;">
              {{ t('components.library.radios.Builder.table.filter.header.actions') }}
            </th>
          </tr>
        </thead>
        <tbody>
          <!-- Filter -->

          <tr
            v-for="(f, index) in filters"
            :key="f.hash"
          >
            <!-- Row: Name (Label) -->

            <td>{{ f.filter.label }}</td>

            <!-- Row: Exclude? -->

            <td>
              <Toggle
                v-model="f.config.not"
                :label="t('components.library.radios.Filter.excludeLabel')"
              />
            </td>

            <!-- Row: Config (List of FilterFields) -->

            <td>
              <!-- A multi-select from a pool of type `playlist`, `tag` or `artist` -->

              <!-- TODO: Implement on-the-fly search for artists and playlists -->

              <Pills
                v-if="f.config.type === 'tag'"
                :get="model => {
                  /* Overwrite the current filter */
                  f.config.names = model.currents.map(item => item.label)
                }"
                :set="model =>({
                  /* Load/initialize filter at `index` */
                  currents: f.config.names.map(name => ({ label: name, type: 'preset' as const })),
                  others: dataStore.tags().value.map(({ name }) => ({ type: 'preset' as const, label: name }))
                })
                "
              />
            </td>
            <!-- TODO:  Query candidates for each filter -->

            <!-- <td>
                {{ t('components.library.radios.Filter.matchingTracks', checkResult.candidates.count) }}
            </td> -->

            <!-- Row: Remove this filter -->

            <td>
              <Button
                destructive
                ghost
                @click="filters.splice(index, 1)"
              >
                {{ t('components.library.radios.Filter.removeButton') }}
              </Button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Info -->

      <Alert
        v-if="currentFilter"
        blue
      >
        {{ currentFilter.help_text }}
      </Alert>

      <template v-if="checkResult && checkResult.candidates && checkResult.candidates.count">
        <h3 class="ui header">
          {{ t('components.library.radios.Builder.header.matches', checkResult.candidates.count) }}
        </h3>
        <track-table
          v-if="checkResult.candidates.sample"
          :tracks="checkResult.candidates.sample"
          :playable="true"
          :show-position="false"
          :show-duration="false"
          :display-actions="false"
        />
      </template>
    </Section>
  </Layout>
</template>

<style scoped>
  th {
    text-align: left;
  }
  td:last-child {
    text-align: right;
  }
  td:not(:last-child) {
    padding-right: 16px;
  }
</style>
