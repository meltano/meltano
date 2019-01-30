import axios from 'axios';
import utils from './utils';

export default {
  getDashboards() {
    return axios.get(utils.buildUrl('dashboards', 'all'));
  },
  getDashboard(id) {
    return axios.get(utils.buildUrl('dashboards/dashboard', `${id}`));
  },
  saveDashboard(data) {
    return axios.post(utils.buildUrl('dashboards/dashboard', 'save'), data);
  },
  addReportToDashboard(data) {
    return axios.post(utils.buildUrl('dashboards/dashboard/report', 'add'), data);
  },
  removeReportFromDashboard(data) {
    return axios.post(utils.buildUrl('dashboards/dashboard/report', 'remove'), data);
  },
};
