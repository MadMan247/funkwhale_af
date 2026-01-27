import type { Module } from 'vuex'
import type { RootState } from '~/store/index'

import axios from 'axios'
import useLogger from '~/composables/useLogger'

export interface State {
  followsByActor: {
    [key: string]: Follow
  }
  count: number
  incomingFollows: Follow[]
}

interface Follow {
    uuid: string
  }
const logger = useLogger()

const store: Module<State, RootState> = {
  namespaced: true,
  state: {
    followsByActor: {},
    count: 0,
    incomingFollows: []
  },
  mutations: {
    follows: (state, { actorFid, follow }) => {
      if (follow) {
        state.followsByActor[actorFid] = follow
      } else {
        delete state.followsByActor[actorFid]
      }

      state.count = Object.keys(state.followsByActor).length
    },
    incomingFollows: (state, follows) => {
      state.incomingFollows = follows
    },
    reset (state) {
      state.followsByActor = {}
      state.count = 0
      state.incomingFollows = []
    }
  },
  getters: {
    follow: (state) => (actorFid: string) => {
      return state.followsByActor[actorFid]
    },
    incomingFollow: (state) => (actorFid: string) => {
      return state.incomingFollows.find((f: any) => f.actor?.fid === actorFid)
    }
  },
  actions: {
    set ({ commit, state }, { actorFid, value }) {
      if (value) {
        return axios.post('federation/follows/user/', { target: actorFid }).then((response) => {
          logger.info('Successfully subscribed to actor')
          commit('follows', { actorFid, follow: response.data })
        }, () => {
          logger.info('Error while subscribing to actor')
          commit('follows', { actorFid, follow: null })
        })
      } else {
        const follow = state.followsByActor[actorFid]!
        return axios.delete(`federation/follows/user/${follow.uuid}/`).then(() => {
          logger.info('Successfully unsubscribed from actor')
          commit('follows', { actorFid, follow: null })
        }, () => {
          logger.info('Error while unsubscribing from actor')
          commit('follows', { actorFid, follow })
        })
      }
    },
    toggle ({ getters, dispatch }, actorFid) {
      return dispatch('set', { actorFid, value: !getters.follow(actorFid) })
    },
    async fetchFollows ({ commit }, url) {
      try {
        const response = await axios.get('federation/follows/user/all/')
        for (const result of response.data.results) {
          const actorFid = result.actor
          commit('follows', { actorFid, follow: result })
        }
        return response.data
      } catch (error) {
        logger.error('Failed to fetch follows:', error)
        throw error
      }
    },
    async fetchIncomingFollows ({ commit, rootState }) {
      try {
        const response = await axios.get('federation/follows/user/', {
          params: {
            target: rootState.auth.profile?.id
          }
        })
        commit('incomingFollows', response.data.results)
        return response.data
      } catch (error) {
        logger.error('Failed to fetch incoming follows:', error)
        throw error
      }
    }
  }
}

export default store
