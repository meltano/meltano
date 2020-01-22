import axios from 'axios'
import utils from '@/utils/utils'

export default {
  loadReport(name) {
    return axios.post(utils.apiUrl('reports', `${name}`), {
      hasResults: false
    })
  },

  loadReportWithQueryResults(name) {
    return axios.post(utils.apiUrl('reports', `${name}`), {
      hasResults: true
    })
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
