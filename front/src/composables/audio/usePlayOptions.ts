import type { Actor, Album, Artist, Channel, Library, Playlist, PlaylistTrack, Track } from '~/types'
import type { components, operations } from '~/generated/types'
import type { ContentFilter } from '~/store/moderation'

import { computed, type ComputedGetter, markRaw, onUnmounted, ref, type UnwrapRef, watchEffect } from 'vue'
import { i18n } from '~/init/locale'
import { useStore } from '~/store'

import { usePlayer } from '~/composables/audio/player'
import { useQueue } from '~/composables/audio/queue'

import axios, { type AxiosResponse, CanceledError } from 'axios'

export interface PlayOptionsProps {
  isPlayable?: boolean
  tracks?: Track[]
  track?: Track | null
  artist?: Artist | components["schemas"]["SimpleChannelArtist"] | components['schemas']['ArtistWithAlbums'] | null
  album?: Album | null
  playlist?: Playlist | null
  library?: Library | null
  channel?: Channel | null
  account?: Actor | components['schemas']['APIActor'] | null
  /**
   * isOpen is a flag that usePlayOptions watches. When true, usePlayOptions eagerly downloads the track list
   * for the given object.
   */
  isOpen?: boolean
}

/**
 * once wraps an expensive async function prepared by the given getter. It returns a wrapper that may invoke the async
 * function. It ensures then async function runs at most once unless it rejects or the refs it requires change. If
 * either happens, once may invoke the async function again.
 *
 * The async function should _not_ access reactive values because these accesses cannot be tracked. Instead, follow this
 * pattern:
 *
 * @example
 *
 * once(() => {
 *   const { album, artist, track } = props // Read from reactive objects here.
 *   return async ({ signal }) => {
 *     // Use the values here.
 *     // This will be called once unless the reactive values change or it rejects.
 *     // You can forward the signal to Axios, for example.
 *   }
 * }
 */
const once = <Return>(
  setup: ComputedGetter<(opts: { signal: AbortSignal }) => Promise<Return>>
) => {
  const disposed = new AbortController()
  onUnmounted(() => { disposed.abort(new CanceledError() )})

  const fnRef = computed(setup)
  let fn: UnwrapRef<typeof fnRef> | undefined

  // job and abort are bound together; when we called fn we gave it abort's signal.
  // Therefore, we might cancel job's side effects using abort.
  let job: Promise<Return> | undefined
  let abort: AbortController

  watchEffect(() => {
    fn = fnRef.value
    job = undefined
    abort?.abort(new CanceledError())
  })

  return () => {
    if (job == null) {
      job = new Promise((res, rej) => {
        disposed.signal.throwIfAborted()
        abort = new AbortController()
        disposed.signal.addEventListener('abort', () => abort.abort(disposed.signal.reason))
        abort.signal.addEventListener('abort', () => { rej(abort.signal.reason) })
        fn?.({ signal: abort.signal }).then(res, rej)
      })

      // If the job rejects, discard it.
      job.catch(() => { job = undefined })
    }

    return job
  }
}

export default (props: PlayOptionsProps) => {
  const { enqueue: addToQueue, currentTrack, playNext, currentIndex, enqueueAt, queue, clear, playTrack } = useQueue()
  const { isPlaying } = usePlayer()
  const store = useStore()
  const playableTracks = ref<Track[]>()

  const abort = new AbortController()
  onUnmounted(() => abort.abort())

  watchEffect(() => {
    if (!abort.signal.aborted && props.isOpen) {
      // Eagerly load the tracks.
      void getPlayableTracks()
    }
  })

  const playable = computed(() =>
    // TODO: Find out how to get tracks, album from Artist
    props.isPlayable
      || (props.track?.uploads.length ?? 0) > 0
      || playableTracks.value == null // Still loading tracks
      || playableTracks.value.some((track) => (track.uploads?.length ?? 0) > 0)
      || (props.tracks ?? []).some((track) => (track.uploads?.length ?? 0) > 0)
  )

  const filterableArtist = computed(() => {
    const artists = []
    if (props.track?.artist_credit) {
      props.track.artist_credit.forEach(ac => {
        if (ac.artist) {
          artists.push(ac.artist)
        }
      })
    }
    if (props.album?.artist_credit) {
      props.album.artist_credit.forEach(ac => {
        if (ac.artist) {
          artists.push(ac.artist)
        }
      })
    }
    if (props.artist) {
      artists.push(props.artist)
    }

    return artists
  })

  const filterArtist = async () => store.dispatch('moderation/hide', { type: 'artist', target: filterableArtist.value })

  const addMessage = (tracks: Track[]) => {
    if (!tracks.length) {
      return
    }

    const { t } = i18n.global
    store.commit('ui/addMessage', {
      content: t('composables.audio.usePlayOptions.addToQueueMessage', tracks.length),
      date: new Date()
    })
  }

  type GetTrackParams = operations['get_tracks']['parameters']['query']
  type GetPlaylistTracksParams = operations['get_playlist_tracks']['parameters']['query']
  interface GetTracksPage {
    (url: `tracks/${string}`, opts?: { params?: GetTrackParams, signal?: AbortSignal }): Promise<Track[]>
    (url: `playlists/${string}`, opts?: { params?: GetPlaylistTracksParams, signal?: AbortSignal }): Promise<PlaylistTrack[]>
  }

  const getTracksPage: GetTracksPage = async (
    url: string,
    opts?: {
      params?: GetTrackParams | GetPlaylistTracksParams,
      signal?: AbortSignal
    }
  ): Promise<any[]> => {
    const out: any[] = []

    // when fetching artists/or album tracks, sometimes, we may have to fetch
    // multiple pages. fetch at most 11 pages
    for(let page = 1; url != null && page <= 11; ++page) {
      const { data: { results, next } }: AxiosResponse<
        components['schemas']['PaginatedTrackList']
        | components['schemas']['PaginatedPlaylistTrackList']
      > = await axios.get(url, {
        paramsSerializer: {
          indexes: null
        },
        params: {
          page_size: 100,
          hidden: '',
          playable: true,
          ...opts?.params
        },
        signal: opts?.signal ?? abort.signal
      })

      out.push(...results)

      if (next == null) {
        break
      }

      url = next
    }

    return out
  }

  const isLoading = ref(false)

  let getPlayableTracks: () => Track[] | Promise<Track[]>

  if (props.tracks != null || (props.track != null && (props.track.uploads?.length ?? 0) > 0)) {
    // Fast path: in this context, we already know the track or tracks to play.
    getPlayableTracks = () => {
      const { tracks = [], track } = props
      let out: Track[] | undefined

      if (tracks.length > 0) {
        out = tracks
      } else if (track != null) {
        out = [track]
      } else {
        out = []
      }

      return out.filter(track => (track.uploads?.length ?? 0) > 0).map(markRaw)
    }
  } else {
    // Slow path: we must fetch the track or tracks from the server. This retrieves the track list given the current
    // context (an album, an artist, a playlist). It will only fire once unless the previous call failed.
    getPlayableTracks = once(() => {
      const {
        track,
        playlist,
        artist,
        album,
        library
      } = props

      return async ({ signal }) => {
        const getTracks = async (): Promise<Track[]> => {
          // TODO (wvffle): Why is there no channel?
          if (track != null) {
            // fetch uploads from api
            const response = await axios.get(`tracks/${track.id}/`, { signal })
            return [response.data as Track]
          } else if (playlist != null) {
            const playlistTracks = (await getTracksPage(`playlists/${playlist.uuid}/tracks/`, { signal })).map((item) => item.track as unknown as Track) // TODO: What the heck? Why does the API have 'string' here?
            const artistIds = store.getters['moderation/artistFilters']().map((filter: ContentFilter) => filter.target.id)
            return artistIds.length === 0
              ? playlistTracks
              : playlistTracks.filter(track => !(
                (track.artist_credit?.some(ac => artistIds.includes(ac.artist.id)) || track.album)
                && track.album?.artist_credit?.some(ac => artistIds.includes(ac.artist.id))
              ))
          } else if (artist != null) {
            return getTracksPage('tracks/', { params: { artist: String(artist.id), include_channels: true, ordering: ['album__release_date', 'disc_number', 'position'] } })
          } else if (album != null) {
            return getTracksPage('tracks/', { params: { album: album.id, include_channels: true, ordering: ['disc_number', 'position'] } })
          } else if (library != null) {
            return getTracksPage('tracks/', { params: { library: library.uuid, ordering: ['-creation_date'] } })
          } else {
            return []
          }
        }

        return getTracks().then(
          tracks => tracks.filter((track) => track.uploads?.length).map(markRaw),
          e => e instanceof CanceledError ? [] : Promise.reject(e)
        )
      }
    })
  }

  // const el = useCurrentElement()

  const enqueue = async () => {
    const tracks = await getPlayableTracks()
    if (tracks.length <= 0) {
      return
    }
    await addToQueue(...tracks)
    addMessage(tracks)
  }

  const enqueueNext = async (next = false) => {
    const tracks = await getPlayableTracks()
    if (tracks.length <= 0) {
      return
    }

    const wasEmpty = queue.value.length === 0
    await enqueueAt(currentIndex.value + 1, ...tracks)
    if (next && !wasEmpty) {
      await playNext()
      isPlaying.value = true
    }
    addMessage(tracks)
  }

  const replacePlay = async (index?: number) => {
    const tracksToPlay = await getPlayableTracks()
    if (tracksToPlay.length <= 0) {
      return
    }
    await clear()
    await addToQueue(...tracksToPlay)
    if (props.track && props.tracks?.length) {
      const trackIndex = index ?? props.tracks?.findIndex(track => track.id === props.track?.id && track.position === props.track?.position) ?? 0
      await playTrack(trackIndex)
      isPlaying.value = true
    } else {
      await playTrack(0, true)
      isPlaying.value = true
    }
    addMessage(tracksToPlay)
  }

  const activateTrack = async (track: Track, index: number) => {
    if (track.id === currentTrack.value?.id && track.position === currentTrack.value?.position) {
      isPlaying.value = true
    }

    return replacePlay(index)
  }

  const requestPlaylistUploadsAccess = async (playlist: Playlist) => {
    const libraryUrl = playlist.library
    if (!libraryUrl) {
      throw new Error('Playlist library URL is missing.')
    }
    const libResponse = await axios.get(libraryUrl)
    const id = libResponse.data?.id || libResponse.data?.results?.id
    if (!id) {
      throw new Error('Library id not found in response.')
    }
    const fetchResponse = await axios.post('federation/fetches', { object_uri: id })
    if (!fetchResponse.data.object) {
      throw new Error('Library object not found in response. Probably fetch could not find it on remote')
    }

    //  to commit to store or update the playlist idk how
    return await axios.post('federation/follows/library', {
      target: fetchResponse.data.object.id.split('/').filter(Boolean).pop()
    })
  };

  return {
    playable,
    filterableArtist,
    filterArtist,
    enqueue,
    enqueueNext,
    replacePlay,
    activateTrack,
    isLoading,
    requestPlaylistUploadsAccess
  }
}
