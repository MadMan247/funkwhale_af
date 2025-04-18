<script setup lang="ts">
import { SUPPORTED_LOCALES, setI18nLanguage } from '~/init/locale'
import { useI18n } from 'vue-i18n'

import { useModal } from '~/ui/composables/useModal.ts'

import Modal from '~/components/ui/Modal.vue'
import Button from '~/components/ui/Button.vue'
import Layout from '~/components/ui/Layout.vue'

const { t, locale } = useI18n()

const isOpen = useModal('language').isOpen
</script>

<template>
  <Modal
    v-model="isOpen"
    over-popover
    :title="t('components.common.UserMenu.label.language')"
  >
    <Layout
      columns
      column-width="200px"
    >
      <Button
        v-for="(language, key) in SUPPORTED_LOCALES"
        :key="key"
        ghost
        thin-font
        small
        align-text="left"
        :aria-pressed="key===locale || undefined"
        @click="setI18nLanguage(key)"
      >
        {{ language }}
      </Button>
    </Layout>
  </Modal>
</template>

<style module>
  .description {
    font-size: 0.875em;
  }
</style>
