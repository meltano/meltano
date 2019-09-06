import axios from 'axios'
import utils from '@/utils/utils'

export default {
  version() {
    return axios.get(utils.root('/version'))
  },

  upgrade() {
    return axios.post(utils.root('/upgrade'))
  }
}
