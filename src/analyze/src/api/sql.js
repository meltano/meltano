import axios from 'axios';
import utils from '@/utils/utils';

export default {
  getSql(model, design, data) {
    return axios.post(utils.apiUrl('sql/get', `${model}/${design}`), data);
  },

  getDialect(slug, model) {
    return axios.get(utils.apiUrl('sql', `projects/${slug}/get/${model}/dialect`));
  },

  getDistinct(model, design, field) {
    return axios.post(utils.apiUrl('sql/distinct', `${model}/${design}`), { field });
  },
};
