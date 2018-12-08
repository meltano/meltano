import axios from 'axios';
import utils from './utils';

export default {
  index() {
    return axios.get(utils.buildUrl('settings'));
  },
  deleteConnection(connection) {
    return axios.delete(utils.buildUrl("settings", "delete"), connection);
  },
  save(data) {
    return axios.post(utils.buildUrl('settings', 'new'), data);
  },
};
