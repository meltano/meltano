import axios from 'axios';
import utils from '@/utils/utils';

export default {
  index(slug, model, design) {
    return axios.get(utils.apiUrl('repos/projects', `${slug}/designs/${model}/${design}`));
  },

  getTable(table) {
    return axios.get(utils.apiUrl('repos/tables', `${table}`));
  },
};
