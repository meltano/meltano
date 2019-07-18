import lodash from 'lodash';

import pluginsApi from '../../api/plugins';

const defaultState = Object.freeze({
  plugins: {},
  installedPlugins: {},
  installingPlugins: {
    extractors: [],
    loaders: [],
    models: [],
    connections: [],
  },
});

const getters = {
  getHasInstalledPluginsOfType(state) {
    return (pluginType) => {
      const hasOwns = [];
      lodash.forOwn(state.installedPlugins[pluginType], val => hasOwns.push(val));
      return hasOwns.length > 0;
    };
  },
  getIsPluginInstalled(state) {
    return (pluginType, pluginName) => (state.installedPlugins[pluginType]
      ? Boolean(state.installedPlugins[pluginType].find(item => item.name === pluginName))
      : false);
  },
  getIsInstallingPlugin(state) {
    return (pluginType, pluginName) => state.installingPlugins[pluginType].includes(pluginName);
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
  installPluginStart(state, installConfig) {
    state.installingPlugins[installConfig.pluginType].push(installConfig.name);
  },

  installPluginComplete(state, installConfig) {
    const idx = state.installingPlugins[installConfig.pluginType].indexOf(installConfig.name);
    state.installingPlugins[installConfig.pluginType].splice(idx, 1);
  },

  setAllPlugins(state, plugins) {
    state.plugins = plugins;
  },

  setInstalledPlugins(state, projectConfig) {
    if (projectConfig.plugins) {
      state.installedPlugins = projectConfig.plugins;
    }
  },
};

export default {
  namespaced: true,
  state: lodash.cloneDeep(defaultState),
  getters,
  actions,
  mutations,
};
