import axios from 'axios';
import utils from '@/utils/utils';

export default {
  getAllPlugins() {
    return axios.get(utils.apiUrl('orchestrations'));
  },

  getInstalledPlugins() {
    return axios.get(utils.apiUrl('orchestrations', 'installed-plugins'));
  },

  installPlugin(installConfig) {
    return axios.post(utils.apiUrl('orchestrations', 'install-plugin'), installConfig);
  },
};
