<script setup lang="ts">
import type { ComponentProps } from 'vue-component-type-helpers'
import type { Radio } from '~/types'

import { useI18n } from 'vue-i18n'

import Card from '~/components/ui/Card.vue'
import PlayButton from '~/components/audio/PlayButton.vue'

const { t } = useI18n()

const play = defineEmit<[radio: Radio]>()
const { radio, small, ...cardProps } = defineProps<{
  radio: Radio
  small?: boolean
} & ComponentProps<typeof Card>>()
</script>

<template>
  <Card
    v-bind="cardProps"
    :title="radio.name"
    class="radio-card"
    :to="/* TODO: get correct route here */ ''"
  >
    <template #image>
      <div class="cover-name">
        {{ t('vui.radio') }}
      </div>
    </template>

    <PlayButton @play="play(radio)" />

    <div
      v-if="!small"
      class="radio-description"
    >
      {{ radio.description }}
    </div>
  </Card>
</template>

<style lang="scss">
@import './style.scss'
</style>
