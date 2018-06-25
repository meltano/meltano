import axios from 'axios';
import utils from './utils';

export default {
  index(model, explore) {
    return axios.get(utils.buildUrl('repos/explores', `${model}/${explore}`));
  },

  getSql(model, explore, data) {
    return axios.post(utils.buildUrl('sql/get', `${model}/${explore}`), data);
  },

  getDistinct(model, explore, field) {
    return axios.post(utils.buildUrl('sql/distinct', `${model}/${explore}`), { field });
  },
};
