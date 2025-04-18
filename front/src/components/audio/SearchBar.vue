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
  // TODO: Find out what jQuery version supports `search`
  // jQuery(el.value).search('cancel query')

  // Cancel any API search request to backend…
  return router.push(`/search?q=${query.value}&type=artists`)
}

const blur = () => {
  search.value.blur()
}

onMounted(() => {
  // TODO: Find out what jQuery version supports `search`
  // jQuery(el.value).search({
  //   type: 'category',
  //   minCharacters: 3,
  //   showNoResults: true,
  //   error: {
  //     // @ts-expect-error Semantic is broken
  //     noResultsHeader: t('components.audio.SearchBar.header.noResults'),
  //     noResults: t('components.audio.SearchBar.empty.noResults')
  //   },

  //   onSelect (result, response) {
  //     jQuery(el.value).search('set value', query.value)
  //     router.push(result.routerUrl)
  //     jQuery(el.value).search('hide results')
  //     return false
  //   },
  //   onSearchQuery (value) {
  //     // query.value = value
  //     emit('search')
  //   },
  //   apiSettings: {
  //     url: store.getters['instance/absoluteUrl']('api/v1/search?query={query}'),
  //     beforeXHR: function (xhrObject) {
  //       if (!store.state.auth.authenticated) {
  //         return xhrObject
  //       }

  //       if (store.state.auth.oauth.accessToken) {
  //         xhrObject.setRequestHeader('Authorization', store.getters['auth/header'])
  //       }

  //       return xhrObject
  //     },
  //     onResponse: function (initialResponse) {
  //       const id = objectId.value
  //       const results: Partial<Record<CategoryCode, Results>> = {}

  //       let resultsEmpty = true
  //       for (const category of categories.value) {
  //         results[category.code] = {
  //           name: category.name,
  //           results: []
  //         }

  //         if (category.code === 'federation' && id) {
  //           resultsEmpty = false
  //           results[category.code]?.results.push({
  //             title: t('components.audio.SearchBar.link.fediverse'),
  //             routerUrl: {
  //               name: 'search',
  //               query: { id }
  //             }
  //           })
  //         }

  //         if (category.code === 'podcasts' && id) {
  //           resultsEmpty = false
  //           results[category.code]?.results.push({
  //             title: t('components.audio.SearchBar.link.rss'),
  //             routerUrl: {
  //               name: 'search',
  //               query: { id, type: 'rss' }
  //             }
  //           })
  //         }

  //         if (category.code === 'more') {
  //           results[category.code]?.results.push({
  //             title: t('components.audio.SearchBar.link.more'),
  //             routerUrl: {
  //               name: 'search',
  //               query: { type: 'artists', q: query.value }
  //             }
  //           })
  //         }

  //         if (isCategoryGuard(category)) {
  //           for (const result of initialResponse[category.code]) {
  //             resultsEmpty = false
  //             const id = category.getId(result)
  //             results[category.code]?.results.push({
  //               title: category.getTitle(result),
  //               id,
  //               routerUrl: {
  //                 name: category.route,
  //                 params: { id }
  //               },
  //               description: category.getDescription(result)
  //             })
  //           }
  //         }
  //       }

  //       return {
  //         results: resultsEmpty
  //           ? {}
  //           : results
  //       }
  //     }
  //   }
  // })
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
