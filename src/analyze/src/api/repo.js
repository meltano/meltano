import axios from 'axios';
import utils from './utils';

export default {
  index() {
    return axios.get(utils.buildUrl('repos'));
  },

  file(id) {
    return axios.get(utils.buildUrl('repos', `file/${id}`));
  },

  lint() {
    return axios.get(utils.buildUrl('repos', 'lint'));
  },

  sync() {
    return axios.get(utils.buildUrl('repos', 'sync'));
  },

  models() {
    return axios.get(utils.buildUrl('repos', 'models'));
  },
};
