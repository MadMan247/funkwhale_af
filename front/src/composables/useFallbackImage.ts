import type { Artist, Track, TrackAlbum } from '~/types'
import { useStore } from '~/store'


export function useFallbackImage() {
  const store = useStore()

  const onCoverError = (e: Event, obj: Track | TrackAlbum | Artist) => {
    const img = e.target as HTMLImageElement
    if (!img) return
    if (!store) return
    const cover = obj.cover?.urls
    // here we could add the default image, but the actual ugly image allow to see there is data loss on the server.
    if (!cover) return

    // Prevent infinite loop
    if (img.dataset.size == "medium_square_crop") return
    img.dataset.size = 'medium_square_crop'

    img.src = store.getters['instance/absoluteUrl'](cover.medium_square_crop)

  }

  return { onCoverError }
}
