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

  getIsLoadingPluginsOfType(state) {
    return pluginType => {
      const plugins = state.plugins[pluginType]
      return plugins === undefined || plugins.length === 0
    }
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

  getPluginLabel(state) {
    return (type, name) => {
      const pluginList = state.plugins[type]
      const targetPlugin = pluginList
        ? pluginList.find(plugin => plugin.name === name)
        : {}

      return targetPlugin ? targetPlugin.label : 'Undefined label'
    }
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

  getInstalledPlugins({ commit }) {
    return pluginsApi.getInstalledPlugins().then(response => {
      commit('setInstalledPlugins', response.data)
    })
  },

  getPlugins({ commit }) {
    pluginsApi.getPlugins().then(response => {
      commit('setAllPlugins', response.data)
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
      .then(dispatch('getPlugins'))
  },

  installRelatedPlugins({ dispatch }, installConfig) {
    return pluginsApi.installBatch(installConfig).then(() => {
      dispatch('getPlugins')
      dispatch('dashboards/getDashboards', null, { root: true })
      dispatch('reports/loadReports', null, { root: true })
      dispatch('repos/getModels', null, { root: true })
    })
  }
}

const mutations = {
  addPluginComplete(state, addConfig) {
    const idx = state.addingPlugins[addConfig.pluginType].indexOf(
      addConfig.name
    )
    Vue.delete(state.addingPlugins[addConfig.pluginType], idx)
  },

  addPluginStart(state, addConfig) {
    state.addingPlugins[addConfig.pluginType].push(addConfig.name)
  },

  installPluginComplete(state, installConfig) {
    const idx = state.installingPlugins[installConfig.pluginType].indexOf(
      installConfig.name
    )
    Vue.delete(state.installingPlugins[installConfig.pluginType], idx)
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
