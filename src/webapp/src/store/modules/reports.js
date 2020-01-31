import lodash from 'lodash'

import reportsApi from '@/api/reports'
import utils from '@/utils/utils'

const defaultState = utils.deepFreeze({
  reports: []
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
    })
  },
  updateReport(_, payload) {
    return reportsApi.updateReport(payload).then(response => {
      console.log('**: setReport mutation?')
    })
  }
}

const mutations = {
  addReport(state, report) {
    console.log('added report')

    state.reports.push(report)
  },
  setReports(state, reports) {
    state.reports = reports
  }
}

export default {
  namespaced: true,
  state: lodash.cloneDeep(defaultState),
  getters,
  actions,
  mutations
}
