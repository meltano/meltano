import axios from 'axios';
import utils from './utils';

export default {
  index() {
    return axios.get(utils.buildUrl('repos'));
  },

  file(unique) {
    return axios.get(utils.buildUrl('repos', `file/${unique}`));
  },

  lint() {
    return axios.get(utils.buildUrl('repos', 'lint'));
  },

  update() {
    return axios.get(utils.buildUrl('repos', 'update'));
  },

  models() {
    return axios.get(utils.buildUrl('repos', 'models'));
  },
};
