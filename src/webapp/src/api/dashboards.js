import axios from 'axios'
import utils from '@/utils/utils'

export default {
  addReportToDashboard(data) {
    return axios.post(utils.apiUrl('dashboards/dashboard/report', 'add'), data)
  },

  getActiveDashboardReportsWithQueryResults(activeReports) {
    return axios.post(
      utils.apiUrl('dashboards/dashboard', 'reports'),
      activeReports
    )
  },

  getDashboard(id) {
    return axios.get(utils.apiUrl('dashboards/dashboard', `${id}`))
  },

  getDashboards() {
    return axios.get(utils.apiUrl('dashboards', 'all'))
  },

  removeReportFromDashboard(data) {
    return axios.post(
      utils.apiUrl('dashboards/dashboard/report', 'remove'),
      data
    )
  },

  saveDashboard(data) {
    return axios.post(utils.apiUrl('dashboards/dashboard', 'save'), data)
  }
}
