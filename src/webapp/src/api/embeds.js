import axios from 'axios'
import utils from '@/utils/utils'

export default {
  generate(payload) {
    return axios.post(utils.apiUrl('reports', 'embed'), payload)
  },
  loadFromToken(token) {
    return axios.get(utils.apiUrl('reports/embed', token))
  }
}
