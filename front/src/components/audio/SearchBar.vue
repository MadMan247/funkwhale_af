<script setup lang="ts">

import { useFocus } from '@vueuse/core'
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

import onKeyboardShortcut from '~/composables/onKeyboardShortcut'

const search = ref()
const { focused } = useFocus(search)
onKeyboardShortcut(['shift', 'f'], () => (focused.value = true), true)
onKeyboardShortcut(['ctrl', 'k'], () => (focused.value = true), true)

const { t } = useI18n()
const labels = computed(() => ({
  placeholder: t('components.audio.SearchBar.placeholder.search'),
  searchContent: t('components.audio.SearchBar.label.search'),
  artist: t('components.audio.SearchBar.label.artist'),
  album: t('components.audio.SearchBar.label.album'),
  track: t('components.audio.SearchBar.label.track'),
  tag: t('components.audio.SearchBar.label.tag')
}))

const router = useRouter()
const query = ref()

const enter = () => {
  // Cancel any API search request to backend…
  return router.push(`/search?q=${query.value}&type=artists`)
}

const blur = () => {
  search.value.blur()
}

onMounted(() => {
  // Search functionality could be implemented here if needed
})
</script>

<template>
  <div
    class="ui fluid category search"
    @keypress.enter="enter"
  >
    <slot />
    <div class="ui icon input">
      <input
        ref="search"
        v-model="query"
        :aria-label="labels.searchContent"
        type="search"
        class="prompt"
        name="search"
        :placeholder="labels.placeholder"
        @keydown.esc="blur"
      >
      <i class="search icon" />
    </div>
    <div class="results" />
    <slot name="after" />
  </div>
</template>
