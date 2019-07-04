import lodash from 'lodash';

import pluginsApi from '../../api/plugins';

const state = {
  plugins: {},
  installedPlugins: {},
  installingPlugins: {
    extractors: [],
    loaders: [],
    models: [],
    connections: [],
  },
};

const getters = {
  getHasInstalledPluginsOfType() {
    return (pluginType) => {
      const hasOwns = [];
      lodash.forOwn(state.installedPlugins[pluginType], val => hasOwns.push(val));
      return hasOwns.length > 0;
    };
  },
  getIsPluginInstalled(stateRef) {
    return (pluginType, pluginName) => (stateRef.installedPlugins[pluginType]
      ? Boolean(stateRef.installedPlugins[pluginType].find(item => item.name === pluginName))
      : false);
  },
  getIsInstallingPlugin(stateRef) {
    return (pluginType, pluginName) => stateRef.installingPlugins[pluginType].includes(pluginName);
  },
};

const actions = {
  getAllPlugins({ commit }) {
    pluginsApi.getAllPlugins()
      .then((response) => {
        commit('setAllPlugins', response.data);
      });
  },

  addPlugin(_, addConfig) {
    return pluginsApi.addPlugin(addConfig);
  },

  installPlugin({ commit, dispatch }, installConfig) {
    commit('installPluginStart', installConfig);

    return pluginsApi.installPlugin(installConfig)
      .then(() => {
        dispatch('getInstalledPlugins')
          .then(() => {
            commit('installPluginComplete', installConfig);
            dispatch('getAllPlugins');
          });
      });
  },

  getInstalledPlugins({ commit }) {
    return pluginsApi.getInstalledPlugins()
      .then((response) => {
        commit('setInstalledPlugins', response.data);
      });
  },
};

const mutations = {
  installPluginStart(_, installConfig) {
    state.installingPlugins[installConfig.pluginType].push(installConfig.name);
  },

  installPluginComplete(_, installConfig) {
    const idx = state.installingPlugins[installConfig.pluginType].indexOf(installConfig.name);
    state.installingPlugins[installConfig.pluginType].splice(idx, 1);
  },

  setAllPlugins(_, plugins) {
    state.plugins = plugins;
  },

  setInstalledPlugins(_, projectConfig) {
    if (projectConfig.plugins) {
      state.installedPlugins = projectConfig.plugins;
    }
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
