import axios from 'axios';
import utils from './utils';

export default {
  index() {
    return axios.get(utils.buildUrl('dashboards'));
  },
  getDashboards() {
    return axios.get(utils.buildUrl('dashboards', 'all'));
  },
  getDashboard(id) {
    return axios.get(utils.buildUrl('dashboards', `dashboard/${id}`));
  },
};
