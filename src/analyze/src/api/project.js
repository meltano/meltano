import axios from 'axios';
import utils from './utils';

export default {
  index() {
    return axios.get(utils.buildUrl('projects'));
  },

  add(payload) {
    return axios.post(utils.buildUrl('projects', 'new'), payload);
  },
};
