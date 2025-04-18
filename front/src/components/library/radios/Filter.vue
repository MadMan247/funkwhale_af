<script setup lang="ts">
// TODO (wvffle): SORT IMPORTS LIKE SO EVERYWHERE
import type { BuilderFilter, FilterConfig } from './Builder.vue'
import type { Track } from '~/types'
import { useI18n } from 'vue-i18n'

import axios from 'axios'

import { useVModel } from '@vueuse/core'
import { ref, onMounted, watch, computed } from 'vue'
import { useStore } from '~/store'
import { clone } from 'lodash-es'

import Modal from '~/components/ui/Modal.vue'
import TrackTable from '~/components/audio/track/Table.vue'
import Button from '~/components/ui/Button.vue'

import useErrorHandler from '~/composables/useErrorHandler'

type Filter = { candidates: { count: number, sample: Track[] } }
type ResponseType = { filters: Array<Filter> }

interface Events {
  (e: 'update:data', name: string, value: number[] | boolean): void
  (e: 'delete'): void
}

interface Props {
  data: {
    filter: BuilderFilter
    config: FilterConfig
  }
}

const { t } = useI18n()

const emit = defineEmits<Events>()
const props = defineProps<Props>()
const data = useVModel(props, 'data', emit)

const store = useStore()

const checkResult = ref<Filter | null>(null)
const showCandidadesModal = ref(false)
const exclude = computed({
  get: () => data.value.config.not,
  set: (value: boolean) => (data.value.config.not = value)
})

// const el = useCurrentElement()

// This component appears on "create new radio" and offers filters. "New filter" => Dropdown search field
// TODO: Re-implement with <Input>, <select>

onMounted(() => {
  for (const field of data.value.filter.fields) {
    // @ts-expect-error We threw out Semantic UI types
    const settings: SemanticUI.DropdownSettings = {
      // @ts-expect-error value? any!
      onChange (value) {
        // TODO: Find out if the following removal causes any regression #2440
        // value = $(this).dropdown('get value').split(',')

        // if (field.type === 'list' && field.subtype === 'number') {
        //   value = value.map((number: string) => parseInt(number))
        // }

        // data.value.config[field.name] = value
        fetchCandidates()
      }
    }

    let selector = field.type === 'list'
      ? '.dropdown.multiple'
      : '.dropdown'

    if (field.autocomplete) {
      selector += '.autocomplete'

      settings.fields = field.autocomplete_fields
      settings.minCharacters = 1
      settings.apiSettings = {
        url: store.getters['instance/absoluteUrl'](`${field.autocomplete}?${field.autocomplete_qs}`),
        // @ts-expect-error xhr? any!
        beforeXHR (xhrObject) {
          if (store.state.auth.oauth.accessToken) {
            xhrObject.setRequestHeader('Authorization', store.getters['auth/header'])
          }

          return xhrObject
        },
        // @ts-expect-error initialResponse? any!
        onResponse (initialResponse) {
          return !settings.fields?.remoteValues
            ? { results: initialResponse.results }
            : initialResponse
        }
      }
    }

    // TODO: Find out if the following removal causes any regression #2440
    // $(el.value).find(selector).dropdown(settings)
  }
})

const fetchCandidates = async () => {
  const params = {
    filters: [{
      ...clone(data.value.config),
      type: data.value.filter.type
    }]
  }

  try {
    const response = await axios.post('radios/radios/validate/', params)
    checkResult.value = (response.data as ResponseType).filters[0]
  } catch (error) {
    useErrorHandler(error as Error)
  }
}

watch(exclude, fetchCandidates)
fetchCandidates()
</script>

<template>
  <tr>
    <td>{{ data.filter.label }}</td>
    <td>
      <div class="ui toggle checkbox">
        <input
          id="exclude-filter"
          v-model="exclude"
          name="public"
          type="checkbox"
        >
        <label
          for="exclude-filter"
          class="visually-hidden"
        >
          {{ t('components.library.radios.Filter.excludeLabel') }}
        </label>
      </div>
    </td>
    <td>
      <div
        v-for="f in data.filter.fields"
        :key="f.name"
        class="ui field"
      >
        <div :class="['ui', 'search', 'selection', 'dropdown', { autocomplete: f.autocomplete }, { multiple: f.type === 'list' }]">
          <i class="dropdown icon" />
          <div class="default text">
            {{ f.placeholder }}
          </div>
          <input
            v-if="f.type === 'list' && data.config[f.name as keyof FilterConfig]"
            :id="f.name"
            :value="(data.config[f.name as keyof FilterConfig] as string[]).join(',')"
            type="hidden"
          >
          <div
            v-if="typeof data.config[f.name as keyof FilterConfig] === 'object'"
            class="ui menu"
          >
            <div
              v-for="(v, i) in data.config[f.name as keyof FilterConfig] as object"
              v-once
              :key="data.config.ids?.[i] ?? v"
              class="ui item"
              :data-value="v"
            >
              <template v-if="data.config.names">
                {{ data.config.names[i] }}
              </template>
              <template v-else>
                {{ v }}
              </template>
            </div>
          </div>
        </div>
      </div>
    </td>
    <td>
      <a
        v-if="checkResult"
        href=""
        :class="['ui', { success: checkResult.candidates.count > 10 }, 'label']"
        @click.prevent="showCandidadesModal = !showCandidadesModal"
      >
        {{ t('components.library.radios.Filter.matchingTracks', checkResult.candidates.count) }}
      </a>
      <Modal
        v-if="checkResult"
        v-model:show="showCandidadesModal"
        :title="t('components.library.radios.Filter.matchingTracksModalHeader')"
      >
        <div class="content">
          <div class="description">
            <track-table
              v-if="checkResult.candidates.count > 0"
              :tracks="checkResult.candidates.sample"
            />
          </div>
        </div>
        <div class="actions">
          <Button color="secondary">
            {{ t('components.library.radios.Filter.cancelButton') }}
          </Button>
        </div>
      </Modal>
    </td>
    <td>
      <Button
        destructive
        @click="emit('delete')"
      >
        {{ t('components.library.radios.Filter.removeButton') }}
      </Button>
    </td>
  </tr>
</template>
