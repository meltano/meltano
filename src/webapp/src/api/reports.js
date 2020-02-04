import axios from 'axios'
import utils from '@/utils/utils'

export default {
  loadFromEmbedToken(token) {
    return axios.get(utils.apiUrl('reports/embed', token))
  },

  generateEmbedURL(id) {
    return axios.post(utils.apiUrl('reports', 'embed'), { id })
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
