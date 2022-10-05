import axios from 'axios'
import utils from '@/utils/utils'

export default {
  upgrade() {
    return axios.post(utils.apiRoot('/upgrade'))
  },

  version(params) {
    return axios.get(utils.apiRoot('/version'), { params })
  },

  identity() {
    return axios.get(utils.apiRoot('/identity'))
  },
}
