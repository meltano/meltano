import settingsApi from '../../api/settings';

const state = {
  settings: {
    connections: [],
  },
};

const getters = {
  hasConnections() {
    return state.settings.connections && state.settings.connections.length;
  },
  isConnectionDialectSqlite() {
    return connectionDialect => connectionDialect === 'sqlite';
  },
};

const actions = {
  getSettings({ commit }) {
    settingsApi.index().then((response) => {
      commit('setSettings', response.data.settings);
    });
  },
  saveConnection({ commit }, connection) {
    settingsApi.saveConnection(connection).then((response) => {
      commit('setSettings', response.data.settings);
    });
  },
  deleteConnection({ commit }, connection) {
    const connectionToRemove = state.settings.connections
      .find(item => item === connection);
    settingsApi.deleteConnection(connectionToRemove)
      .then((response) => {
        commit('setSettings', response.data.settings);
      });
  },
};

const mutations = {
  setSettings(_, settings) {
    state.settings = settings;
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
