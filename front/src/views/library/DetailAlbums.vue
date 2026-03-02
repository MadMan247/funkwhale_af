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
  <!-- TODO: Consider adding a semantic role (preferably through the Section component) -->
  <section>
    <AlbumWidget
      v-if="object.uuid"
      :key="String(object.uploads_count)"
      has-search
      :query="{
        playable: true,
        ordering: ['-creation_date'],
        library: object.uuid
      }"
      :header="false /* TODO: Remove non-existent prop? */"
      :controls="false /* TODO: Remove non-existent prop? */"
    >
      <empty-state>
        <p>
          {{ isOwner
            ? t('views.library.DetailAlbums.empty.upload')
            : t('views.library.DetailAlbums.empty.follow')
          }}
        </p>
      </empty-state>
    </AlbumWidget>
  </section>
</template>
