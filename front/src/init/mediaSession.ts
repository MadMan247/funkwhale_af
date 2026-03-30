import type { InitModule } from '~/types'
import { watch } from 'vue'
import { useQueue } from '~/composables/audio/queue'
import { usePlayer } from '~/composables/audio/player'
import { isWebAudioRequested, getAudioContext } from '~/composables/audio/audio-api'

export let resetHandlers: () => void = () => {}
export let refreshMetadata: () => void = () => {}

window.addEventListener('beforeunload', () => {
  navigator.mediaSession.metadata = null
  navigator.mediaSession.playbackState = 'none'
  navigator.mediaSession.setActionHandler('seekto', null)
  navigator.mediaSession.setActionHandler('nexttrack', null)
  navigator.mediaSession.setActionHandler('previoustrack', null)
})

export const install: InitModule = ({ store }) => {
  const { currentTrack, playNext, playPrevious } = useQueue()
  const { isPlaying, seekTo, pauseReason, PauseReason, currentTime, duration } = usePlayer()

  if (!('mediaSession' in navigator)) return

  // Play/pause controls
  navigator.mediaSession.setActionHandler('play', async () => {
    if (isWebAudioRequested.value && getAudioContext().state === 'suspended') {
      await getAudioContext().resume()
    }
    isPlaying.value = true
  })

  navigator.mediaSession.setActionHandler('pause', () => {
    isPlaying.value = false
    pauseReason.value = PauseReason.MediaSession
  })

  // Sync playback state to lockscreen
  watch(isPlaying, (playing) => {
    navigator.mediaSession.playbackState = playing ? 'playing' : 'paused'
  }, { immediate: true })

  // Keep lockscreen state alive in background where Vue reactivity is throttled
  setInterval(() => {
    navigator.mediaSession.playbackState = isPlaying.value ? 'playing' : 'paused'
    if (isPlaying.value) updatePositionState()
  }, 1000)


  // iOS only activates MediaSession controls (next/prev/seekto) once an audio
  // session is established — registering them at init time is too early.
  // We defer registration until duration is known, which means audio is playing.
  let handlersRegistered = false
  watch(duration, (dur) => {
    if (dur > 0) {
      updatePositionState()

      if (!handlersRegistered) {
        registerHandlers()

        // Explicitly set seekforward/seekbackward to null so iOS shows
        // next/previous track buttons instead of seek buttons
        navigator.mediaSession.setActionHandler('seekforward', null)
        navigator.mediaSession.setActionHandler('seekbackward', null)

        navigator.mediaSession.setActionHandler('nexttrack', () => playNext())
        navigator.mediaSession.setActionHandler('previoustrack', () => playPrevious())

        // seekto enables scrubbing from the lockscreen progress bar
        navigator.mediaSession.setActionHandler('seekto', async (details) => {
          if (details.seekTime !== undefined) {
            await seekTo(details.seekTime)
            updatePositionState()
          }
        })
      }
    }
  })

  const registerHandlers = () => {
    handlersRegistered = true
    navigator.mediaSession.setActionHandler('seekforward', null)
    navigator.mediaSession.setActionHandler('seekbackward', null)
    navigator.mediaSession.setActionHandler('nexttrack', () => playNext())
    navigator.mediaSession.setActionHandler('previoustrack', () => playPrevious())
    navigator.mediaSession.setActionHandler('seekto', async (details) => {
      if (details.seekTime !== undefined) {
        await seekTo(details.seekTime)
        updatePositionState()
      }
    })
  }

  resetHandlers = () => {
    handlersRegistered = false
    // Clear all handlers so iOS resets the session
    navigator.mediaSession.setActionHandler('seekto', null)
    navigator.mediaSession.setActionHandler('nexttrack', null)
    navigator.mediaSession.setActionHandler('previoustrack', null)
    navigator.mediaSession.metadata = null
  }

  refreshMetadata = () => {
    const track = currentTrack.value
    if (!track) {
      navigator.mediaSession.metadata = null
      return
    }
    const absoluteCoverUrl = store.getters['instance/absoluteUrl'](track.coverUrl)
    const artistName = track.artistCredit?.map(ac => ac.artist.name).join(', ') || 'Unknown Artist'
    navigator.mediaSession.metadata = new window.MediaMetadata({
      title: track.title,
      artist: artistName,
      album: track.albumTitle || '',
      artwork: [
        { src: absoluteCoverUrl, sizes: '512x512', type: 'image/jpeg' },
        { src: absoluteCoverUrl, sizes: '1024x1024', type: 'image/jpeg' }
      ]
    })
  }


  function updatePositionState() {
    const dur = duration.value
    const pos = currentTime.value
    // iOS disables all lockscreen controls if duration is 0 or invalid
    if (!dur || dur <= 0) return
    if (pos < 0 || pos > dur) return
    try {
      navigator.mediaSession.setPositionState({
        duration: dur,
        playbackRate: 1,
        position: pos
      })
    } catch (e) {
      // Ignore race conditions during track transitions
    }
  }

  // Update lockscreen metadata when track changes
  watch(currentTrack, refreshMetadata, { immediate: true })
}
