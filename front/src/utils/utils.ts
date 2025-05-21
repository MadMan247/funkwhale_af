import type { Track, Album, ArtistCredit, QueueItemSource } from '~/types'
import type { components } from '~/generated/types'
import type { QueueTrack } from '~/composables/audio/queue'
import store from '~/store'


export function generateTrackCreditString (track: Track | Album | null): string | null {
  if (!track || !track.artist_credit || track.artist_credit.length === 0) {
    return null
  }

  const artistCredits = track.artist_credit.map((ac: ArtistCredit) => {
    return ac.artist.name + (ac.joinphrase ? ` ${ac.joinphrase}` : '')
  })

  return artistCredits.join('')
}

export function generateTrackCreditStringFromQueue (track: QueueTrack | QueueItemSource | null): string | null {
  if (!track || !track.artistCredit || track.artistCredit.length === 0) {
    return null
  }

  const artistCredits = track.artistCredit.map((ac: ArtistCredit) => {
    return ac.artist.name + (ac.joinphrase ? ` ${ac.joinphrase}` : '')
  })

  return artistCredits.join('')
}

export function getArtistCoverUrl (artistCredits: ArtistCredit[]): string | undefined {
  for (const artistCredit of artistCredits) {
    const mediumSquareCrop = getSimpleArtistCoverUrl(artistCredit.artist, 'medium_square_crop')

    if (mediumSquareCrop) {
      return store.getters['instance/absoluteUrl'](mediumSquareCrop)
    }
  }
  return undefined
}

const getSimpleArtistCover = (artist: components['schemas']['SimpleChannelArtist'] | components['schemas']['Artist'] | components['schemas']['ArtistWithAlbums']) =>
  (field: 'original' | 'small_square_crop' | 'medium_square_crop' | 'large_square_crop') =>
    artist.cover
      ? (field in artist.cover ? artist.cover.urls[field] : null)
      : null

/** Returns the absolute Url of this artist's cover on this instance
 *
 * @param artist: a simple artist
 * @param field: the size you want
*/
export const getSimpleArtistCoverUrl = (
  artist: components['schemas']['SimpleChannelArtist'] | components['schemas']['Artist'] | components['schemas']['ArtistWithAlbums'],
  field: 'original' | 'small_square_crop' | 'medium_square_crop' | 'large_square_crop'
): string | null => {
  const coverGetter = getSimpleArtistCover(artist);
  if (!coverGetter) return null;

  const cover = coverGetter(field);
  if (!cover) return null;

  return store.getters['instance/absoluteUrl'](cover);
};
