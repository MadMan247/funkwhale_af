<script setup lang="ts">
// import type { Tag } from '~/types'

import { ref, watch, onMounted, nextTick } from 'vue'
// import { isEqual } from 'lodash-es'
// import { useStore } from '~/store'
import { useI18n } from 'vue-i18n'

// interface Events {
//   (e: 'update:modelValue', tags: string[]): void
// }

interface Props {
  modelValue: string[]
}

const { t } = useI18n()

// const emit = defineEmits<Events>()
const props = defineProps<Props>()

// const store = useStore()

const dropdown = ref()

watch(() => props.modelValue, (value) => {
  return
  // TODO: Find out if the following removal causes any regression #2440
  // const current = $(dropdown.value).dropdown('get value').split(',').sort()

  // if (!isEqual([...value].sort(), current)) {
  //   $(dropdown.value).dropdown('set exactly', value)
  // }
})

// TODO: Find out if the following removal causes any regression #2440
// const handleUpdate = () => {
//   const value = $(dropdown.value).dropdown('get value').split(',')
//   emit('update:modelValue', value)
//   return value
// }

onMounted(async () => {
  await nextTick()

  // TODO: Find out if the following removal causes any regression #2440
  // $(dropdown.value).dropdown({
  //   keys: { delimiter: 32 },
  //   forceSelection: false,
  //   saveRemoteData: false,
  //   filterRemoteData: true,
  //   preserveHTML: false,
  //   apiSettings: {
  //     url: store.getters['instance/absoluteUrl']('/api/v1/tags/?name__startswith={query}&ordering=length&page_size=5'),
  //     // @ts-expect-error I'm not curious to research what xhr is but I'm sure it served its purpose well
  //     beforeXHR: function (xhrObject) {
  //       if (store.state.auth.oauth.accessToken) {
  //         xhrObject.setRequestHeader('Authorization', store.getters['auth/header'])
  //       }
  //       return xhrObject
  //     },
  //     // @ts-expect-error yes, semantic-ui has a large API.
  //     onResponse (response) {
  //       response = { results: [], ...response }

  //       const currentSearch: string = ''
  //       // TODO: Find out if the following removal causes any regression #2440
  //       // $(dropdown.value).dropdown('get query')

  //       if (currentSearch) {
  //         const existingTag = response.results.find((result: Tag) => result.name === currentSearch)

  //         if (existingTag) {
  //           if (response.results.indexOf(existingTag) !== 0) {
  //             response.results = [existingTag, ...response.results]
  //             response.results.splice(response.results.indexOf(existingTag) + 1, 1)
  //           }
  //         } else {
  //           response.results = [{ name: currentSearch }, ...response.results]
  //         }
  //       }
  //       return response
  //     }
  //   },
  //   fields: { remoteValues: 'results', value: 'name' },
  //   allowAdditions: true,
  //   minCharacters: 1,
  //   onAdd: handleUpdate,
  //   onRemove: handleUpdate,
  //   onLabelRemove: handleUpdate,
  //   onChange: handleUpdate
  // })
  // $(dropdown.value).dropdown('set exactly', props.modelValue)
})
</script>

<template>
  <div
    ref="dropdown"
    class="ui multiple search selection dropdown"
  >
    <input type="hidden">
    <i class="dropdown icon" />
    <input
      id="tags-search"
      type="text"
      class="search"
    >
    <div class="default text">
      {{ t('components.library.TagSelector.placeholder.search') }}
    </div>
  </div>
</template>
