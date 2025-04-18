<script setup lang="ts">
import type { FSLogs } from '~/types'
import { useI18n } from 'vue-i18n'

interface Props {
  data: FSLogs
}

defineProps<Props>()

const { t } = useI18n()
</script>

<template>
  <div class="ui segment component-fs-logs">
    <div
      v-if="data.status === 'pending'"
      class="ui active dimmer"
    >
      <div class="ui text loader">
        {{ t('components.library.FsLogs.empty.notStarted') }}
      </div>
    </div>
    <template v-else>
      <p
        v-for="row in data.logs"
        :key="row"
      >
        {{ row }}
      </p>
    </template>
  </div>
</template>
