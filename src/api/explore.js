import axios from 'axios';
import utils from './utils';

export default {
  index(model, explore) {
    return axios.get(utils.buildUrl('repos/explores', `${model}/${explore}`));
  },

  get_sql(model, explore, data) {
    return axios.post(utils.buildUrl('sql/get', `${model}/${explore}`), data);
  },
};
