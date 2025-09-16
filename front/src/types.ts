import type { App } from 'vue'
import type { Store } from 'vuex'
import type { Router } from 'vue-router'
import type { AxiosError } from 'axios'
import type { RootState } from '~/store'

// App types are synced from the backend. Run `yarn update-schema`.
import { type components } from '~/generated/types.ts'

// eslint-disable-next-line
import type { ComponentPublicInstance } from '@vue/runtime-core'
import type { QueueTrack } from '~/composables/audio/queue'

export type FunctionRef = Element | ComponentPublicInstance | null

// App structure stuff
export interface InitModuleContext {
  app: App
  router: Router
  store: Store<RootState>
}

export type InitModule = (ctx: InitModuleContext) => void | Promise<void>

export interface QueueItemSource extends QueueTrack {
  key: string

  labels: {
    remove: string
    selectTrack: string
    favorite: string
  }
}

// Theme stuff
export type Theme = 'auto' | 'light' | 'dark'

export interface ThemeEntry {
  icon: string
  name: string
  key: Theme
}

// Track stuff
export type ContentCategory = 'podcast' | 'music'

// Use backend-defined schema types

export type Actor = components['schemas']['FullActor']
export type Activity = components['schemas']['Activity']
export type Album = components['schemas']['Album']
export type ArtistCredit = components['schemas']['ArtistCredit']
export type Channel = components['schemas']['Channel']
export type Library = components['schemas']['Library']
export type License = components['schemas']['License']
export type Listening = components['schemas']['Listening']
export type Playlist = components['schemas']['Playlist']
export type PlaylistTrack = components['schemas']['PlaylistTrack']
export type PrivacyLevelEnum = components['schemas']['PrivacyLevelEnum']
export type LibraryPrivacyLevelEnum = components['schemas']['LibraryPrivacyLevelEnum']
export type Radio = components['schemas']['Radio']
export type SearchResult = components['schemas']['SearchResult']
export type Tag = components['schemas']['Tag']
export type Track = components['schemas']['Track']
export type Usage = components['schemas']['Usage']
export type LibraryScan = components['schemas']['LibraryScan']
export type LibraryFollow = components['schemas']['LibraryFollow']
export type Cover = components['schemas']['CoverField']
export type RateLimitStatus = components['schemas']['RateLimit']['scopes'][number]
export type PaginatedAlbumList = components['schemas']['PaginatedAlbumList']
export type PaginatedChannelList = components['schemas']['PaginatedChannelList']
export type UserTrackFavorite = components['schemas']['UserTrackFavorite']

export type Artist = components['schemas']['Artist']


export type ImportStatus = components['schemas']['ImportStatusEnum']

// TODO: Find out which type: `Follow` or `LibraryFollow`
// export interface UserFollow {
//   uuid: string
//   approved: boolean

//   name: string
//   type?: 'federation.Actor' | 'federation.UserFollow'
//   target?: Actor
// }

// API stuff
// eslint-disable-next-line
export interface APIErrorResponse extends Record<string, APIErrorResponse | string | string[] | { code: string }[]> {}

export interface BackendError extends AxiosError {
  isHandled: boolean
  backendErrors: string[]
  rawPayload?: APIErrorResponse
}

// Backend response now contains pagination fields.
// Example: PaginatedArtistWithAlbumsList
// Example: PaginatedAlbumsList
export interface BackendResponse<T> {
  count: number
  results: T[]
}

// WebSocket stuff

// FS Browser
export interface FSEntry {
  dir: boolean
  name: string
}

export interface FileSystem {
  root: boolean
  content: FSEntry[]
  import: FSLogs
}

export interface FSLogs {
  status: 'pending' | 'started'
  reference: unknown
  logs: string[]
}

// Content stuff
export interface Content {
  content_type: 'text/plain' | 'text/markdown'
  text: string
}

// Form stuff
export interface FormField {
  label: string
  input_type: 'short_text' | 'long_text'
  required: boolean
}

export interface Form {
  fields: FormField[]
  help_text: Content
}

// Upload stuff
export interface Upload {
  id: number
  uuid: string
  filename?: string
  source?: string
  duration?: number
  mimetype: string
  extension: string
  listen_url: string
  bitrate?: number
  size?: number

  import_status: ImportStatus
  import_details?: {
    detail: object
    error_code: string
  }

  import_metadata?: Record<string, string> & { tags?: string[] }
}

// Profile stuff
// export interface Actor {
//   id: number
//   fid?: string
//   name?: string
//   icon?: Cover
//   summary: string
//   preferred_username: string
//   full_username: string
//   is_local: boolean
//   domain: string
// }

export interface User {
  id: number
  avatar?: Cover
  email: string
  summary: { text: string, content_type: string }
  username: string
  full_username: string
  instance_support_message_display_date: string
  funkwhale_support_message_display_date: string
  is_superuser: boolean
  privacy_level: PrivacyLevelEnum
}

// Settings stuff
export type SettingsId = 'instance'
export interface SettingsGroup {
  label: string
  id: SettingsId
  settings: SettingsField[]
}

export interface SettingsField {
  name: string
  fieldType?: 'markdown'
  fieldParams?: {
    charLimit: number | null
    permissive: boolean
  }
}

export interface SettingsDataEntry {
  identifier: string
  fieldType: string
  fieldParams: object
  help_text: string
  verbose_name: string
  value: unknown
  field: {
    class: string
    widget: {
      class: string
    }
  }

  additional_data: {
    choices: [string, string]
  }
}

// Note stuff
export interface Note {
  uuid: string
  type: 'request' | 'report'
  author?: Actor
  summary?: string
  creation_date?: string
}

// Instance policy stuff
export interface InstancePolicy {
  id: number
  uuid: string
  creation_date: string
  actor: Actor

  summary: string
  is_active: boolean
  block_all: boolean
  silence_activity: boolean
  silence_notifications: boolean
  reject_media: boolean
}

// Plugin stuff
export interface Plugin {
  name: string
  label: string
  homepage?: string
  enabled: boolean
  description?: string
  source?: string
  values?: Record<string, any>
  conf?: {
    name: string
    label: string
    type: 'text' | 'long_text' | 'url' | 'password' | 'boolean'
    help?: string
  }[]
}

// Report stuff
export type EntityObjectType = 'artist' | 'album' | 'track' | 'library' | 'playlist' | 'account' | 'channel'

export interface ReportTarget {
  id: number
  type: EntityObjectType
}

export type ReviewStatePayload = { value: unknown } | Partial<Artist> | Partial<Album> | Partial<Track>
export interface ReviewState {
  [id: string]: ReviewStatePayload
}

export interface Review {
  uuid: string
  is_applied: boolean | null
  is_approved: boolean | null
  created_by: Actor
  previous_state: ReviewState
  payload: ReviewState
  target?: ReportTarget & {
    type: 'artist' | 'album' | 'track'
    repr: string
  }
  creation_date: string
  summary?: string
  type: 'update'
}

export interface Report {
  uuid: string
  summary?: string
  is_applied: boolean
  is_handled: boolean
  previous_state: string
  notes: Note[]
  type: string

  assigned_to?: Actor
  submitter?: Actor
  submitter_email?: string

  target_owner?: Actor
  target?: ReportTarget
  target_state: {
    _target: ReportTarget
    domain: string
    [k: string]: unknown
  }

  creation_date: string
  handled_date: string
}

// User request stuff
export type UserRequestStatus = 'approved' | 'refused' | 'pending'
export interface UserRequest {
  uuid: string
  notes: Note[]
  status: UserRequestStatus

  assigned_to?: Actor
  submitter?: Actor
  submitter_email?: string

  creation_date: string
  handled_date: string

  metadata: Record<string, string>
}

// Notification stuff
export interface Notification {
  id: number
  is_read: boolean
  activity: Activity
}

// Application stuff
export interface Application {
  client_id: string
  name: string
  redirect_uris: string
  scopes: string
  client_secret: string

  // This is actually a date string
  created: string
}
