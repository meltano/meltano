import lodash from 'lodash';

import pluginsApi from '../../api/plugins';

const state = {
  plugins: {},
  installedPlugins: {},
  installingPlugins: {
    extractors: [],
    loaders: [],
    models: [],
  },
};

const getters = {
  getIsPluginInstalled(stateRef) {
    return (pluginType, extractor) => (stateRef.installedPlugins[pluginType]
      ? Boolean(stateRef.installedPlugins[pluginType].find(item => item.name === extractor))
      : false);
  },
  getIsInstallingPlugin(stateRef) {
    return (pluginType, extractor) => stateRef.installingPlugins[pluginType].includes(extractor);
  },
};

const actions = {
  getAllPlugins({ commit }) {
    pluginsApi.getAllPlugins()
      .then((response) => {
        commit('setAllPlugins', response.data);
      });
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
    pluginsApi.getInstalledPlugins()
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
    lodash.pull(state.installingPlugins[installConfig.pluginType], installConfig.name);
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
