import dashboardApi from '../../api/dashboards';

const state = {
  activeDashboard: {},
  dashboards: [],
  isAddDashboard: true,
  saveDashboardSettings: { name: null, description: null },
};

const actions = {
  getDashboards({ commit }) {
    dashboardApi.getDashboards()
      .then((response) => {
        const dashboards = response.data;
        commit('setDashboards', dashboards);
      });
  },
  getDashboard({ commit }, dashboard) {
    dashboardApi.getDashboard(dashboard.id)
      .then((response) => {
        commit('setAddDashboard', false);
        commit('setCurrentDashboard', response.data);
      });
  },
  setAddDashboard({ commit }, value) {
    commit('setAddDashboard', value);
  },
  saveDashboard({ commit }, data) {
    dashboardApi.saveDashboard(data)
      .then((response) => {
        commit('setAddDashboard', false);
        commit('setCurrentDashboard', response.data);
        commit('resetSaveDashboardSettings');
      })
      .catch((e) => {
        commit('setSqlErrorMessage', e);
        state.loadingQuery = false;
      });
  },
};

const mutations = {
  resetSaveDashboardSettings() {
    state.saveDashboardSettings = { name: null, description: null };
  },
  setDashboards(_, dashboards) {
    state.dashboards = dashboards;
  },
  setCurrentDashboard(_, dashboard) {
    state.activeDashboard = dashboard;
  },
  setAddDashboard(_, value) {
    state.isAddDashboard = value;
  },
};

export default {
  namespaced: true,
  state,
  actions,
  mutations,
};
