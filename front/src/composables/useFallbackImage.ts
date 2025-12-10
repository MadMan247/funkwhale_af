import { getCurrentInstance } from 'vue'
import type { Artist, Track, TrackAlbum } from '~/types'

export function useFallbackImage() {
  const onCoverError = (e: Event, obj: Track | TrackAlbum | Artist) => {
    const img = e.target as HTMLImageElement
    if (!img) return

    const cover = obj.cover?.urls
    if (!cover) return

    img.onerror = null // prevent infinite loop
    const store = getCurrentInstance()?.appContext.config.globalProperties.$store
    if (!store) return

    img.src = store.getters['instance/absoluteUrl'](cover.medium_square_crop)
  }

  return { onCoverError }
}
