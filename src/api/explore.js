import axios from 'axios';
import utils from './utils';

export default {
  index(model, explore) {
    return axios.get(utils.buildUrl('repos/explores', `${model}/${explore}`));
  },

  run(model, explore, data) {
    return axios.post(utils.buildUrl('sql', `${model}/${explore}`), data);
  },
};
