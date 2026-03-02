<script setup lang="ts">
import type { Library } from '~/types'

import ArtistWidget from '~/components/artist/Widget.vue'

import { useI18n } from 'vue-i18n'

const { t } = useI18n()

interface Props {
  object: Library
  isOwner: boolean
}

defineProps<Props>()
</script>

<template>
  <section>
    <ArtistWidget
      v-if="object.uuid"
      ref="artists"
      :key="object.uploads_count"
      :query="{
        playable: true,
        ordering: ['-creation_date'],
        library: object.uuid
      }"
      has-search
      :header="false /* TODO: Remove non-existent prop? */"
      :controls="false /* TODO: Remove non-existent prop? */"
    >
      <template #empty-state>
        <empty-state>
          <p>
            <span
              v-if="isOwner"
            >
              {{ t('views.library.DetailOverview.empty.upload') }}
            </span>
            <span
              v-else
            >
              {{ t('views.library.DetailOverview.empty.follow') }}
            </span>
          </p>
        </empty-state>
      </template>
    </ArtistWidget>
  </section>
</template>
