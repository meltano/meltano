import dashboardsApi from '../../api/dashboards';
import reportsApi from '../../api/reports';

const state = {
  activeDashboard: {},
  activeDashboardReports: [],
  dashboards: [],
  reports: [],
};

const actions = {
  initialize({ dispatch }, slug) {
    const promiseGetReports = dispatch('getReports');
    const promiseGetDashboards = dispatch('getDashboards');
    Promise.all([promiseGetReports, promiseGetDashboards])
      .then(() => {
        dispatch('preloadDashboard', slug);
      })
      .catch(() => { });
  },
  preloadDashboard({ dispatch }, slug) {
    // Load from slug or refresh existing activeDashboard's reports with activeDashboardReports
    if (slug) {
      const dashboardMatch = state.dashboards.find(dashboard => dashboard.slug === slug);
      if (dashboardMatch) {
        dispatch('updateCurrentDashboard', dashboardMatch);
      }
    } else if (state.activeDashboard.reportIds) {
      dispatch('getActiveDashboardReportsWithQueryResults');
    }
  },
  getDashboards({ commit }) {
    return new Promise((resolve) => {
      dashboardsApi.getDashboards()
        .then((response) => {
          const dashboards = response.data;
          commit('setDashboards', dashboards);
          resolve();
        })
        .catch(() => { });
    });
  },
  setDashboard({ dispatch }, dashboard) {
    dispatch('updateCurrentDashboard', dashboard);
  },
  getReports({ commit }) {
    return new Promise((resolve) => {
      reportsApi.loadReports()
        .then((response) => {
          commit('setReports', response.data);
          resolve();
        })
        .catch(() => { });
    });
  },
  getActiveDashboardReportsWithQueryResults({ commit }) {
    const ids = state.activeDashboard.reportIds;
    const activeReports = state.reports.filter(report => ids.includes(report.id));
    dashboardsApi.getActiveDashboardReportsWithQueryResults(activeReports)
      .then((response) => {
        commit('setActiveDashboardReports', response.data);
      })
      .catch(() => { });
  },
  saveDashboard({ dispatch, commit }, data) {
    dashboardsApi.saveDashboard(data)
      .then((response) => {
        dispatch('updateCurrentDashboard', response.data);
        commit('addSavedDashboardToDashboards', response.data);
      })
      .catch(() => { });
  },
  saveNewDashboardWithReport({ commit, dispatch }, { data, report }) {
    dashboardsApi.saveDashboard(data)
      .then((response) => {
        const dashboard = response.data;
        commit('setCurrentDashboard', dashboard);
        commit('addSavedDashboardToDashboards', dashboard);
        dispatch('addReportToDashboard', {
          reportId: report.id,
          dashboardId: dashboard.id,
        });
      })
      .catch(() => { });
  },
  addReportToDashboard({ dispatch }, data) {
    dashboardsApi.addReportToDashboard(data)
      .then((response) => {
        dispatch('updateCurrentDashboard', response.data);
      })
      .catch(() => {});
  },
  removeReportFromDashboard({ dispatch }, data) {
    dashboardsApi.removeReportFromDashboard(data)
      .then((response) => {
        dispatch('updateCurrentDashboard', response.data);
      })
      .catch(() => {});
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
