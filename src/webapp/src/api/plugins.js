import axios from 'axios'
import utils from '@/utils/utils'

export default {
  addPlugin(addConfig) {
    return axios.post(utils.apiUrl('plugins', 'add'), addConfig)
  },

  getInstalledPlugins() {
    return axios.get(utils.apiUrl('plugins', 'installed'))
  },

  getPlugins() {
    return axios.get(utils.apiUrl('plugins', 'all'))
  },

  installBatch(installConfig) {
    return axios.post(utils.apiUrl('plugins', 'install/batch'), installConfig)
  },

  installPlugin(installConfig) {
    return axios.post(utils.apiUrl('plugins', 'install'), installConfig)
  },
}
