import axios from 'axios';
import utils from '@/utils/utils';

export default {
  getAllPlugins() {
    return axios.get(utils.apiUrl('plugins', 'all'));
  },

  getInstalledPlugins() {
    return axios.get(utils.apiUrl('plugins', 'installed'));
  },

  installPlugin(installConfig) {
    return axios.post(utils.apiUrl('plugins', 'install'), installConfig);
  },
};
