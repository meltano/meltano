import axios from 'axios';
import utils from './utils';

export default {
  index() {
    return axios.get(utils.buildUrl('/'));
  },
  getDashboard(id) {
    return axios.get(utils.buildUrl('dashboards', `${id}`));
  },
};
