import axios from 'axios'
import utils from '@/utils/utils'

export default {
  loadReports() {
    return axios.get(utils.apiUrl('reports'))
  },

  loadReport(name) {
    return axios.get(utils.apiUrl('reports/load', `${name}`))
  },

  saveReport(data) {
    return axios.post(utils.apiUrl('reports', 'save'), data)
  },

  updateReport(data) {
    return axios.post(utils.apiUrl('reports', 'update'), data)
  }
}
