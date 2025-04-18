<script setup lang="ts">
import type { Playlist, BackendError } from '~/types'
import type { components } from '~/generated/types'

import { useVModels } from '@vueuse/core'
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'

import axios from 'axios'

import useSharedLabels from '~/composables/locale/useSharedLabels'
import useLogger from '~/composables/useLogger'

import Layout from '~/components/ui/Layout.vue'
import Alert from '~/components/ui/Alert.vue'
import Button from '~/components/ui/Button.vue'
import Input from '~/components/ui/Input.vue'
import Slider from '~/components/ui/Slider.vue'

interface Events {
  (e: 'update:playlist', value: Playlist): void
}

interface Props {
  title?: boolean
  create?: boolean
  playlist?: Playlist | null
}

const emit = defineEmits<Events>()
const props = withDefaults(defineProps<Props>(), {
  title: true,
  create: false,
  playlist: null
})

const { playlist } = useVModels(props, emit)

const logger = useLogger()

const errors = ref([] as string[])
const success = ref(false)

const store = useStore()
const name = ref(playlist.value?.name ?? '')
const privacyLevel = ref(playlist.value?.privacy_level ?? store.state.auth.profile?.privacy_level ?? 'me')
const description = ref(playlist.value?.description ?? '')

const { t } = useI18n()
const labels = computed(() => ({
  placeholder: t('components.playlists.Form.placeholder.name')
}))

const sharedLabels = useSharedLabels()
const privacyLevelChoices = {
  me: sharedLabels.fields.privacy_level.choices.me,
  instance: sharedLabels.fields.privacy_level.choices.instance,
  followers: sharedLabels.fields.privacy_level.choices.followers,
  everyone: sharedLabels.fields.privacy_level.choices.everyone
} as const satisfies Record<components['schemas']['PrivacyLevelEnum'], string>

const isLoading = ref(false)
const submit = async () => {
  isLoading.value = true
  success.value = false
  errors.value = []

  try {
    const url = props.create ? 'playlists/' : `playlists/${playlist.value?.id}/`
    const method = props.create ? 'post' : 'patch'

    const data = {
      name: name.value,
      privacy_level: privacyLevel.value,
      description: description.value
    }

    const response = await axios.request({ method, url, data })
    success.value = true

    if (props.create) {
      name.value = ''
    } else {
      playlist.value = response.data
    }

    store.dispatch('playlists/fetchOwn')
  } catch (error) {
    logger.error('Error while creating playlist')
    errors.value = (error as BackendError).backendErrors
  }

  isLoading.value = false
}

</script>

<template>
  <Layout
    form
    @submit.prevent="submit()"
  >
    <h3
      v-if="title"
    >
      {{ t('components.playlists.Form.header.createPlaylist') }}
    </h3>
    <Alert
      v-if="success"
      green
    >
      <h4 class="header">
        <template v-if="playlist">
          {{ t('components.playlists.Form.header.updateSuccess') }}
        </template>
        <template v-else>
          {{ t('components.playlists.Form.header.createSuccess') }}
        </template>
      </h4>
    </Alert>
    <Alert
      v-if="errors.length > 0"
      red
      role="alert"
    >
      <h4 class="header">
        {{ t('components.playlists.Form.header.createFailure') }}
      </h4>
      <ul class="list">
        <li
          v-for="(error, key) in errors"
          :key="key"
        >
          {{ error }}
        </li>
      </ul>
    </Alert>
    <div class="field">
      <label for="playlist-name">{{ t('components.playlists.Form.label.name') }}</label>
      <Input
        id="playlist-name"
        v-model="name"
        name="name"
        required
        type="text"
        :placeholder="labels.placeholder"
      />
    </div>
    <div class="field">
      <Slider
        v-model="privacyLevel"
        :options="privacyLevelChoices"
        :label="t('components.playlists.Form.label.visibility')"
      />
    </div>
    <!-- TODO: Add description to model and types -->
    <div class="field">
      <ContentForm
        v-model="description"
        :placeholder="t('components.playlists.Form.placeholder.description')"
        :rows="3"
        :max-length="500"
      />
    </div>
    <div class="field">
      <span id="updatePlaylistLabel" />
      <Button
        primary
        :class="['ui', 'fluid', {'loading': isLoading}, 'button']"
        type="submit"
      >
        <template v-if="playlist">
          {{ t('components.playlists.Form.button.update') }}
        </template>
        <template v-else>
          {{ t('components.playlists.Form.button.create') }}
        </template>
      </Button>
    </div>
  </Layout>
</template>
