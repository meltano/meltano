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
  getReports({ commit }) {
    designApi.loadReports()
      .then((response) => {
        commit('setReports', response.data);
      });
  },
  getActiveDashboardReportsWithSql({ commit }) {
    const ids = state.activeDashboard.reportIds;
    const activeReports = state.reports.filter(report => ids.includes(report.id));
    // TODO implement round trip
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
      });
  },
  addReportToDashboard({ commit }, data) {
    dashboardApi.addReportToDashboard(data)
      .then((response) => {
        commit('setAddDashboard', false);
        commit('setCurrentDashboard', response.data);
      });
  },
  removeReportFromDashboard({ commit }, data) {
    dashboardApi.removeReportFromDashboard(data)
      .then((response) => {
        commit('setAddDashboard', false);
        commit('setCurrentDashboard', response.data);
      });
  },
};

const mutations = {
  resetSaveDashboardSettings() {
    state.saveDashboardSettings = { name: null, description: null };
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
  actions,
  mutations,
};
