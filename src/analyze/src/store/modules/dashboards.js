import dashboardApi from '../../api/dashboards';
import designApi from '../../api/design';
import reportApi from '../../api/reports';

const state = {
  activeDashboard: {},
  activeDashboardReports: [],
  dashboards: [],
  reports: [],
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
  setDashboard({ dispatch }, dashboard) {
    dispatch('updateCurrentDashboard', dashboard);
  },
  getReports({ commit }) {
    return new Promise((resolve) => {
      reportApi.loadReports()
        .then((response) => {
          commit('setReports', response.data);
          resolve();
        });
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
  saveDashboard({ dispatch, commit }, data) {
    dashboardApi.saveDashboard(data)
      .then((response) => {
        dispatch('updateCurrentDashboard', response.data);
        commit('addSavedDashboardToDashboards', response.data);
      });
  },
  saveNewDashboardWithReport({ commit, dispatch }, { data, report }) {
    dashboardApi.saveDashboard(data)
      .then((response) => {
        const dashboard = response.data;
        commit('setCurrentDashboard', dashboard);
        commit('addSavedDashboardToDashboards', dashboard);
        dispatch('addReportToDashboard', {
          reportId: report.id,
          dashboardId: dashboard.id,
        });
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
  updateCurrentDashboard({ commit }, dashboard) {
    commit('setCurrentDashboard', dashboard);
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
