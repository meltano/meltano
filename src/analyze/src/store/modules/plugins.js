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
    return (collectionType, extractor) => (stateRef.installedPlugins[collectionType]
      ? Boolean(stateRef.installedPlugins[collectionType].find(item => item.name === extractor))
      : false);
  },
  getIsInstallingPlugin(stateRef) {
    return (collectionType, extractor) => stateRef.installingPlugins[collectionType].includes(extractor);
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
    state.installingPlugins[installConfig.collectionType].push(installConfig.name);
  },

  installPluginComplete(_, installConfig) {
    lodash.pull(state.installingPlugins[installConfig.collectionType], installConfig.name);
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
