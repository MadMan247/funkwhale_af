<script setup lang="ts">
import type { Radio } from '~/types'

import { ref, computed } from 'vue'
import { useStore } from '~/store'
import { useI18n } from 'vue-i18n'

import UserLink from '~/components/common/UserLink.vue'

import RadioButton from './Button.vue'
import Card from '~/components/ui/Card.vue'
import Button from '~/components/ui/Button.vue'
import Spacer from '~/components/ui/Spacer.vue'

interface Props {
  type: string
  customRadio?: Radio | null
  objectId?: string | null
}

const { t } = useI18n()

const props = withDefaults(defineProps<Props>(), {
  customRadio: null,
  objectId: null
})

const store = useStore()

const isDescriptionExpanded = ref(false)

const radio = computed(() => props.customRadio
  ? props.customRadio
  : store.getters['radios/types'][props.type]
)

const customRadioId = computed(() => props.customRadio?.id ?? null)
</script>

<template>
  <Card
    v-if="radio.id"
    small
    blue
    :title="radio.name"
    :to="{name: 'library.radios.detail', params: {id: radio.id}}"
  >
    <template #topright>
      <radio-button
        :type="type"
        :custom-radio-id="customRadioId"
        :object-id="objectId"
        play-only
      />
    </template>

    <template #default>
      <UserLink
        v-if="radio.user"
        :user="radio.user"
        :avatar="false"
      />
      <Spacer />
      <div
        class="description"
        :class="{expanded: isDescriptionExpanded}"
        @click="isDescriptionExpanded = !isDescriptionExpanded"
      >
        {{ radio.description }}
      </div>
    </template>

    <template #action>
      <Button
        v-if="store.state.auth.authenticated && type === 'custom' && radio.user.id === store.state.auth.profile?.id"
        primary
        full
        grow
        :to="{name: 'library.radios.edit', params: {id: customRadioId }}"
      >
        {{ t('components.radios.Card.button.edit') }}
      </Button>
    </template>
  </Card>
  <Card
    v-else
    small
    solid
    blue
    icon="bi-boombox-fill"
    :title="radio.name"
  >
    <template #default>
      <UserLink
        v-if="radio.user"
        :user="radio.user"
        :avatar="false"
      />
      <Spacer v-if="radio.user" />
      <div
        class="description"
        :class="{expanded: isDescriptionExpanded}"
        @click="isDescriptionExpanded = !isDescriptionExpanded"
      >
        {{ radio.description }}
      </div>
    </template>

    <template #action>
      <radio-button
        :type="type"
        :custom-radio-id="customRadioId"
        :object-id="objectId"
        grow
      />
      <Button
        v-if="store.state.auth.authenticated && type === 'custom' && radio.user.id === store.state.auth.profile?.id"
        secondary
        :to="{name: 'library.radios.edit', params: {id: customRadioId }}"
      >
        {{ t('components.radios.Card.button.edit') }}
      </Button>
    </template>
  </Card>
</template>

<style lang="scss" scoped>
.play-button.is-icon-only {
  top: 16px;
  right: 16px;
}
h6.title {
  font-size: 3em;
}
</style>
