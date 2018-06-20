import axios from 'axios';
import utils from './utils';

export default {
  index(model, explore) {
    return axios.get(utils.buildUrl('repos/explores', `${model}/${explore}`));
  },
};
