<script setup lang="ts">
import type { EditObject, EditObjectType } from '~/composables/moderation/useEditConfigs'
import type { Library } from '~/types'

import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

import store from '~/store'
import axios from 'axios'

import useErrorHandler from '~/composables/useErrorHandler'
import EditForm from '~/components/library/EditForm.vue'

import Loader from '~/components/ui/Loader.vue'
import Header from '~/components/ui/Header.vue'
import Alert from '~/components/ui/Alert.vue'

interface Props {
  objectType: EditObjectType
  object: EditObject
  libraries: Library[] | null
}

withDefaults(defineProps<Props>(), {
  libraries: null
})

const { t } = useI18n()

const canEdit = store.state.auth.availablePermissions.library

const isLoadingLicenses = ref(false)
const licenses = ref([])
const fetchLicenses = async () => {
  isLoadingLicenses.value = true

  try {
    const response = await axios.get('licenses/')
    licenses.value = response.data.results
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoadingLicenses.value = false
}

fetchLicenses()
</script>

<template>
  <Header :h2="canEdit ? t('components.library.TrackEdit.header.edit') : t('components.library.TrackEdit.header.suggest')" />
  <Alert
    v-if="!object.is_local"
    yellow
  >
    {{ t('components.library.TrackEdit.message.remote') }}
  </Alert>
  <edit-form
    v-else-if="!isLoadingLicenses"
    :object-type="objectType"
    :object="object"
    :can-edit="canEdit"
    :licenses="licenses"
  />
  <Loader v-else />
</template>
