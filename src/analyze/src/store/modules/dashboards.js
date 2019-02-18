import dashboardApi from '../../api/dashboards';
import designApi from '../../api/design';

const state = {
  activeDashboard: {},
  activeDashboardReports: [],
  dashboards: [],
  reports: [],
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
  getReports({ commit }) {
    designApi.loadReports()
      .then((response) => {
        commit('setReports', response.data);
      });
  },
  getActiveDashboardReportsWithQueryResults({ commit }) {
    const ids = state.activeDashboard.reportIds;
    const activeReports = state.reports.filter(report => ids.includes(report.id));
    dashboardApi.getActiveDashboardReportsWithQueryResults(activeReports)
      .then((response) => {
        commit('setActiveDashboardReports', response.data);
      });
  },
  saveDashboard({ commit }, data) {
    dashboardApi.saveDashboard(data)
      .then((response) => {
        commit('setCurrentDashboard', response.data);
        commit('addSavedDashboardToDashboards', response.data);
      });
  },
  saveNewDashboardWithReport({ commit, dispatch }, { data, report }) {
    const promiseDashboard = dashboardApi.saveDashboard(data);
    const promiseReport = designApi.saveReport(report);
    Promise.all([promiseDashboard, promiseReport])
      .then((values) => {
        const dashboard = values[0].data;
        const reportWithId = values[1].data;
        commit('setCurrentDashboard', dashboard);
        commit('addSavedDashboardToDashboards', dashboard);
        dispatch('addReportToDashboard', {
          reportId: reportWithId.id,
          dashboardId: dashboard.id,
        });
      });
  },
  addReportToDashboard({ commit }, data) {
    dashboardApi.addReportToDashboard(data)
      .then((response) => {
        commit('setCurrentDashboard', response.data);
      });
  },
  removeReportFromDashboard({ commit }, data) {
    dashboardApi.removeReportFromDashboard(data)
      .then((response) => {
        commit('setCurrentDashboard', response.data);
      });
  },
};

const mutations = {
  addSavedDashboardToDashboards(_, dashboard) {
    state.dashboards.push(dashboard);
  },
  setActiveDashboardReports(_, reports) {
    state.activeDashboardReports = reports;
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
