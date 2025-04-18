<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

import Button from '~/components/ui/Button.vue'
import Modal from '~/components/ui/Modal.vue'
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

const confirm = () => {
  showModal.value = false
  emit('confirm')
  props.action?.()
}
</script>

<template>
  <component
    :is="props.popoverItem ? PopoverItem : Button"
    destructive
    v-bind="$attrs"
    @click.prevent.stop="showModal = true"
  >
    <slot />

    <Modal
      v-model="showModal"
      destructive
      :title="title || t('components.common.DangerousButton.header.confirm')"
      :cancel="t('components.common.DangerousButton.button.cancel')"
    >
      <div class="scrolling content">
        <div class="description">
          <slot name="modal-content" />
        </div>
      </div>
      <template #actions>
        <Button
          v-bind="{[{success: 'primary', danger: 'destructive'}[confirmColor || 'danger']]: true}"
          @click="confirm"
        >
          <slot name="modal-confirm">
            {{ t('components.common.DangerousButton.button.confirm') }}
          </slot>
        </Button>
      </template>
    </Modal>
  </component>
</template>
