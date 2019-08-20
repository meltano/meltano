import Vue from 'vue'

import lodash from 'lodash'

import pluginsApi from '../../api/plugins'
import utils from '@/utils/utils'

const defaultState = utils.deepFreeze({
  installedPlugins: {},
  installingPlugins: {
    connections: [],
    extractors: [],
    loaders: [],
    models: [],
    orchestrators: []
  },
  plugins: {}
})

const getters = {
  getHasInstalledPluginsOfType(state) {
    return pluginType => {
      const hasOwns = []
      lodash.forOwn(state.installedPlugins[pluginType], val =>
        hasOwns.push(val)
      )
      return hasOwns.length > 0
    }
  },

  getIsInstallingPlugin(state) {
    return (pluginType, pluginName) =>
      state.installingPlugins[pluginType].includes(pluginName)
  },

  getIsPluginInstalled(state) {
    return (pluginType, pluginName) =>
      state.installedPlugins[pluginType]
        ? Boolean(
            state.installedPlugins[pluginType].find(
              item => item.name === pluginName
            )
          )
        : false
  }
}

const actions = {
  addPlugin(_, addConfig) {
    return pluginsApi.addPlugin(addConfig)
  },

  getAllPlugins({ commit }) {
    pluginsApi.getAllPlugins().then(response => {
      commit('setAllPlugins', response.data)
    })
  },

  getInstalledPlugins({ commit }) {
    return pluginsApi.getInstalledPlugins().then(response => {
      commit('setInstalledPlugins', response.data)
    })
  },

  installPlugin({ commit, dispatch }, installConfig) {
    commit('installPluginStart', installConfig)

    if (installConfig.pluginType == 'extractors') {
      dispatch('installRelatedPlugins', installConfig)
    }

    return pluginsApi
      .installPlugin(installConfig)
      .then(() => {
        dispatch('getInstalledPlugins').then(() => {
          commit('installPluginComplete', installConfig)
          dispatch('getAllPlugins')
        })
      })
      .catch(error => {
        Vue.toasted.global.error(error.response.data.code)
      })
  },

  installRelatedPlugins({ dispatch }, installConfig) {
    return pluginsApi.installBatch(installConfig).then(() => {
      dispatch('getAllPlugins')
    })
  }
}

const mutations = {
  installPluginComplete(state, installConfig) {
    const idx = state.installingPlugins[installConfig.pluginType].indexOf(
      installConfig.name
    )
    state.installingPlugins[installConfig.pluginType].splice(idx, 1)
  },

  installPluginStart(state, installConfig) {
    state.installingPlugins[installConfig.pluginType].push(installConfig.name)
  },

  setAllPlugins(state, plugins) {
    state.plugins = plugins
  },

  setInstalledPlugins(state, projectConfig) {
    if (projectConfig.plugins) {
      state.installedPlugins = projectConfig.plugins
    }
  }
}

export default {
  namespaced: true,
  state: lodash.cloneDeep(defaultState),
  getters,
  actions,
  mutations
}
