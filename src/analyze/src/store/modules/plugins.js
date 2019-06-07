import lodash from 'lodash';

import orchestrationsApi from '../../api/orchestrations';

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
    orchestrationsApi.index()
      .then((response) => {
        commit('setAllPlugins', response.data);
      });
  },

  installPlugin({ commit, dispatch }, installConfig) {
    commit('installPluginStart', installConfig);

    return orchestrationsApi.installPlugin(installConfig)
      .then(() => {
        dispatch('getInstalledPlugins')
          .then(() => {
            commit('installPluginComplete', installConfig);
            dispatch('getAllPlugins');
          });
      });
  },

  getInstalledPlugins({ commit }) {
    orchestrationsApi.installedPlugins()
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
