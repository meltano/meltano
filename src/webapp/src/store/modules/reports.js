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
  getReportsByIds(state) {
    return ids => state.reports.filter(report => ids.includes(report.id))
  }
}

const actions = {
  loadReports({ commit }) {
    return reportsApi
      .loadReports()
      .then(response => commit('setReports', response.data))
  },
  saveReport({ commit }, payload) {
    return reportsApi.saveReport(payload).then(response => {
      commit('addReport', response.data)
      commit('resetSaveReportSettings')
    })
  },
  updateReport({ commit }, payload) {
    return reportsApi.updateReport(payload).then(() => {
      console.log('**: setReport mutation?')
      commit('resetSaveReportSettings')
    })
  },
  updateSaveReportSettings({ commit }, name) {
    commit('setSaveReportSettingsName', name)
  }
}

const mutations = {
  addReport(state, report) {
    console.log('added report')

    state.reports.push(report)
  },
  resetSaveReportSettings(state) {
    state.saveReportSettings = { name: null }
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
