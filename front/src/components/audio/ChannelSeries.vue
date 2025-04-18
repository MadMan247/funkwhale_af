<script setup lang="ts">
import type { BackendError, Album } from '~/types'

import { clone } from 'lodash-es'
import { ref, reactive } from 'vue'
import { useI18n } from 'vue-i18n'

import axios from 'axios'
import ChannelSerieCard from '~/components/audio/ChannelSerieCard.vue'
import AlbumCard from '~/components/audio/album/Card.vue'
import Layout from '~/components/ui/Layout.vue'
import Loader from '~/components/ui/Loader.vue'
import Button from '~/components/ui/Button.vue'

interface Props {
  filters: object
  isPodcast?: boolean
  limit?: number
}

const { t } = useI18n()

const props = withDefaults(defineProps<Props>(), {
  isPodcast: true,
  limit: 5
})

const isLoading = ref(false)
const errors = ref([] as string[])

const albums = reactive([] as Album[])
const nextPage = ref()
const count = ref(0)

const fetchData = async (url = 'albums/') => {
  isLoading.value = true

  try {
    const params = {
      ...clone(props.filters),
      page_size: props.limit,
      include_channels: true
    }

    const response = await axios.get(url, { params })
    nextPage.value = response.data.next
    count.value = response.data.count
    albums.push(...response.data.results)
  } catch (error) {
    errors.value = (error as BackendError).backendErrors
  }

  isLoading.value = false
}

fetchData()
</script>

<template>
  <slot />
  <Layout flex>
    <Loader v-if="isLoading" />
    <template v-if="isPodcast">
      <channel-serie-card
        v-for="serie in albums"
        :key="serie.id"
        :serie="serie"
      />
    </template>
    <template v-else>
      <album-card
        v-for="album in albums"
        :key="album.id"
        :album="album"
      />
    </template>
    <template v-if="nextPage">
      <Button
        v-if="nextPage"
        secondary
        @click="fetchData(nextPage)"
      >
        {{ t('components.audio.ChannelSeries.button.showMore') }}
      </Button>
    </template>
  </Layout>
  <template v-if="!isLoading && albums.length === 0">
    <empty-state
      :refresh="true"
      @refresh="fetchData()"
    >
      <p>
        {{ t('components.audio.ChannelSeries.help.subscribe') }}
      </p>
    </empty-state>
  </template>
</template>
