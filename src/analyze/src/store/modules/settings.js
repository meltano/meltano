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
};

const actions = {
  getSettings({ commit }) {
    settingsApi.index().then((data) => {
      commit('setSettings', data.data.settings);
    });
  },
  deleteConnection({ commit }, connection) {
    const connectionToRemove = state.settings.connections.find(item => item === connection);
    settingsApi.deleteConnection(connectionToRemove).then((data) => {
      commit('setSettings', data.data);
    });
  },
  saveNewConnection({ commit }, formData) {
    const settingsCopy = Object.assign({}, state.settings);
    settingsCopy.connections.push(formData);
    settingsApi.save(settingsCopy).then((data) => {
      commit('setSettings', data.data);
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
