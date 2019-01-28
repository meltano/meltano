import dashboardApi from '../../api/dashboards';

const state = {
  dashboards: [],
  activeDashboard: {},
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
        commit('setCurrentDashboard', response.data);
      });
  },
};

const mutations = {
  setDashboards(_, dashboards) {
    state.dashboards = dashboards;
  },
  setCurrentDashboard(_, dashboard) {
    state.activeDashboard = dashboard;
  },
};

export default {
  namespaced: true,
  state,
  actions,
  mutations,
};
