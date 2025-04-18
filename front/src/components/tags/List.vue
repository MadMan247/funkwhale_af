<script setup lang="ts">
import { truncate } from '~/utils/filters'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import Layout from '~/components/ui/Layout.vue'
import Pill from '~/components/ui/Pill.vue'

interface Props {
  tags: string[]
  showMore?: boolean
  truncateSize?: number
  limit?: number
  labelClasses?: string
  detailRoute?: string
}

const props = withDefaults(defineProps<Props>(), {
  showMore: true,
  truncateSize: 25,
  limit: 5,
  labelClasses: '',
  detailRoute: 'library.tags.detail'
})

const { t } = useI18n()
const honorLimit = ref(true)

const tags = computed(() => {
  if (!honorLimit.value) {
    return props.tags
  }

  return props.tags.slice(0, props.limit)
})
</script>

<template>
  <Layout
    flex
    gap-16
    class="component-tags-list"
  >
    <router-link
      v-for="tag in tags"
      :key="tag"
      :to="{name: props.detailRoute, params: { id: tag } }"
      :class="props.labelClasses"
      style="text-decoration: none;"
    >
      <Pill raised>
        {{ `#${truncate(tag, props.truncateSize)}` }}
      </Pill>
    </router-link>
    <Pill
      v-if="props.showMore && tags.length < props.tags.length"
      @click.prevent="honorLimit = false"
    >
      {{ t('components.tags.List.button.more', props.tags.length - tags.length) }}
    </Pill>
  </Layout>
</template>
