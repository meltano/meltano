import axios from 'axios';
import utils from './utils';

export default {
  index() {
    return axios.get(utils.buildUrl('settings'));
  },

  save(data) {
    return axios.post(utils.buildUrl('settings', 'new'), data);
  },
};
