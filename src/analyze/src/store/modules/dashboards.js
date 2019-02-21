import dashboardApi from '../../api/dashboards';
import designApi from '../../api/design';

const state = {
  activeDashboard: {},
  activeDashboardReports: [],
  dashboards: [],
  isAddDashboard: true,
  reports: [],
  saveDashboardSettings: { name: null, description: null },
};

const getters = {
  hasDashboards() {
    return state.dashboards.length > 0;
  },
  getIsActiveDashboardMatch: () => dashboard => dashboard.id === state.activeDashboard.id,
};

const actions = {
  initialize({ dispatch }, slug) {
    dispatch('getReports').then(() => {
      dispatch('getDashboards', slug);
    });
  },
  getDashboards({ dispatch, commit }, slug) {
    return new Promise((resolve) => {
      dashboardApi.getDashboards()
        .then((response) => {
          const dashboards = response.data;
          commit('setDashboards', dashboards);
          resolve();

          if (slug) {
            const dashboardMatch = dashboards.find(dashboard => dashboard.slug === slug);
            if (dashboardMatch) {
              dispatch('updateCurrentDashboard', dashboardMatch);
            }
          }
        });
    });
  },
  getDashboard({ dispatch }, dashboard) {
    dashboardApi.getDashboard(dashboard.id)
      .then((response) => {
        dispatch('updateCurrentDashboard', response.data);
      });
  },
  getReports({ commit }) {
    return new Promise((resolve) => {
      designApi.loadReports()
        .then((response) => {
          commit('setReports', response.data);
          resolve();
        });
    });
  },
  setAddDashboard({ commit }, value) {
    commit('setAddDashboard', value);
  },
  saveDashboard({ dispatch, commit }, data) {
    dashboardApi.saveDashboard(data)
      .then((response) => {
        dispatch('updateCurrentDashboard', response.data);
        commit('addSavedDashboardToDashboards', response.data);
        commit('resetSaveDashboardSettings');
      });
  },
  addReportToDashboard({ dispatch }, data) {
    dashboardApi.addReportToDashboard(data)
      .then((response) => {
        dispatch('updateCurrentDashboard', response.data);
      });
  },
  removeReportFromDashboard({ dispatch }, data) {
    dashboardApi.removeReportFromDashboard(data)
      .then((response) => {
        dispatch('updateCurrentDashboard', response.data);
      });
  },
  updateCurrentDashboard({ dispatch, commit }, dashboard) {
    commit('setAddDashboard', false);
    commit('setCurrentDashboard', dashboard);
    dispatch('updateActiveDashboardReportsWithQueryResults');
  },
  updateActiveDashboardReportsWithQueryResults({ commit }) {
    const ids = state.activeDashboard.reportIds;
    const activeReports = state.reports.filter(report => ids.includes(report.id));
    dashboardApi.getActiveDashboardReportsWithQueryResults(activeReports)
      .then((response) => {
        commit('setActiveDashboardReports', response.data);
      });
  },
};

const mutations = {
  addSavedDashboardToDashboards(_, dashboard) {
    state.dashboards.push(dashboard);
  },
  resetSaveDashboardSettings() {
    state.saveDashboardSettings = { name: null, description: null };
  },
  setActiveDashboardReports(_, reports) {
    state.activeDashboardReports = reports;
  },
  setAddDashboard(_, value) {
    state.isAddDashboard = value;
  },
  setCurrentDashboard(_, dashboard) {
    state.activeDashboard = dashboard;
  },
  setDashboards(_, dashboards) {
    state.dashboards = dashboards;
  },
  setReports(_, reports) {
    state.reports = reports;
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
