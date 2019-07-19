import lodash from 'lodash';

import utils from '@/utils/utils';
import dashboardsApi from '../../api/dashboards';
import reportsApi from '../../api/reports';

const defaultState = utils.deepFreeze({
  activeDashboard: {},
  activeDashboardReports: [],
  dashboards: [],
  reports: [],
});

const actions = {
  initialize({ dispatch }, slug) {
    const promiseGetReports = dispatch('getReports');
    const promiseGetDashboards = dispatch('getDashboards');
    Promise.all([promiseGetReports, promiseGetDashboards])
      .then(() => {
        dispatch('preloadDashboard', slug);
      });
  },
  preloadDashboard({ dispatch, state }, slug) {
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
        });
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
        });
    });
  },
  getActiveDashboardReportsWithQueryResults({ commit, state }) {
    const ids = state.activeDashboard.reportIds;
    const activeReports = state.reports.filter(report => ids.includes(report.id));
    dashboardsApi.getActiveDashboardReportsWithQueryResults(activeReports)
      .then((response) => {
        commit('setActiveDashboardReports', response.data);
      });
  },
  saveDashboard({ dispatch, commit }, data) {
    dashboardsApi.saveDashboard(data)
      .then((response) => {
        dispatch('updateCurrentDashboard', response.data);
        commit('addSavedDashboardToDashboards', response.data);
      });
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
      });
  },
  addReportToDashboard({ dispatch }, data) {
    dashboardsApi.addReportToDashboard(data)
      .then((response) => {
        dispatch('updateCurrentDashboard', response.data);
      });
  },
  removeReportFromDashboard({ dispatch }, data) {
    dashboardsApi.removeReportFromDashboard(data)
      .then((response) => {
        dispatch('updateCurrentDashboard', response.data);
      });
  },
  updateCurrentDashboard({ commit }, dashboard) {
    commit('setCurrentDashboard', dashboard);
  },
};

const mutations = {
  addSavedDashboardToDashboards(state, dashboard) {
    state.dashboards.push(dashboard);
  },
  setActiveDashboardReports(state, reports) {
    state.activeDashboardReports = reports;
  },
  setCurrentDashboard(state, dashboard) {
    state.activeDashboard = dashboard;
  },
  setDashboards(state, dashboards) {
    state.dashboards = dashboards;
  },
  setReports(state, reports) {
    state.reports = reports;
  },
};

export default {
  namespaced: true,
  state: lodash.cloneDeep(defaultState),
  actions,
  mutations,
};
