import Vue from 'vue'

import lodash from 'lodash'

import dashboardsApi from '@/api/dashboards'
import utils from '@/utils/utils'

const defaultState = utils.deepFreeze({
  activeDashboard: {},
  activeDashboardReportsWithQueryResults: [],
  dashboards: [],
  isInitializing: true,
  isLoadingActiveDashboard: true
})

const getters = {
  activeReportIds: state => {
    return state.activeDashboard.reportIds
  },
  activeReports: (state, getters, rootState, rootGetters) => {
    return rootGetters['reports/getReportsByIds'](getters.activeReportIds)
  }
}

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

  getActiveDashboardReportsWithQueryResults({ commit, getters }) {
    commit('setIsLoadingActiveDashboard', true)
    return dashboardsApi
      .getActiveDashboardReportsWithQueryResults(getters.activeReports)
      .then(response => {
        commit('setActiveDashboardReportsWithQueryResults', response.data)
        commit('setIsLoadingActiveDashboard', false)
      })
  },

  getDashboards({ commit }) {
    return dashboardsApi.getDashboards().then(response => {
      commit('setDashboards', response.data)
    })
  },

  initialize({ commit, dispatch }, slug) {
    commit('setIsInitializing', true)
    const uponLoadReports = dispatch('reports/loadReports', null, {
      root: true
    })
    const uponGetDashboards = dispatch('getDashboards')
    return Promise.all([uponLoadReports, uponGetDashboards]).then(() => {
      if (slug) {
        dispatch('preloadDashboard', slug)
      }
      commit('setIsInitializing', false)
    })
  },

  preloadDashboard({ dispatch, state, getters }, slug) {
    // Load from slug or refresh existing activeDashboard's reports with activeDashboardReportsWithQueryResults
    if (slug) {
      const dashboardMatch = state.dashboards.find(
        dashboard => dashboard.slug === slug
      )
      if (dashboardMatch) {
        dispatch('updateCurrentDashboard', dashboardMatch)
      }
    } else if (getters.activeReportIds) {
      dispatch('getActiveDashboardReportsWithQueryResults')
    }
  },

  removeReportFromDashboard({ commit, dispatch }, data) {
    commit('removeReportFromDashboard', data)

    return dashboardsApi.removeReportFromDashboard(data).then(response => {
      return dispatch('updateCurrentDashboard', response.data)
    })
  },

  reorderDashboardReports({ dispatch }, payload) {
    dashboardsApi.reorderDashboardReports(payload).then(response => {
      dispatch('updateCurrentDashboard', response.data)
    })
  },

  resetActiveDashboard: ({ commit }) => commit('reset', 'activeDashboard'),

  resetActiveDashboardReports: ({ commit }) =>
    commit('reset', 'activeDashboardReportsWithQueryResults'),

  saveDashboard({ dispatch, commit }, payload) {
    return dashboardsApi.saveDashboard(payload).then(response => {
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

  updateActiveDashboardReportsWithQueryResults({ commit }, reports) {
    commit('setActiveDashboardReportsWithQueryResults', reports)
  },

  updateCurrentDashboard({ commit, dispatch }, dashboard) {
    commit('setCurrentDashboard', dashboard)
    dispatch('getActiveDashboardReportsWithQueryResults')
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
    Vue.delete(state.dashboards, idx)
  },

  removeReportFromDashboard(state, idsPayload) {
    const targetDashboard = state.dashboards.find(
      dashboard => dashboard.id === idsPayload.dashboardId
    )
    const idx = targetDashboard.reportIds.indexOf(idsPayload.reportId)
    Vue.delete(targetDashboard.reportIds, idx)
  },

  reset(state, attr) {
    if (defaultState.hasOwnProperty(attr)) {
      state[attr] = lodash.cloneDeep(defaultState[attr])
    }
  },

  setActiveDashboardReportsWithQueryResults(state, reports) {
    state.activeDashboardReportsWithQueryResults = reports
  },

  setCurrentDashboard(state, dashboard) {
    state.activeDashboard = dashboard
  },

  setDashboard(state, dashboard) {
    const target = state.dashboards.find(item => item.id === dashboard.id)
    const idx = state.dashboards.indexOf(target)
    Vue.set(state.dashboards, idx, dashboard)
  },

  setDashboards(state, dashboards) {
    state.dashboards = dashboards
  },

  setDashboardStatus(_, { dashboard, isDeleting = false }) {
    Vue.set(dashboard, 'isDeleting', isDeleting)
  },

  setIsInitializing(state, value) {
    state.isInitializing = value
  },

  setIsLoadingActiveDashboard(state, value) {
    state.isLoadingActiveDashboard = value
  }
}

export default {
  namespaced: true,
  state: lodash.cloneDeep(defaultState),
  getters,
  actions,
  mutations
}
