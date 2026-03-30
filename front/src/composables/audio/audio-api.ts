import type { IAudioContext, IMediaElementAudioSourceNode } from 'standardized-audio-context'

import { AudioContext } from 'standardized-audio-context'
import { ref } from 'vue'

// 1. Toggle for Web Audio (Turn this on only for Milkdrop)
export const isWebAudioRequested = ref(false)

// Track the gain value globally so Native and Web Audio can share it
export const currentGain = ref(1)

let _AUDIO_CONTEXT: AudioContext | null = null
let _GAIN_NODE: ReturnType<AudioContext['createGain']> | null = null

export const getAudioContext = (): AudioContext => {
  if (!_AUDIO_CONTEXT) {
    _AUDIO_CONTEXT = new AudioContext()
    _GAIN_NODE = _AUDIO_CONTEXT.createGain()
    _GAIN_NODE.gain.value = currentGain.value
    _GAIN_NODE.connect(_AUDIO_CONTEXT.destination)
  }
  return _AUDIO_CONTEXT
}

export const getGainNode = () => {
  getAudioContext() // ensure initialized
  return _GAIN_NODE!
}

// Connect Gain Node
export const setGain = (value: number) => {
  const safeValue = Math.max(0, Math.min(value, 1))
  currentGain.value = safeValue
  if (_GAIN_NODE) _GAIN_NODE.gain.value = safeValue
  // if AudioContext not yet created, currentGain will be applied on creation
}

// TODO (wvffle): Create equalizer filters
const getEqualizerFilters = () => [getGainNode()]

export const createAudioSource = (sourceElement: HTMLAudioElement): IMediaElementAudioSourceNode<IAudioContext> | null => {
  if (!isWebAudioRequested.value) return null
  return getAudioContext().createMediaElementSource(sourceElement)
}

let lastNode: IMediaElementAudioSourceNode<IAudioContext> | null = null
export const connectAudioSource = (sourceNode: IMediaElementAudioSourceNode<IAudioContext> | null) => {
  if (sourceNode === null) return
  for (const filter of getEqualizerFilters()) {
    try { lastNode?.disconnect(filter) } catch (e) { /* ignore */ }
    sourceNode.connect(filter)
  }
  lastNode = sourceNode
}
