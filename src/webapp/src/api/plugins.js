import axios from 'axios'
import utils from '@/utils/utils'

export default {
  getAllPlugins() {
    return axios.get(utils.apiUrl('plugins', 'all'))
  },

  getInstalledPlugins() {
    return axios.get(utils.apiUrl('plugins', 'installed'))
  },

  installBatch(installConfig) {
    return axios.post(utils.apiUrl('plugins', 'install/batch'), installConfig)
  },

  installPlugin(installConfig) {
    return axios.post(utils.apiUrl('plugins', 'install'), installConfig)
  },

  addPlugin(addConfig) {
    return axios.post(utils.apiUrl('plugins', 'add'), addConfig)
  }
}
