import axios from 'axios'
import utils from '@/utils/utils'

export default {
  index() {
    return axios.get(utils.apiUrl('repos'))
  },

  file(id) {
    return axios.get(utils.apiUrl('repos', `file/${id}`))
  },

  lint() {
    return axios.get(utils.apiUrl('repos', 'lint'))
  },

  sync() {
    return axios.get(utils.apiUrl('repos', 'sync'))
  },

  models() {
    return axios.get(utils.apiUrl('repos', 'models'))
  }
}
