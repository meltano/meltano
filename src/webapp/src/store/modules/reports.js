import Vue from 'vue'

import lodash from 'lodash'

import reportsApi from '@/api/reports'
import utils from '@/utils/utils'

const defaultState = utils.deepFreeze({
  reports: [],
  saveReportSettings: { name: null }
})

const getters = {
  getReportBySlug(state) {
    return ({ design, model, namespace, slug }) =>
      state.reports.find(
        report =>
          report.design === design &&
          report.model === model &&
          report.namespace === namespace &&
          report.slug === slug
      )
  },
  getReportById(state) {
    return id => state.reports.find(report => report.id === id)
  },
  getReportsByIds(state) {
    return ids => ids.map(id => state.reports.find(report => report.id === id))
  }
}

const actions = {
  getReports({ commit }) {
    return reportsApi
      .getReports()
      .then(response => commit('setReports', response.data))
  },
  saveReport({ commit }, payload) {
    return reportsApi.saveReport(payload).then(response => {
      commit('addReport', response.data)
      commit('resetSaveReportSettings')
      return response
    })
  },
  updateReport({ commit }, payload) {
    return reportsApi.updateReport(payload).then(response => {
      commit('setReport', response.data)
      commit('resetSaveReportSettings')
      return response
    })
  },
  updateSaveReportSettings({ commit }, name) {
    commit('setSaveReportSettingsName', name)
  }
}

const mutations = {
  addReport(state, report) {
    state.reports.push(report)
  },
  resetSaveReportSettings(state) {
    state.saveReportSettings = { name: null }
  },
  setReport(state, report) {
    const target = state.reports.find(item => item.id === report.id)
    const idx = state.reports.indexOf(target)
    Vue.set(state.reports, idx, report)
  },
  setReports(state, reports) {
    state.reports = reports
  },
  setSaveReportSettingsName(state, name) {
    state.saveReportSettings.name = name
  }
}

export default {
  namespaced: true,
  state: lodash.cloneDeep(defaultState),
  getters,
  actions,
  mutations
}
