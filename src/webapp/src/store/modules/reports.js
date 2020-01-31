import lodash from 'lodash'

import reportsApi from '@/api/reports'
import utils from '@/utils/utils'

const defaultState = utils.deepFreeze({
  reports: []
})

const getters = {
  getReportsByIds(state) {
    return ids => {
      return state.reports.filter(report => ids.includes(report.id))
    }
  }
}

const actions = {
  loadReports({ commit }) {
    return reportsApi
      .loadReports()
      .then(response => commit('setReports', response.data))
  },
  saveReport(_, payload) {
    return reportsApi.saveReport(payload)
  },
  updateReport(_, payload) {
    return reportsApi.updateReport(payload)
  }
}

const mutations = {
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
