import { AudioContext } from 'standardized-audio-context-mock'
import { vi } from 'vitest'

vi.mock('standardized-audio-context', () => ({
  AudioContext
}))

// Mock HTMLMediaElement methods for testing
Object.defineProperty(HTMLMediaElement.prototype, 'load', {
  configurable: true,
  value: vi.fn()
})

Object.defineProperty(HTMLMediaElement.prototype, 'play', {
  configurable: true,
  value: vi.fn().mockResolvedValue(undefined)
})

Object.defineProperty(HTMLMediaElement.prototype, 'pause', {
  configurable: true,
  value: vi.fn()
})

Object.defineProperty(HTMLMediaElement.prototype, 'addTextTrack', {
  configurable: true,
  value: vi.fn()
})
