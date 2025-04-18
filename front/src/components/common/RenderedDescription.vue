<script setup lang="ts">
import type { BackendError } from '~/types'

import { ref, computed } from 'vue'
import { whenever } from '@vueuse/core'
import { useI18n } from 'vue-i18n'

import axios from 'axios'
import clip from 'text-clipper'

import Layout from '~/components/ui/Layout.vue'
import Button from '~/components/ui/Button.vue'
import Alert from '~/components/ui/Alert.vue'

interface Events {
  (e: 'updated', data: unknown): void
}

interface Props {
  content?: { text?: string, html?: string } | null
  fieldName?: string
  updateUrl?: string
  canUpdate?: boolean
  fetchHtml?: boolean
  permissive?: boolean
  truncateLength?: number
  moreLink?: boolean
}

const { t } = useI18n()

const emit = defineEmits<Events>()
const props = withDefaults(defineProps<Props>(), {
  content: null,
  fieldName: 'description',
  updateUrl: '',
  canUpdate: true,
  fetchHtml: false,
  permissive: false,
  truncateLength: 200,
  moreLink: true
})

const preview = ref('')
const fetchPreview = async () => {
  const response = await axios.post('text-preview/', { text: props.content?.text ?? '', permissive: props.permissive })
  preview.value = response.data.rendered
}

whenever(() => props.fetchHtml, fetchPreview)

const truncatedHtml = computed(() => clip(props.content?.html ?? '', props.truncateLength, {
  html: true,
  maxLines: 3
}))

const showMore = ref(false)

// Truncated or full Html or an empty string
const html = computed(() => props.fetchHtml
  ? preview.value
  : props.truncateLength > 0 && !showMore.value
    ? truncatedHtml.value
    : props.content?.html ?? ''
)

const isTruncated = computed(() => props.truncateLength > 0 && truncatedHtml.value.length < (props.content?.html ?? '').length)

const isUpdating = ref(false)
const text = ref(props.content?.text ?? '')
const isLoading = ref(false)
const errors = ref([] as string[])
const submit = async () => {
  errors.value = []
  isLoading.value = true

  try {
    const response = await axios.patch(props.updateUrl, {
      [props.fieldName]: text.value
        ? { content_type: 'text/markdown', text: text.value }
        : null
    })

    emit('updated', response.data)
    isUpdating.value = false
  } catch (error) {
    errors.value = (error as BackendError).backendErrors
  }

  isLoading.value = false
}
</script>

<template>
  <Layout
    v-if="content && !isUpdating"
    flex
    gap-4
  >
    <!-- Render the truncated or full description -->
    <sanitized-html
      :html="html"
      :class="['description', isTruncated ? 'truncated' : '']"
    />

    <!-- Display the `show more` / `show less` button -->

    <template v-if="isTruncated">
      <a
        v-if="showMore === false && props.moreLink !== false"
        class="more"
        style="align-self: flex-end; color: var(--fw-primary);"
        href=""
        @click.stop.prevent="showMore = true"
      >
        {{ t('components.common.RenderedDescription.button.more') }}
      </a>
      <a
        v-else-if="props.moreLink !== false"
        class="more"
        style="align-self: center; color: var(--fw-primary);"
        href=""
        @click.stop.prevent="showMore = false"
      >
        {{ t('components.common.RenderedDescription.button.less') }}
      </a>
    </template>
  </Layout>
  <span v-else-if="!isUpdating">
    {{ t('components.common.RenderedDescription.empty.noDescription') }}
  </span>

  <!-- [DISABLED] Display an edit form -->
  <!-- TODO: Check if we want to revive in-situ editing here -->

  <form
    v-if="isUpdating"
    @submit.prevent="submit()"
  >
    <Alert
      v-if="errors.length > 0"
      red
      title="{{ t('components.common.RenderedDescription.header.failure') }}"
      role="alert"
    >
      <ul class="list">
        <li
          v-for="(error, key) in errors"
          :key="key"
        >
          {{ error }}
        </li>
      </ul>
    </Alert>
    <content-form
      v-model="text"
      :autofocus="true"
    />
    <Button
      class="left floated"
      solid
      secondary
      @click.prevent="isUpdating = false"
    >
      {{ t('components.common.RenderedDescription.button.cancel') }}
    </Button>
    <Button
      :class="['ui', {'loading': isLoading}, 'right', 'floated', 'button']"
      type="submit"
      :disabled="isLoading"
      solid
      primary
    >
      {{ t('components.common.RenderedDescription.button.update') }}
    </Button>
  </form>
</template>

<style lang="scss" scoped>
  .description {
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    white-space: normal;
    &.truncated {
      -webkit-line-clamp: 1; /* Number of lines to show */
      line-clamp: 1;
      max-height: 72px;
      flex-shrink: 1;
    }
  }
</style>
