import type { Module } from 'vuex'
import type { RootState } from '~/store/index'

import axios from 'axios'
import useLogger from '~/composables/useLogger'

export interface State {
  followsByActor: {
    [key: string]: Follow
  }
  count: number
}

interface Follow {
    uuid: string
  }
const logger = useLogger()

const store: Module<State, RootState> = {
  namespaced: true,
  state: {
    followsByActor: {},
    count: 0
  },
  mutations: {
    follows: (state, { fid, follow }) => {
      if (follow) {
        state.followsByActor[fid] = follow
      } else {
        delete state.followsByActor[fid]
      }

      state.count = Object.keys(state.followsByActor).length
    },
    reset (state) {
      state.followsByActor = {}
      state.count = 0
    }
  },
  getters: {
    follow: (state) => (fid: string) => {
      return state.followsByActor[fid]
    }
  },
  actions: {
    set ({ commit, state }, { fid, value }) {
      if (value) {
        return axios.post('federation/follows/user/', { target: fid }).then((response) => {
          logger.info('Successfully subscribed to actor')
          commit('follows', { fid, follow: response.data })
        }, () => {
          logger.info('Error while subscribing to actor')
          commit('follows', { fid, follow: null })
        })
      } else {
        const follow = state.followsByActor[fid]
        return axios.delete(`federation/follows/user/${follow.uuid}/`).then(() => {
          logger.info('Successfully unsubscribed from actor')
          commit('follows', { fid, follow: null })
        }, () => {
          logger.info('Error while unsubscribing from actor')
          commit('follows', { fid, follow })
        })
      }
    },
    toggle ({ getters, dispatch }, fid) {
      dispatch('set', { fid, value: !getters.follow(fid) })
    },
    async fetchFollows ({ dispatch, state, commit, rootState }, url) {
      const response = await axios.get('federation/follows/user/all/')
      for (const result of response.data.results) {
        commit('follows', { fid: result.actor, follow: result })
      }
    }
  }
}

export default store
