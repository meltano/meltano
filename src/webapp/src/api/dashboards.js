import axios from 'axios'
import utils from '@/utils/utils'

export default {
  getDashboards() {
    return axios.get(utils.apiUrl('dashboards', 'all'))
  },

  getDashboard(id) {
    return axios.get(utils.apiUrl('dashboards/dashboard', `${id}`))
  },

  getActiveDashboardReportsWithQueryResults(activeReports) {
    return axios.post(
      utils.apiUrl('dashboards/dashboard', 'reports'),
      activeReports
    )
  },

  saveDashboard(data) {
    return axios.post(utils.apiUrl('dashboards/dashboard', 'save'), data)
  },

  addReportToDashboard(data) {
    return axios.post(utils.apiUrl('dashboards/dashboard/report', 'add'), data)
  },

  removeReportFromDashboard(data) {
    return axios.post(
      utils.apiUrl('dashboards/dashboard/report', 'remove'),
      data
    )
  }
}
