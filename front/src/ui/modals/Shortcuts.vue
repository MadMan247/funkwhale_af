<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import onKeyboardShortcut from '~/composables/onKeyboardShortcut'

import { useModal } from '~/ui/composables/useModal.ts'

import Modal from '~/components/ui/Modal.vue'
import Button from '~/components/ui/Button.vue'
import Layout from '~/components/ui/Layout.vue'
import Spacer from '~/components/ui/Spacer.vue'

const { t } = useI18n()

const isOpen = useModal('shortcuts').isOpen

onKeyboardShortcut('h', (() => { isOpen.value = !isOpen.value }))

const general = computed(() => [
  {
    title: t('components.ShortcutsModal.shortcut.general.label'),
    shortcuts: [
      {
        key: 'h',
        summary: t('components.ShortcutsModal.shortcut.general.show')
      },
      {
        key: 'shift + f',
        summary: t('components.ShortcutsModal.shortcut.general.focus')
      },
      {
        key: '/',
        summary: t('components.ShortcutsModal.shortcut.general.focus')
      },
      {
        key: 'esc',
        summary: t('components.ShortcutsModal.shortcut.general.unfocus')
      }
    ]
  }
])

const player = computed(() => [
  {
    title: t('components.ShortcutsModal.shortcut.audio.label'),
    shortcuts: [
      {
        key: 'p',
        summary: t('components.ShortcutsModal.shortcut.audio.playPause')
      },
      {
        key: 'left',
        summary: t('components.ShortcutsModal.shortcut.audio.seekBack5')
      },
      {
        key: 'right',
        summary: t('components.ShortcutsModal.shortcut.audio.seekForward5')
      },
      {
        key: 'shift + left',
        summary: t('components.ShortcutsModal.shortcut.audio.seekBack30')
      },
      {
        key: 'shift + right',
        summary: t('components.ShortcutsModal.shortcut.audio.seekForward30')
      },
      {
        key: 'ctrl + shift + left',
        summary: t('components.ShortcutsModal.shortcut.audio.playPrevious')
      },
      {
        key: 'ctrl + shift + right',
        summary: t('components.ShortcutsModal.shortcut.audio.playNext')
      },
      {
        key: 'shift + up',
        summary: t('components.ShortcutsModal.shortcut.audio.increaseVolume')
      },
      {
        key: 'shift + down',
        summary: t('components.ShortcutsModal.shortcut.audio.decreaseVolume')
      },
      {
        key: 'm',
        summary: t('components.ShortcutsModal.shortcut.audio.toggleMute')
      },
      {
        key: 'e',
        summary: t('components.ShortcutsModal.shortcut.audio.expandQueue')
      },
      {
        key: 'l',
        summary: t('components.ShortcutsModal.shortcut.audio.toggleLoop')
      },
      {
        key: 's',
        summary: t('components.ShortcutsModal.shortcut.audio.shuffleQueue')
      },
      {
        key: 'q',
        summary: t('components.ShortcutsModal.shortcut.audio.clearQueue')
      },
      {
        key: 'f',
        summary: t('components.ShortcutsModal.shortcut.audio.toggleFavorite')
      }
    ]
  }
])
</script>

<template>
  <Modal
    v-model="isOpen"
    :priority="10"
    :title="t('components.ShortcutsModal.header.modal')"
  >
    <Layout grid="auto / repeat(auto-fit, minmax(min-content, max(calc(50% - 16px), 367px)))">
      <div
        v-for="section in player"
        :key="section.title"
      >
        <h3 style="margin-top: 0px;">
          {{ section.title }}
        </h3>
        <layout
          stack
          no-gap
        >
          <template
            v-for="shortcut in section.shortcuts"
            :key="shortcut.summary"
          >
            <layout flex>
              <span
                :class="$style.description"
                style="align-self: center;"
              >{{ shortcut.summary }}</span>
              <Spacer grow />
              <Button
                style="pointer-events: none;"
                min-content
              >
                {{ shortcut.key }}
              </Button>
            </layout>
            <hr>
          </template>
        </layout>
      </div>
      <div
        v-for="section in general"
        :key="section.title"
      >
        <h3 style="margin-top: 0px;">
          {{ section.title }}
        </h3>
        <layout
          stack
          no-gap
        >
          <div
            v-for="shortcut in section.shortcuts"
            :key="shortcut.summary"
          >
            <layout flex>
              <span
                :class="$style.description"
                style="align-self: center;"
              >{{ shortcut.summary }}</span>
              <Spacer grow />
              <Button
                style="pointer-events:none;"
                min-content
              >
                {{ shortcut.key }}
              </Button>
            </layout>
            <hr>
          </div>
        </layout>
      </div>
    </Layout>
  </Modal>
</template>

<style module>
  .description {
    font-size: 0.875em;
  }
</style>
