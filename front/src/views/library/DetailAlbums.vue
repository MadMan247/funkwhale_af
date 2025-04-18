<script setup lang="ts">
import type { Library } from '~/types'

import AlbumWidget from '~/components/album/Widget.vue'

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
    <album-widget
      v-if="object.uuid"
      :key="String(object.uploads_count)"
      :header="false"
      :search="true"
      :controls="false"
      :filters="{playable: true, ordering: '-creation_date', library: object.uuid}"
    >
      <template #empty-state>
        <empty-state>
          <p>
            <span
              v-if="isOwner"
            >
              {{ t('views.library.DetailAlbums.empty.upload') }}
            </span>
            <span
              v-else
            >
              {{ t('views.library.DetailAlbums.empty.follow') }}
            </span>
          </p>
        </empty-state>
      </template>
    </album-widget>
  </section>
</template>
