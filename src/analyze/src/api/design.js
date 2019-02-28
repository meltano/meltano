import axios from 'axios';
import utils from '@/utils/utils';

export default {
  index(model, design) {
    return axios.get(utils.buildUrl('repos/designs', `${model}/${design}`));
  },

  getTable(table) {
    return axios.get(utils.buildUrl('repos/tables', `${table}`));
  },
};
