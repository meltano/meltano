import lodash from 'lodash'

import repoApi from '@/api/repo'
import utils from '@/utils/utils'

const defaultState = utils.deepFreeze({
  activeView: {
    file: '',
    is_markdown: false,
    populated: false,
  },
  errors: [],
  files: {},
  loadingUpdate: false,
  loadingValidation: false,
  models: {},
  validated: false,
})

const getters = {
  hasCode(state) {
    return state.activeView.populated && !state.activeView.is_markdown
  },

  hasError(state) {
    return state.errors && state.errors.length
  },

  hasFiles(state) {
    return state.files.hasOwnProperty('topics') && state.files.topics.items
  },

  hasMarkdown(state) {
    return state.activeView.populated && state.activeView.is_markdown
  },

  hasModels(state) {
    return !lodash.isEmpty(state.models)
  },

  passedValidation(state) {
    return state.validated && state.errors && !state.errors.length
  },

  urlForModelDesign: () => (model, design) => `/analyze/${model}/${design}`,
}

const actions = {
  getModels({ commit }) {
    repoApi.models().then((response) => {
      commit('setModels', response.data)
    })
  },

  getRepo({ state, commit }) {
    repoApi.index().then((response) => {
      const files = response.data
      commit('setValidatedState', response.data)
      state.loadingValidation = false
      commit('setRepoFiles', { files })
    })
  },

  lint({ state, commit }) {
    state.loadingValidation = true
    repoApi
      .lint()
      .then((response) => {
        commit('setValidatedState', response.data)
        state.loadingValidation = false
      })
      .catch(() => {
        state.loadingValidation = false
      })
  },

  sync({ state, commit, dispatch }) {
    state.loadingUpdate = true
    repoApi
      .sync()
      .then((response) => {
        dispatch('getModels')
        commit('setValidatedState', response.data)
        state.loadingUpdate = false
      })
      .catch(() => {
        state.loadingUpdate = false
      })
  },
}

const mutations = {
  setCurrentFileTable(state, file) {
    state.activeView = file
  },

  setModels(state, models) {
    state.models = models
  },

  setRepoFiles(state, { files }) {
    state.files = files
  },

  setValidatedState(state, validated) {
    state.errors = []
    state.validated = true
    // validation failed, so there will be errors
    if (!validated.result) {
      state.errors = validated.errors
    }
  },
}

export default {
  namespaced: true,
  state: lodash.cloneDeep(defaultState),
  getters,
  actions,
  mutations,
}
