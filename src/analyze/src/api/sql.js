import axios from 'axios';
import utils from './utils';

export default {
  getSql(model, design, data) {
    return axios.post(utils.buildUrl('sql/get', `${model}/${design}`), data);
  },

  getDialect(model) {
    return axios.get(utils.buildUrl('sql/get', `${model}/dialect`));
  },

  getDistinct(model, design, field) {
    return axios.post(utils.buildUrl('sql/distinct', `${model}/${design}`), { field });
  },
};
