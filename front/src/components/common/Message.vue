<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useStore } from '~/store'
import Alert from '~/components/ui/Alert.vue'

interface Message {
  content: string
  key: string
  color?: 'blue' | 'red' | 'purple' | 'green' | 'yellow'
  error?: boolean | string
  date?: Date
}

const props = defineProps<{ message: Message }>()
const isVisible = ref(true)
const store = useStore()

const messageColor = computed(() => {
  if (props.message.color) {
    return props.message.color
  }

  if (props.message.error || props.message.content?.toLowerCase().includes('error')) {
    return 'red'
  }

  return 'blue'
})

onMounted(() => {
  setTimeout(() => {
    isVisible.value = false
    store.commit('ui/removeMessage', props.message.key)
  }, 5000)
})
</script>

<template>
  <Transition name="fade">
    <Alert
      v-if="isVisible"
      role="alert"
      :[messageColor]="true"
      class="is-notification"
    >
      {{ message.content }}
    </Alert>
  </Transition>
</template>
