import axios from 'axios'
import utils from '@/utils/utils'

export default {
  upgrade() {
    return axios.post(utils.root('/upgrade'))
  },

  version(params) {
    return axios.get(utils.root('/version'), { params })
  }
}
