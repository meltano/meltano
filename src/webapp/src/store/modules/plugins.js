import Vue from 'vue'

import lodash from 'lodash'

import pluginsApi from '../../api/plugins'
import utils from '@/utils/utils'
import pluginUtils from '@/utils/plugins'

const defaultState = utils.deepFreeze({
  addingPlugins: {
    connections: [],
    extractors: [],
    loaders: [],
    models: [],
    orchestrators: []
  },
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
  getHasDefaultTransforms(state) {
    return namespace =>
      state.plugins.transforms.find(
        transform => transform.namespace === namespace
      )
  },

  getHasInstalledPluginsOfType(state) {
    return pluginType => {
      const hasOwns = []
      lodash.forOwn(state.installedPlugins[pluginType], val =>
        hasOwns.push(val)
      )
      return hasOwns.length > 0
    }
  },

  getInstalledPlugin(state) {
    return (pluginType, pluginName) => {
      const targetPlugin = state.installedPlugins[pluginType]
        ? state.installedPlugins[pluginType].find(
            plugin => plugin.name === pluginName
          )
        : null
      return targetPlugin || {}
    }
  },

  getIsAddingPlugin(state) {
    return (pluginType, pluginName) =>
      state.addingPlugins[pluginType].includes(pluginName)
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
  },

  getIsStepExtractorsMinimallyValidated(state) {
    return (
      state.installedPlugins.extractors &&
      state.installedPlugins.extractors.length > 0
    )
  },

  getIsStepLoadersMinimallyValidated(_, getters) {
    return getters.getIsStepExtractorsMinimallyValidated
  },

  getIsStepScheduleMinimallyValidated(state, getters) {
    return (
      getters.getIsStepLoadersMinimallyValidated &&
      state.installedPlugins.loaders &&
      state.installedPlugins.loaders.length > 0
    )
  },

  getPluginProfiles() {
    return plugin => {
      const pluginProfiles = lodash.map(
        plugin['profiles'],
        profile => `${plugin.name}@${profile.name}`
      )
      return [plugin.name, ...pluginProfiles]
    }
  },

  visibleExtractors(state) {
    return pluginUtils.filterVisiblePlugins({
      installedPlugins: state.installedPlugins.extractors,
      pluginList: state.plugins.extractors
    })
  },

  visibleLoaders(state) {
    return pluginUtils.filterVisiblePlugins({
      installedPlugins: state.installedPlugins.loaders,
      pluginList: state.plugins.loaders
    })
  }
}

const actions = {
  addPlugin({ commit }, addConfig) {
    commit('addPluginStart', addConfig)
    return pluginsApi
      .addPlugin(addConfig)
      .finally(() => commit('addPluginComplete', addConfig))
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
      .then(() => commit('installPluginComplete', installConfig))
      .then(dispatch('getInstalledPlugins'))
      .then(dispatch('getAllPlugins'))
      .catch(error => {
        Vue.toasted.global.error(error.response.data.code)
      })
  },

  installRelatedPlugins({ dispatch }, installConfig) {
    return pluginsApi.installBatch(installConfig).then(() => {
      dispatch('getAllPlugins')
      dispatch('repos/getAllModels', null, { root: true })
    })
  }
}

const mutations = {
  addPluginComplete(state, addConfig) {
    const idx = state.addingPlugins[addConfig.pluginType].indexOf(
      addConfig.name
    )
    state.addingPlugins[addConfig.pluginType].splice(idx, 1)
  },

  addPluginStart(state, addConfig) {
    state.addingPlugins[addConfig.pluginType].push(addConfig.name)
  },

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
