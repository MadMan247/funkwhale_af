import type { Track, Artist, Album, Playlist, Library, Channel, Actor } from '~/types'
import type { components } from '~/generated/types'
import type { ContentFilter } from '~/store/moderation'

import { computed, markRaw, ref } from 'vue'
import { i18n } from '~/init/locale'
import { useStore } from '~/store'

import { usePlayer } from '~/composables/audio/player'
import { useQueue } from '~/composables/audio/queue'

import axios from 'axios'

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
}

export default (props: PlayOptionsProps) => {
  const { enqueue: addToQueue, currentTrack, playNext, currentIndex, enqueueAt, queue, clear, playTrack } = useQueue()
  const { isPlaying } = usePlayer()
  const store = useStore()

  const playable = computed(() => {
    if (props.isPlayable) {
      return true
    }

    if (props.track) {
      return props.track.uploads?.length > 0
    } else if (props.artist) {
      // TODO: Find out how to get tracks, album from Artist

      /*
      return props.artist.tracks_count > 0
        || props.artist?.albums?.some((album) => album.is_playable === true)
      */
    } else if (props.tracks) {
      return props.tracks?.some((track) => (track.uploads?.length ?? 0) > 0)
    }

    return false
  })

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

  const getTracksPage = async (params: object, page = 1, tracks: Track[] = []): Promise<Track[]> => {
    if (page > 11) {
      // it's 10 * 100 tracks already, let's stop here
      return tracks
    }

    // when fetching artists/or album tracks, sometimes, we may have to fetch
    // multiple pages
    const response = await axios.get('tracks/', {
      params: {
        ...params,
        page_size: 100,
        page,
        hidden: '',
        playable: true
      }
    })

    tracks.push(...response.data.results)
    if (response.data.next) {
      return getTracksPage(params, page + 1, tracks)
    }

    return tracks
  }

  const isLoading = ref(false)
  const getPlayableTracks = async () => {
    isLoading.value = true

    const tracks: Track[] = []

    // TODO (wvffle): Why is there no channel?
    if (props.tracks?.length) {
      tracks.push(...props.tracks)
    } else if (props.track) {
      if (props.track.uploads?.length) {
        tracks.push(props.track)
      } else {
        // fetch uploads from api
        const response = await axios.get(`tracks/${props.track.id}/`)
        tracks.push(response.data as Track)
      }
    } else if (props.playlist) {
      const response = await axios.get(`playlists/${props.playlist.uuid}/tracks/`)
      const playlistTracks = (response.data.results as Array<{ track: Track }>).map(({ track }) => track as Track)

      const artistIds = store.getters['moderation/artistFilters']().map((filter: ContentFilter) => filter.target.id)
      if (artistIds.length) {
        tracks.push(...playlistTracks.filter((track) => {
          return !((track.artist_credit?.some(ac => artistIds.includes(ac.artist.id)) || track.album) && track.album?.artist_credit?.some(ac => artistIds.includes(ac.artist.id)))
        }))
      } else {
        tracks.push(...playlistTracks)
      }
    } else if (props.artist) {
      tracks.push(...await getTracksPage({ artist: props.artist.id, include_channels: 'true', ordering: 'album__release_date,disc_number,position' }))
    } else if (props.album) {
      tracks.push(...await getTracksPage({ album: props.album.id, include_channels: 'true', ordering: 'disc_number,position' }))
    } else if (props.library) {
      tracks.push(...await getTracksPage({ library: props.library.uuid, ordering: '-creation_date' }))
    }

    isLoading.value = false

    return tracks.filter(track => track.uploads?.length).map(markRaw)
  }

  // const el = useCurrentElement()

  const enqueue = async () => {
    const tracks = await getPlayableTracks()
    await addToQueue(...tracks)
    addMessage(tracks)
  }

  const enqueueNext = async (next = false) => {
    const tracks = await getPlayableTracks()

    const wasEmpty = queue.value.length === 0
    await enqueueAt(currentIndex.value + 1, ...tracks)

    if (next && !wasEmpty) {
      await playNext()
      isPlaying.value = true
    }

    addMessage(tracks)
  }

  const replacePlay = async (index?: number) => {
    await clear()
    const tracksToPlay = await getPlayableTracks()
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
    const libraryUrl = playlist.library;
  if (!libraryUrl) {
    throw new Error("Playlist library URL is missing.");
  }
  const libResponse = await axios.get(libraryUrl);
  const id = libResponse.data?.id || libResponse.data?.results?.id;
  if (!id) {
    throw new Error("Library id not found in response.");
  }
  const fetchResponse = await axios.post('federation/fetches',
    { object_uri: id }
  );
  if (!fetchResponse.data.object) {
    throw new Error("Library object not found in response. Probably fetch could not find it on remote");
  }
  const response = await axios.post(
    'federation/follows/library',
    { target: fetchResponse.data.object.id.split('/').filter(Boolean).pop() }
  );

    //  to commit to store or update the playlist idk how
  return response;
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
