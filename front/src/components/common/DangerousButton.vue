<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

import Button from '~/components/ui/Button.vue'
import Modal from '~/components/ui/Modal.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Layout from '~/components/ui/Layout.vue'
import PopoverItem from '~/components/ui/popover/PopoverItem.vue'

interface Events {
  (e: 'confirm'): void
}

// Note that properties such as [disabled] and 'destructive' | 'primary' are inherited.
const props = defineProps<{
  title?: string
  action?:() => void,
  confirmColor?:'success' | 'danger',
  popoverItem?: boolean
}>()

const { t } = useI18n()

const emit = defineEmits<Events>()

const showModal = ref(false)

const canceled = ref(false)

const confirm = () => {
  showModal.value = false
  emit('confirm')
  props.action?.()
}
</script>

<template>
  <component
    :is="props.popoverItem ? PopoverItem : Button"
    :keep-open="props.popoverItem"
    icon="bi-exclamation-octagon-fill"
    destructive
    v-bind="$attrs"
    @click.prevent.stop="showModal = !showModal"
  >
    <!-- default slot: Button content -->
    <slot />
    <Modal
      v-if="!props.popoverItem"
      v-model="showModal"
      :title="title || t('components.common.DangerousButton.header.confirm')"
      :cancel="t('components.common.DangerousButton.button.cancel')"
    >
      <Layout
        flex
        style="flex-wrap: nowrap;
        align-items: center;"
      >
        <i
          class="bi bi-exclamation-octagon  destructive ghost"
          style="font-size: 6rem;"
        />
        <div>
          <slot name="content" />
        </div>
      </Layout>
      <template #actions>
        <Spacer grow />
        <Button
          ghost
          v-bind="{[{success: 'primary', danger: 'destructive'}[confirmColor || 'danger']]: true}"
          @click="confirm"
        >
          <slot name="confirm">
            {{ t('components.common.DangerousButton.button.confirm') }}
          </slot>
        </Button>
      </template>
    </Modal>
  </component>
  <template v-if="props.popoverItem && showModal">
    <Layout>
      <hr>
      <div
        v-if="$slots.content"
        style="font-size: 1rem;"
      >
        <slot name="content" />
      </div>
      <Layout
        flex
        gap-8
      >
        <Button
          v-bind="{[{success: 'primary', danger: 'destructive'}[confirmColor || 'danger']]: true}"
          @click="confirm"
        >
          <slot name="confirm">
            {{ t('components.common.DangerousButton.button.confirm') }}
          </slot>
        </Button>
        <Spacer
          h
          grow
        />
        <Button
          secondary
          raised
          solid
          autofocus
          @click="showModal = false; canceled = true;"
        >
          <slot name="cancel">
            {{ t('components.common.DangerousButton.button.cancel') }}
          </slot>
        </Button>
      </Layout>
    </Layout>
  </template>
</template>
