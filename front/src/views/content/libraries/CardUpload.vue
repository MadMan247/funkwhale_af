<script setup lang="ts">
import type { Library, PrivacyLevelEnum } from '~/types'

import { useI18n } from 'vue-i18n'
import { computed } from 'vue'

import useSharedLabels from '~/composables/locale/useSharedLabels'

interface Props {
  library: Library
}
interface Props {
  new : boolean
}

const props = defineProps<Props>()

const title = computed(() => props.library?.name || props.new)

const imageUrl = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA1MTIgNTEyIj48IS0tIUZvbnQgQXdlc29tZSBGcmVlIDYuNi4wIGJ5IEBmb250YXdlc29tZSAtIGh0dHBzOi8vZm9udGF3ZXNvbWUuY29tIExpY2Vuc2UgLSBodHRwczovL2ZvbnRhd2Vzb21lLmNvbS9saWNlbnNlL2ZyZWUgQ29weXJpZ2h0IDIwMjQgRm9udGljb25zLCBJbmMuLS0+PHBhdGggZD0iTTI1NiA4MEMxNDkuOSA4MCA2Mi40IDE1OS40IDQ5LjYgMjYyYzkuNC0zLjggMTkuNi02IDMwLjQtNmMyNi41IDAgNDggMjEuNSA0OCA0OGwwIDEyOGMwIDI2LjUtMjEuNSA0OC00OCA0OGMtNDQuMiAwLTgwLTM1LjgtODAtODBsMC0xNiAwLTQ4IDAtNDhDMCAxNDYuNiAxMTQuNiAzMiAyNTYgMzJzMjU2IDExNC42IDI1NiAyNTZsMCA0OCAwIDQ4IDAgMTZjMCA0NC4yLTM1LjggODAtODAgODBjLTI2LjUgMC00OC0yMS41LTQ4LTQ4bDAtMTI4YzAtMjYuNSAyMS41LTQ4IDQ4LTQ4YzEwLjggMCAyMSAyLjEgMzAuNCA2QzQ0OS42IDE1OS40IDM2Mi4xIDgwIDI1NiA4MHoiLz48L3N2Zz4='

const { t } = useI18n()

const sharedLabels = useSharedLabels()

// TODO: Check if this is still needed:
// const sizeLabel = computed(() => t('views.content.libraries.Card.label.size'))

const privacyTooltips = (level: PrivacyLevelEnum) => `Visibility: ${sharedLabels.fields.privacy_level.choices[level].toLowerCase()}`
</script>

<template>
  <fw-card
    :title="title"
    :image="imageUrl"
  >
    <div class="content">
      <h4 class="header">
        <span
          v-if="library.privacy_level === 'me'"
          class="right floated"
          :data-tooltip="privacyTooltips('me')"
        >
          <i class="small lock icon" />
        </span>
        <span
          v-else-if="library.privacy_level === 'instance'"
          class="right floated"
          :data-tooltip="privacyTooltips('instance')"
        >
          <i class="small circle outline icon" />
        </span>
        <span
          v-else-if="library.privacy_level === 'everyone'"
          class="right floated"
          :data-tooltip="privacyTooltips('everyone')"
        >
          <i class="small globe icon" />
        </span>
      </h4>

      <!-- TODO: Does library have a description? Its schema has not. -->
      <!-- <div class="description">
        {{ library.description }}
        <div class="ui hidden divider" />
      </div> -->

      <div class="content">
        <i class="music icon" />
        {{ t('views.content.libraries.Card.meta.tracks', library.uploads_count) }}
      </div>
    </div>
    <!-- <div class="ui bottom basic attached buttons">
      <router-link
        :to="{name: 'library.detail.upload', params: {id: library.uuid}}"
        class="ui button"
      >
        {{ t('views.content.libraries.Card.button.upload') }}
      </router-link>
    </div> -->
  </fw-card>
</template>
