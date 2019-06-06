import axios from 'axios';
import utils from '@/utils/utils';

export default {
  getPlugins() {
    return axios.get(utils.apiUrl('plugins', 'get/all'));
  },
};
