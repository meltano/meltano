import axios from 'axios'
import utils from '@/utils/utils'

export default {
  deleteReport(report) {
    return axios.delete(utils.apiUrl('reports', 'delete'), { data: report })
  },

  getReports() {
    return axios.get(utils.apiUrl('reports'))
  },

  saveReport(data) {
    return axios.post(utils.apiUrl('reports', 'save'), data)
  },

  updateReport(data) {
    return axios.post(utils.apiUrl('reports', 'update'), data)
  }
}
