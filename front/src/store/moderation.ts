import type { Module } from 'vuex'
import type { RootState } from '~/store/index'

import axios from 'axios'
import { sortBy } from 'lodash-es'
import useLogger from '~/composables/useLogger'

export interface State {
  filters: ContentFilter[]
  actorFilters: ActorFilter[]
  showFilterModal: boolean
  showReportModal: boolean
  lastUpdate: Date,
  filterModalTarget: {
    type: null
    target: null | { id: string, name: string }
  }
  reportModalTarget: {
    type: null | 'channel'
    target: null
    typeLabel: string
    label: string
    _obj?: {
      fid?: string
      actor?: { fid: string }
    }
  }
}

export interface ContentFilter {
  uuid: string
  creation_date: Date
  target: {
    type: 'artist'
    id: number
  }
}

export interface ActorFilter {
  name: string
  full_username: string
}

const logger = useLogger()

const store: Module<State, RootState> = {
  namespaced: true,
  state: {
    filters: [],
    actorFilters: [],
    showFilterModal: false,
    showReportModal: false,
    lastUpdate: new Date(),
    filterModalTarget: {
      type: null,
      target: null
    },
    reportModalTarget: {
      type: null,
      target: null,
      typeLabel: '',
      label: ''
    }
  },
  mutations: {
    filterModalTarget (state, value) {
      state.filterModalTarget = value
    },
    reportModalTarget (state, value) {
      state.reportModalTarget = value
    },
    empty (state) {
      state.filters = []
      state.actorFilters = []
    },
    contentFilter (state, value) {
      state.filters.push(value)
    },
    showFilterModal (state, value) {
      state.showFilterModal = value
      if (!value) {
        state.filterModalTarget = {
          type: null,
          target: null
        }
      }
    },
    showReportModal (state, value) {
      state.showReportModal = value
      if (!value) {
        state.reportModalTarget = {
          type: null,
          target: null,
          typeLabel: '',
          label: ''
        }
      }
    },
    reset (state) {
      state.filters = []
      state.actorFilters = []
      state.filterModalTarget = {
        type: null,
        target: null
      }
      state.showFilterModal = false
      state.showReportModal = false
      state.reportModalTarget = {
        type: null,
        target: null,
        typeLabel: '',
        label: ''
      }
    },
    deleteContentFilter (state, uuid) {
      state.filters = state.filters.filter((e) => {
        return e.uuid !== uuid
      })
    },
    addActorFilter (state, filter: ActorFilter) {
      state.actorFilters = [...state.actorFilters, filter]
    },
    deleteActorFilter (state, fullUsername) {
      state.actorFilters = state.actorFilters.filter((e) => e.full_username !== fullUsername)
    }
  },
  getters: {
    artistFilters: (state) => () => {
      const filters = state.filters.filter((filter) => filter.target.type === 'artist')
      const sorted = sortBy(filters, [(e) => { return e.creation_date }])
      return sorted.reverse()
    },
    actorFilters: (state) => () => {
      return state.actorFilters
    }
  },
  actions: {
    hide ({ commit }, payload: State['filterModalTarget']) {
      commit('filterModalTarget', payload)
      commit('showFilterModal', true)
    },
    report ({ commit }, payload) {
      commit('reportModalTarget', payload)
      commit('showReportModal', true)
    },
    async fetchContentFilters ({ dispatch, commit }, url) {
      const params = url
        ? {}
        : {
            page_size: 100,
            ordering: '-creation_date'
          }

      if (!url) commit('empty')
      const response = await axios.get(url ?? 'moderation/content-filters/', { params })

      logger.info(`Fetched a batch of ${response.data.results.length} filters`)

      for (const result of response.data.results) {
        commit('contentFilter', result)
      }

      if (response.data.next) {
        await dispatch('fetchContentFilters', response.data.next)
      }
    },
    async deleteContentFilter ({ commit }, uuid) {
      return axios.delete(`moderation/content-filters/${uuid}/`).then(() => {
        commit('deleteContentFilter', uuid)
      })
    },
    async fetchActorFilters ({ dispatch, commit }, url) {

      if (!url) commit('empty')
      const username = this.state.auth.fullUsername
      const response = await axios.get(url ?? `federation/actors/${username}/blocks/`, {
        params: {
          name: username
        }
      })
      logger.info(`Fetched a batch of ${response.data.results.length} actor filters`)

      for (const result of response.data.results) {
        commit('addActorFilter', { ...result })
      }
      if (response.data.next) {
        await dispatch('fetchActorFilters', response.data.next)
      }
    },
    async blockActor ({ commit }, name) {
      return axios.post(`federation/actors/${name}/block/`).then(() => {
        const preferred = name.split('@')[0]
        commit('addActorFilter', { name: preferred, full_username: name })
        logger.info(`Blocked actor ${name}`)
      })
    },
    async deleteActorFilter ({ commit }, fullUsername) {
      return axios.post(`federation/actors/${fullUsername}/unblock/`).then(() => {
        commit('deleteActorFilter', fullUsername)
        logger.info(`Unblocked actor ${fullUsername}`)
      })
    }
  }
}

export default store
