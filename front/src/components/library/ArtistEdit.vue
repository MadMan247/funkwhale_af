<script setup lang="ts">
import type { EditObjectType } from '~/composables/moderation/useEditConfigs'
import type { Artist, Library } from '~/types'
import { useI18n } from 'vue-i18n'

import { useStore } from '~/store'

import EditForm from '~/components/library/EditForm.vue'
import Section from '~/components/ui/Section.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Layout from '~/components/ui/Layout.vue'
import Alert from '~/components/ui/Alert.vue'

interface Props {
  objectType: EditObjectType
  object: Artist
  libraries?: Library[]
}

defineProps<Props>()

const { t } = useI18n()
const store = useStore()

const canEdit = store.state.auth.availablePermissions.library
</script>

<template>
  <Layout stack>
    <Spacer />
    <Section
      align-left
      :h2="canEdit
        ? t('components.library.ArtistEdit.header.edit')
        : t('components.library.ArtistEdit.header.suggest')
      "
    />
    <Alert
      v-if="!object.is_local"
      yellow
    >
      {{ t('components.library.ArtistEdit.message.remote') }}
    </Alert>
    <!-- TODO: Check if we need to load the corresponding Actor (field: `attributed_to`) -->
    <edit-form
      v-else
      :object-type="objectType"
      :object="{ ...object, attributed_to: undefined }"
    />
  </Layout>
</template>
