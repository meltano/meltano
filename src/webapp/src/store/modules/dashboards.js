import lodash from 'lodash'

import dashboardsApi from '../../api/dashboards'
import reportsApi from '../../api/reports'
import utils from '@/utils/utils'

const defaultState = utils.deepFreeze({
  activeDashboard: {},
  activeDashboardReports: [],
  dashboards: [],
  reports: []
})

const actions = {
  addReportToDashboard({ commit, dispatch }, data) {
    commit('addReportToDashboard', data)
    dashboardsApi.addReportToDashboard(data).then(response => {
      dispatch('updateCurrentDashboard', response.data)
    })
  },

  getActiveDashboardReportsWithQueryResults({ commit, state }) {
    const ids = state.activeDashboard.reportIds
    const activeReports = state.reports.filter(report =>
      ids.includes(report.id)
    )
    dashboardsApi
      .getActiveDashboardReportsWithQueryResults(activeReports)
      .then(response => {
        commit('setActiveDashboardReports', response.data)
      })
  },

  getDashboards({ commit }) {
    return new Promise(resolve => {
      dashboardsApi.getDashboards().then(response => {
        const dashboards = response.data
        commit('setDashboards', dashboards)
        resolve()
      })
    })
  },

  getReports({ commit }) {
    return new Promise(resolve => {
      reportsApi.loadReports().then(response => {
        commit('setReports', response.data)
        resolve()
      })
    })
  },

  initialize({ dispatch }, slug) {
    const promiseGetReports = dispatch('getReports')
    const promiseGetDashboards = dispatch('getDashboards')
    Promise.all([promiseGetReports, promiseGetDashboards]).then(() => {
      dispatch('preloadDashboard', slug)
    })
  },

  preloadDashboard({ dispatch, state }, slug) {
    // Load from slug or refresh existing activeDashboard's reports with activeDashboardReports
    if (slug) {
      const dashboardMatch = state.dashboards.find(
        dashboard => dashboard.slug === slug
      )
      if (dashboardMatch) {
        dispatch('updateCurrentDashboard', dashboardMatch)
      }
    } else if (state.activeDashboard.reportIds) {
      dispatch('getActiveDashboardReportsWithQueryResults')
    }
  },

  removeReportFromDashboard({ commit, dispatch }, data) {
    commit('removeReportFromDashboard', data)
    dashboardsApi.removeReportFromDashboard(data).then(response => {
      dispatch('updateCurrentDashboard', response.data)
    })
  },

  saveDashboard({ dispatch, commit }, data) {
    return dashboardsApi.saveDashboard(data).then(response => {
      commit('addSavedDashboardToDashboards', response.data)
      return dispatch('updateCurrentDashboard', response.data)
    })
  },

  saveNewDashboardWithReport({ commit, dispatch }, { data, report }) {
    return dashboardsApi.saveDashboard(data).then(response => {
      const dashboard = response.data
      commit('setCurrentDashboard', dashboard)
      commit('addSavedDashboardToDashboards', dashboard)
      dispatch('addReportToDashboard', {
        reportId: report.id,
        dashboardId: dashboard.id
      })
    })
  },

  setDashboard({ dispatch }, dashboard) {
    dispatch('updateCurrentDashboard', dashboard)
  },

  updateCurrentDashboard({ commit }, dashboard) {
    commit('setCurrentDashboard', dashboard)
  }
}

const mutations = {
  addReportToDashboard(state, idsPayload) {
    const targetDashboard = state.dashboards.find(
      dashboard => dashboard.id === idsPayload.dashboardId
    )
    targetDashboard.reportIds.push(idsPayload.reportId)
  },

  addSavedDashboardToDashboards(state, dashboard) {
    state.dashboards.push(dashboard)
  },

  removeReportFromDashboard(state, idsPayload) {
    const targetDashboard = state.dashboards.find(
      dashboard => dashboard.id === idsPayload.dashboardId
    )
    const idx = targetDashboard.reportIds.indexOf(idsPayload.reportId)
    targetDashboard.reportIds.splice(idx, 1)
  },

  setActiveDashboardReports(state, reports) {
    state.activeDashboardReports = reports
  },

  setCurrentDashboard(state, dashboard) {
    state.activeDashboard = dashboard
  },

  setDashboards(state, dashboards) {
    state.dashboards = dashboards
  },

  setReports(state, reports) {
    state.reports = reports
  }
}

export default {
  namespaced: true,
  state: lodash.cloneDeep(defaultState),
  actions,
  mutations
}
