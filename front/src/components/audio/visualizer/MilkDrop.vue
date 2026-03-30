<script setup lang="ts">
import { useMilkDrop } from '~/composables/audio/visualizer'
import { isWebAudioRequested } from '~/composables/audio/audio-api'

import { onScopeDispose, ref, watch } from 'vue'
import { useRafFn } from '@vueuse/core'

const milkdrop = ref()
const canvas = ref()

const { visualizer, loadRandomPreset, render, isVisible } = useMilkDrop(canvas)

const { resume, pause } = useRafFn(render)

watch(isVisible, (visible) => visible
  ? resume()
  : pause()
)

onScopeDispose(() => {
  pause()
  // Auto-disable Web Audio when the component unmounts to return to Native Mode
  isWebAudioRequested.value = false

  if (visualizer.value) {
    visualizer.value.loseGLContext()
  }
})

defineExpose({
  loadRandomPreset
})

let autoPresetInterval: ReturnType<typeof setInterval> | null = null

function toggleAutoPreset() {
  if (autoPresetInterval) {
    clearInterval(autoPresetInterval)
    autoPresetInterval = null
  } else {
    autoPresetInterval = setInterval(() => {
      loadRandomPreset()
    }, 23000)
  }
}
</script>

<template>
  <div
    ref="milkdrop"
    class="visualizer"
  >
    <canvas
      ref="canvas"
      @click="loadRandomPreset()"
      @dblclick="toggleAutoPreset()"
    />
  </div>
</template>
