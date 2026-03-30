import type { IAudioContext, IMediaElementAudioSourceNode } from 'standardized-audio-context'
import { isWebAudioRequested, currentGain, createAudioSource, connectAudioSource, getAudioContext } from '~/composables/audio/audio-api'

import { createEventHook, refDefault, type EventHookOn, useEventListener } from '@vueuse/core'
import { effectScope, reactive, ref, type Ref, watch } from 'vue'

import useLogger from '~/composables/useLogger'

const logger = useLogger()

export interface SoundSource {
  uuid: string
  mimetype: string
  url: string
}

export interface Sound {
  preload(): Promise<void>
  dispose(): Promise<void>

  readonly audioNode: IMediaElementAudioSourceNode<IAudioContext> | null
  readonly isErrored: Ref<boolean>
  readonly isLoaded: Ref<boolean>
  readonly isDisposed: Ref<boolean>
  readonly currentTime: number
  readonly playable: boolean
  readonly duration: number
  readonly buffered: number
  looping: boolean

  pause(): Promise<void>
  play(): Promise<void>

  seekTo(seconds: number): Promise<void>
  seekBy(seconds: number): Promise<void>

  onSoundLoop: EventHookOn<Sound>
  onSoundEnd: EventHookOn<Sound>
}

export const soundImplementations = reactive(new Set<Constructor<Sound>>())

export const registerSoundImplementation = <T extends Constructor<Sound>>(implementation: T) => {
  soundImplementations.add(implementation)
  return implementation
}

// Default Sound implementation
@registerSoundImplementation
export class HTMLSound implements Sound {
  #audio = new Audio()
  #soundLoopEventHook = createEventHook<HTMLSound>()
  #soundEndEventHook = createEventHook<HTMLSound>()
  #ignoreError = false
  #scope = effectScope()
  #sourceNode: IMediaElementAudioSourceNode<IAudioContext> | null = null

  readonly isErrored = ref(false)
  readonly isLoaded = ref(false)
  readonly isDisposed = ref(false)

  // Lazy-getter for audioNode to satisfy the Sound interface
  get audioNode(): IMediaElementAudioSourceNode<IAudioContext> | null {
    if (!this.#sourceNode && isWebAudioRequested.value) {
      this.#sourceNode = createAudioSource(this.#audio)
      connectAudioSource(this.#sourceNode)
    }
    return this.#sourceNode
  }

  onSoundLoop: EventHookOn<HTMLSound>
  onSoundEnd: EventHookOn<HTMLSound>

  constructor (sources: SoundSource[]) {
    this.onSoundLoop = this.#soundLoopEventHook.on
    this.onSoundEnd = this.#soundEndEventHook.on

    // TODO: Quality picker
    const source = sources[0]?.url
    if (!source) {
      this.isLoaded.value = true
      return
    }

    this.#audio.crossOrigin = 'anonymous'
    this.#audio.src = source
    this.#audio.preload = 'auto'

    logger.log('CREATED SOUND INSTANCE', this)

    this.#scope.run(() => {
      watch([isWebAudioRequested, currentGain], ([webAudio, gain]) => {
        if (webAudio || this.#sourceNode) {
          // Web Audio mode: force native volume to 1, route through AudioContext
          this.#audio.volume = 1
          // Note: The global GAIN_NODE.gain is already being updated by setGain() in audio-api.ts
          void this.audioNode
        } else {
          // Native mode: no source mode, audio goes directly to speakers
          this.#audio.volume = gain
        }
      }, { immediate: true })

      useEventListener(this.#audio, 'ended', () => this.#soundEndEventHook.trigger(this))

      useEventListener(this.#audio, 'timeupdate', () => {
        if (this.#audio.currentTime === 0) {
          this.#soundLoopEventHook.trigger(this)
        }
      })

      useEventListener(this.#audio, 'waiting', () => {
        logger.log('>> AUDIO WAITING', this)
      })

      useEventListener(this.#audio, 'playing', () => {
        logger.log('>> AUDIO PLAYING', this)
      })

      useEventListener(this.#audio, 'stalled', () => {
        logger.log('>> AUDIO STALLED', this)
      })

      useEventListener(this.#audio, 'suspend', () => {
        logger.log('>> AUDIO SUSPEND', this)
      })

      useEventListener(this.#audio, 'loadeddata', () => {
        // https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/readyState
        this.isLoaded.value = this.#audio.readyState >= 2
      })

      useEventListener(this.#audio, 'error', (err) => {
        if (this.#ignoreError) return
        logger.error('>> AUDIO ERRORED', err, this)
        this.isErrored.value = true
        this.isLoaded.value = true
      })
    })
  }

  #attachToDom () {
    if (typeof document !== 'undefined' && !this.#audio.parentNode) {
      document.body.appendChild(this.#audio)
    }
  }

  async preload () {
    this.isDisposed.value = false
    this.isErrored.value = false
    logger.log('CALLING PRELOAD ON', this)
    this.#audio.load()
  }

  async play () {
    try {
      // 1. Anchor to DOM to prevent iOS from killing the process on lock
      this.#attachToDom()

      // 2. Always resume AudioContext on play.
      // iOS requires a running AudioContext to reliably activate/refresh
      // MediaSession (lock screen) controls. Since we haven't called
      // createMediaElementSource yet in native mode, this is a "silent"
      // heartbeat that won't interfere with background playback.
      if (isWebAudioRequested.value && getAudioContext().state === 'suspended') {
        try {
          await getAudioContext().resume()
        } catch (resumeErr) {
          logger.log('>> AudioContext resume failed (usually a browser policy)', resumeErr)
        }
      }

      // 3. Ensure the element is ready to go
      if (this.#audio.readyState === 0) { // HAVE_NOTHING
        this.#audio.load()
      }

      // 4. Trigger the native playback
      await this.#audio.play()

    } catch (err: any) {
      // Logic: If the error is just a browser policy (like a missed user interaction)
      // or a quick skip (AbortError), we do NOT set isErrored.value to true.
      // This keeps the "Track cannot be loaded" overlay from appearing.
      const isInterrupted = err.name === 'NotAllowedError' || err.name === 'AbortError'

      if (!isInterrupted) {
        logger.error('>> AUDIO PLAY ERROR', err, this)
        this.isErrored.value = true
      } else {
        logger.log(`>> Playback interrupted/blocked: ${err.name}`)
      }
    }
  }

  async pause () {
    return this.#audio.pause()
  }

  async seekTo (seconds: number) {
    this.#audio.currentTime = seconds
  }

  async seekBy (seconds: number) {
    this.#audio.currentTime += seconds
  }

  get playable () {
    return this.#audio.src !== '' || this.isErrored.value
  }

  get duration () {
    const { duration } = this.#audio
    return isNaN(duration) ? 0 : duration
  }

  get buffered () {
    // https://developer.mozilla.org/en-US/docs/Web/Guide/Audio_and_video_delivery/buffering_seeking_time_ranges#creating_our_own_buffering_feedback
    if (this.duration > 0) {
      const { length } = this.#audio.buffered
      for (let i = 0; i < length; i++) {
        if (this.#audio.buffered.start(length - 1 - i) < this.#audio.currentTime) {
          return this.#audio.buffered.end(length - 1 - i)
        }
      }
    }

    return 0
  }

  get currentTime () {
    return this.#audio.currentTime
  }

  get looping () {
    return this.#audio.loop
  }

  set looping (value: boolean) {
    this.#audio.loop = value
  }

  async dispose () {
    if (this.isDisposed.value) return

    // Remove all event listeners
    this.#scope.stop()

    if (this.#sourceNode) {
      this.#sourceNode.disconnect()
      this.#sourceNode = null
    }

    if (this.#audio.parentNode) {
      this.#audio.parentNode.removeChild(this.#audio)
    }

    // Stop audio playback
    this.#audio.pause()
    this.#audio.src = ''
    this.#audio.load()
    this.isDisposed.value = true
  }
}

export const soundImplementation = refDefault(ref<Constructor<Sound>>(), HTMLSound)
