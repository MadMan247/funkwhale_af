<script setup lang="ts">
import type { Track, Radio } from '~/types'

import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useStore } from '~/store'

import axios from 'axios'

import DangerousButton from '~/components/common/DangerousButton.vue'
import TrackTable from '~/components/audio/track/Table.vue'
import RadioButton from '~/components/radios/Button.vue'

import Layout from '~/components/ui/Layout.vue'
import Header from '~/components/ui/Header.vue'
import Section from '~/components/ui/Section.vue'
import Pagination from '~/components/ui/Pagination.vue'
import Alert from '~/components/ui/Alert.vue'
import Button from '~/components/ui/Button.vue'

import useErrorHandler from '~/composables/useErrorHandler'

interface Props {
  id: number
}

const props = defineProps<Props>()

const radio = ref<Radio | null>(null)
const tracks = ref([] as Track[])
const totalTracks = ref(0)
const page = ref(1)

const { t } = useI18n()
const labels = computed(() => ({
  title: t('views.radios.Detail.title')
}))

const isLoading = ref(false)
const fetchData = async () => {
  isLoading.value = true

  const url = `radios/radios/${props.id}/`

  try {
    const radioResponse = await axios.get(url)
    radio.value = radioResponse.data

    const tracksResponse = await axios.get(url + 'tracks/', { params: { page: page.value } })
    totalTracks.value = tracksResponse.data.count
    tracks.value = tracksResponse.data.results
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

watch(page, fetchData, { immediate: true })

const router = useRouter()
const store = useStore()

const deleteRadio = async () => {
  try {
    await axios.delete(`radios/radios/${props.id}/`)
    return router.push({ path: '/library' })
  } catch (error) {
    useErrorHandler(error as Error)
  }
}
</script>

<template>
  <Layout
    stack
    main
  >
    <Loader
      v-if="isLoading"
      v-title="labels.title"
    />
    <Header
      v-if="!isLoading && radio"
      v-title="radio.name"
      page-heading
      :h1="radio.name"
    />
    <h2 class="sub header">
      {{ t('views.radios.Detail.header.radio', {tracks: totalTracks}) }}<username :username="radio?.user.username" />
    </h2>
    <Layout flex>
      <radio-button
        :custom-radio-id="radio?.id"
      />
      <template v-if="store.state.auth.username === radio?.user.username">
        <Button
          icon="bi-pencil"
          secondary
          :to="{name: 'library.radios.edit', params: {id: radio?.id}}"
        >
          {{ t('views.radios.Detail.button.edit') }}
        </Button>
        <dangerous-button
          :action="deleteRadio"
          :title="t('views.radios.Detail.modal.delete.header', {radio: radio.name})"
          icon="bi-trash"
        >
          {{ t('views.radios.Detail.button.delete') }}
          <template #content>
            {{ t('views.radios.Detail.modal.delete.content.warning') }}
          </template>
          <template #confirm>
            {{ t('views.radios.Detail.button.confirm') }}
          </template>
        </dangerous-button>
      </template>
    </Layout>
    <Section
      v-if="totalTracks > 0"
      :h2="t('views.radios.Detail.header.tracks')"
    >
      <track-table :tracks="tracks" />
      <Pagination
        v-if="totalTracks > 25"
        v-model:page="page"
        :pages="Math.ceil(totalTracks / 25)"
      />
    </Section>
    <Alert
      v-else-if="!isLoading && totalTracks === 0"
      blue
    >
      <Layout
        stack
        style="text-align: center;"
      >
        <i
          class="bi bi-broadcast-pin"
          style="font-size: 5em;"
        />
        {{ t('views.radios.Detail.empty.noTracks') }}
        <Button
          v-if="store.state.auth.username === radio?.user.username"
          primary
          icon="bi-pencil"
          style="align-self: center;"
          :to="{name: 'library.radios.edit', params: { id: radio?.id }}"
        >
          {{ t('views.radios.Detail.button.edit') }}
        </Button>
      </Layout>
    </Alert>
  </Layout>
</template>
