import Vue from 'vue'

import lodash from 'lodash'

import dashboardsApi from '../../api/dashboards'
import reportsApi from '../../api/reports'
import utils from '@/utils/utils'

const defaultState = utils.deepFreeze({
  activeDashboard: {},
  activeDashboardReports: [],
  dashboards: [],
  isInitializing: true,
  reports: []
})

const actions = {
  addReportToDashboard({ commit, dispatch }, data) {
    commit('addReportToDashboard', data)
    return dashboardsApi.addReportToDashboard(data).then(response => {
      dispatch('updateCurrentDashboard', response.data)
    })
  },

  deleteDashboard({ commit }, dashboard) {
    let status = {
      dashboard,
      isDeleting: true
    }
    commit('setDashboardStatus', status)

    return dashboardsApi
      .deleteDashboard(dashboard)
      .then(() => {
        commit('deleteDashboard', dashboard)
      })
      .finally(() => {
        commit(
          'setDashboardStatus',
          Object.assign(status, { isDeleting: false })
        )
      })
  },

  getActiveDashboardReportsWithQueryResults({ commit, state }) {
    const ids = state.activeDashboard.reportIds
    const activeReports = state.reports.filter(report =>
      ids.includes(report.id)
    )

    return dashboardsApi
      .getActiveDashboardReportsWithQueryResults(activeReports)
      .then(response => {
        commit('setActiveDashboardReports', response.data)
      })
  },

  getDashboards({ commit }) {
    return dashboardsApi.getDashboards().then(response => {
      commit('setDashboards', response.data)
    })
  },

  getReports({ commit }) {
    return reportsApi
      .loadReports()
      .then(response => commit('setReports', response.data))
  },

  initialize({ commit, dispatch }, slug) {
    commit('setIsInitialzing', true)
    const promiseGetReports = dispatch('getReports')
    const promiseGetDashboards = dispatch('getDashboards')
    return Promise.all([promiseGetReports, promiseGetDashboards]).then(() => {
      if (slug) {
        dispatch('preloadDashboard', slug)
      }
      commit('setIsInitialzing', false)
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

    return dashboardsApi.removeReportFromDashboard(data).then(response => {
      return dispatch('updateCurrentDashboard', response.data)
    })
  },

  resetActiveDashboard: ({ commit }) => commit('reset', 'activeDashboard'),

  resetActiveDashboardReports: ({ commit }) =>
    commit('reset', 'activeDashboardReports'),

  saveDashboard({ dispatch, commit }, data) {
    return dashboardsApi.saveDashboard(data).then(response => {
      commit('addSavedDashboardToDashboards', response.data)
      dispatch('updateCurrentDashboard', response.data)
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

  updateCurrentDashboard({ commit }, dashboard) {
    commit('setCurrentDashboard', dashboard)
  },

  updateDashboard({ commit }, payload) {
    return dashboardsApi.updateDashboard(payload).then(response => {
      commit('setDashboard', response.data)
    })
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

  deleteDashboard(state, dashboard) {
    const idx = state.dashboards.indexOf(dashboard)
    state.dashboards.splice(idx, 1)
  },

  removeReportFromDashboard(state, idsPayload) {
    const targetDashboard = state.dashboards.find(
      dashboard => dashboard.id === idsPayload.dashboardId
    )
    const idx = targetDashboard.reportIds.indexOf(idsPayload.reportId)
    targetDashboard.reportIds.splice(idx, 1)
  },

  reset(state, attr) {
    if (defaultState.hasOwnProperty(attr)) {
      state[attr] = lodash.cloneDeep(defaultState[attr])
    }
  },

  setActiveDashboardReports(state, reports) {
    state.activeDashboardReports = reports
  },

  setCurrentDashboard(state, dashboard) {
    state.activeDashboard = dashboard
  },

  setDashboard(state, dashboard) {
    const target = state.dashboards.find(item => item.id === dashboard.id)
    const idx = state.dashboards.indexOf(target)
    state.dashboards[idx] = dashboard
  },

  setDashboards(state, dashboards) {
    state.dashboards = dashboards
  },

  setDashboardStatus(_, { dashboard, isDeleting = false }) {
    Vue.set(dashboard, 'isDeleting', isDeleting)
  },

  setIsInitialzing(state, value) {
    state.isInitializing = value
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
