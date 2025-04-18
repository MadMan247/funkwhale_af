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
    <artist-widget
      v-if="object.uuid"
      :key="object.uploads_count"
      ref="artists"
      :header="false"
      :search="true"
      :controls="false"
      :filters="{ playable: true, ordering: '-creation_date', library: object.uuid }"
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
    </artist-widget>
  </section>
</template>
