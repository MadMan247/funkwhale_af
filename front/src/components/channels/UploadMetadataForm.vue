<script setup lang="ts">
import type { Upload, Track } from '~/types'

import { reactive, computed, watch, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import AttachmentInput from '~/components/common/AttachmentInput.vue'

import Input from '~/components/ui/Input.vue'
import Pills from '~/components/ui/Pills.vue'

type Values = Pick<Track, 'title' | 'position' | 'tags'> & { cover: string | null, description: string }
interface Events {
  (e: 'update:values', values: Values): void
}

interface Props {
  upload: Upload
  values?: Partial<Values> | null
}

const { t } = useI18n()

const emit = defineEmits<Events>()
const props = withDefaults(defineProps<Props>(), {
  values: null
})

// TODO: Make Tags work
type Item = { type: 'custom' | 'preset', label: string }
type tagsModel = {
  currents: Item[],
  others?: Item[],
}

const tags = ref<tagsModel>({
  currents: [],
  others: []
})

// TODO: check if `position: 0` is a good default
const newValues = reactive<Values>({
  position: 0,
  description: '',
  title: '',
  tags: tags.value.currents.map(tag => tag.label),
  cover: null,
  ...(props.values ?? props.upload.import_metadata ?? {})
})

const isLoading = computed(() => !props.upload)
watch(newValues, (values) => emit('update:values', values), { immediate: true })
</script>

<template>
  <Layout
    form
    :class="[{loading: isLoading}]"
  >
    <Input
      v-model="newValues.title"
      :label="t('components.channels.UploadMetadataForm.label.title')"
      required
    />
    <attachment-input
      v-model="newValues.cover"
      @delete="newValues.cover = ''"
    >
      {{ t('components.channels.UploadMetadataForm.label.image') }}
    </attachment-input>
    <label for="upload-tags">
      {{ t('components.channels.UploadMetadataForm.label.tags') }}
    </label>
    <!-- TODO: Make Tags work -->
    <Pills
      :get="(v) => { tags = v }"
      :set="() => tags"
      label="Custom Tags"
      cancel="Cancel"
    />
    <Spacer />
    <Input
      v-model="newValues.position"
      type="number"
      min="1"
      step="1"
      :label="t('components.channels.UploadMetadataForm.label.position')"
    />
    <label for="upload-description">
      {{ t('components.channels.UploadMetadataForm.label.description') }}
    </label>
    <content-form
      v-model="newValues.description"
      field-id="upload-description"
    />
  </Layout>
</template>
