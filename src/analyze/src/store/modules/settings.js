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
    settingsApi.index().then((data) => {
      commit('setSettings', data.data.settings);
    });
  },
  saveConnection({ commit }, connection) {
    settingsApi.saveConnection(connection).then((data) => {
      commit('setSettings', data.data.settings);
    });
  },
  deleteConnection({ commit }, connection) {
    const connectionToRemove = state.settings.connections
      .find(item => item === connection);
    settingsApi.deleteConnection(connectionToRemove)
      .then((data) => {
        commit('setSettings', data.data.settings);
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
