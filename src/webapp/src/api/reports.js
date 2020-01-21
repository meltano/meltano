import axios from 'axios'
import utils from '@/utils/utils'

export default {
  loadReport(name) {
    return axios.get(utils.apiUrl('reports/load', `${name}`))
  },

  loadReportWithQueryResults(name) {
    return axios.get(utils.apiUrl('reports/load-with-query-results', `${name}`))
  },

  loadReports() {
    return axios.get(utils.apiUrl('reports'))
  },

  saveReport(data) {
    return axios.post(utils.apiUrl('reports', 'save'), data)
  },

  updateReport(data) {
    return axios.post(utils.apiUrl('reports', 'update'), data)
  }
}
