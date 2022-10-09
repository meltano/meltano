import axios from 'axios'
import utils from '@/utils/utils'

export default {
  index() {
    return axios.get(utils.apiUrl('repos'))
  },

  lint() {
    return axios.get(utils.apiUrl('repos', 'lint'))
  },

  models() {
    return axios.get(utils.apiUrl('repos', 'models'))
  },

  sync() {
    return axios.get(utils.apiUrl('repos', 'sync'))
  },
}
