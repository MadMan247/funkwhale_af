<script setup lang="ts">
import type { FileSystem, FSEntry } from '~/types'

import { useVModel } from '@vueuse/core'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import Layout from '~/components/ui/Layout.vue'
import Button from '~/components/ui/Button.vue'
import Input from '~/components/ui/Input.vue'

interface Events {
  (e: 'update:modelValue', value: string[]): void
  (e: 'import'): void
}

interface Props {
  data: FileSystem
  loading: boolean
  modelValue: string[]
}

const { t } = useI18n()

const emit = defineEmits<Events>()
const props = defineProps<Props>()

const value = useVModel(props, 'modelValue', emit)
const handleClick = (entry: FSEntry) => {
  if (!entry.dir) return

  if (entry.name === '..') {
    value.value.pop()
    return
  }

  value.value.push(entry.name)
}
const path = computed(() => props.data.root + '/' + value.value.join('/'))
</script>

<template>
  <div :class="['ui', { loading }]">
    <Layout flex>
      <Input
        v-model="path"
      />
      <Button
        primary
        @click.prevent="emit('import')"
      >
        {{ t('components.library.FsBrowser.button.import') }}
      </Button>
    </Layout>
    <div class="ui list component-fs-browser">
      <a
        v-if="value.length > 0"
        class="item"
        href=""
        @click.prevent="handleClick({ name: '..', dir: true })"
      >
        <i class="bi bi-folder" />
        <div class="content">
          <div class="header doubledot symbol" />
        </div>
      </a>
      <a
        v-for="e in data.content"
        :key="e.name"
        class="item"
        href=""
        @click.prevent="handleClick(e)"
      >
        <i
          v-if="e.dir"
          class="bi bi-folder"
        />
        <i
          v-else
          class="bi bi-file-earmark-music-fill"
        />
        <div class="content">
          <div class="header">{{ e.name }}</div>
        </div>
      </a>
    </div>
  </div>
</template>
