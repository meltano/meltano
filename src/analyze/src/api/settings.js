import axios from 'axios';
import utils from './utils';

export default {
  index() {
    return axios.get(utils.buildUrl('settings'));
  },
  saveConnection(connection) {
    return axios.post(utils.buildUrl("settings", "save"), connection);
  },
  deleteConnection(connection) {
    return axios.post(utils.buildUrl('settings', 'delete'), connection);
  }
};
