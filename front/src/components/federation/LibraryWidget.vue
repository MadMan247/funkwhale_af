<script setup lang="ts">
import type { Library } from '~/types'

import { ref, reactive, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import axios from 'axios'

import Button from '~/components/ui/Button.vue'
import Section from '~/components/ui/Section.vue'
import Loader from '~/components/ui/Loader.vue'
import Alert from '~/components/ui/Alert.vue'
import Spacer from '~/components/ui/Spacer.vue'
import ActorLink from '~/components/common/ActorLink.vue'

import useErrorHandler from '~/composables/useErrorHandler'
import Layout from '../ui/Layout.vue'

interface Events {
  (e: 'loaded', libraries: Library[]): void
}

interface Props {
  url: string
  title?: string
}

const { t } = useI18n()

const emit = defineEmits<Events>()
const props = defineProps<Props>()

const nextPage = ref()
const libraries = reactive([] as Library[])
const isLoading = ref(false)
const fetchData = async (url = props.url) => {
  isLoading.value = true

  try {
    const response = await axios.get(url, {
      params: {
        page_size: 3
      }
    })

    nextPage.value = response.data.next
    libraries.splice(0, libraries.length, ...response.data.results)
    emit('loaded', libraries)
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

onMounted(() => {
  setTimeout(fetchData, 1000)
})

watch(() => props.url, () => {
  fetchData()
})
</script>

<template>
  <Section
    align-left
    :h2="title"
  >
    <Loader
      v-if="isLoading"
      style="grid-column: 1 / -1;"
    />
    <Alert
      v-if="!isLoading && libraries.length === 0"
      blue
      style="grid-column: 1 / -1;"
    >
      {{ t('components.federation.LibraryWidget.empty.noMatch') }}
    </Alert>
    <Layout
      v-if="!isLoading && libraries.length > 0"
      flex
      no-gap
    >
      {{ t('components.federation.LibraryWidget.main') }}
      <template
        v-for="library in libraries"
        :key="library.uuid"
      >
        <ActorLink
          :actor="library.actor"
          discrete
          raised
        />
      </template>
    </Layout>
    <template v-if="nextPage">
      <Spacer />
      <Button
        v-if="nextPage"
        primary
        @click="fetchData(nextPage)"
      >
        {{ t('components.federation.LibraryWidget.button.showMore') }}
      </Button>
    </template>
  </Section>
</template>
