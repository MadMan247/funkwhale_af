<script setup lang="ts">
import type { Library } from '~/types'
import { ref } from 'vue'
import { useStore } from '~/store'

import axios from 'axios'

import LibraryCard from '~/views/content/remote/Card.vue'
import Quota from './Quota.vue'

import useErrorHandler from '~/composables/useErrorHandler'

import Loader from '~/components/ui/Loader.vue'
import Section from '~/components/ui/Section.vue'
import Spacer from '~/components/ui/Spacer.vue'


import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const store = useStore()

const libraries = ref([] as Library[])
const isLoading = ref(false)
const hiddenForm = ref(true)
const fetchData = async () => {
  isLoading.value = true

  try {
    const response = await axios.get('libraries/', { params: { scope: 'me' } })
    libraries.value = response.data.results
    if (libraries.value.length === 0) {
      hiddenForm.value = false
    }
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

fetchData()
</script>

<template>
  <Loader v-if="isLoading" />
  <Section
    v-else
    :h1="t('views.content.libraries.Home.header.libraries')"
    page-header
  >
    <quota />
  </Section>
  <Spacer />
  <Section
    v-if="libraries.length > 0"
  >
    <library-card
      v-for="library in libraries"
      :key="library.uuid"
      :display-scan="false"
      :display-follow="store.state.auth.authenticated && library.actor.full_username != store.state.auth.fullUsername"
      :initial-library="library"
      :display-copy-fid="true"
    />
  </Section>
</template>
