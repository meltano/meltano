import axios from 'axios';
import utils from './utils';

export default {
  index() {
    return axios.get(utils.buildUrl('repos'));
  },

  blob(sha) {
    return axios.get(utils.buildUrl('repos', `blobs/${sha}`));
  },

  lint() {
    return axios.get(utils.buildUrl('repos', 'lint'));
  },

  update() {
    return axios.get(utils.buildUrl('repos', 'update'));
  },
};
