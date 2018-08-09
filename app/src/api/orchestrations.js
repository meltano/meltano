import axios from 'axios';
import utils from './utils';

export default {
  index() {
    return axios.get(utils.buildUrl('orchestrations'));
  },

  run(payload) {
    return axios.post(utils.buildUrl('orchestrations', 'run'), payload);
  }
};
