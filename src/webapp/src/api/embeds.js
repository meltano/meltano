import axios from 'axios'
import utils from '@/utils/utils'

export const EMBED_RESOURCE_TYPES = Object.freeze({
  DASHBOARD: 'dashboard',
  REPORT: 'report'
})

export default {
  generate(payload) {
    return axios.post(utils.apiUrl('embeds', 'embed'), payload)
  },
  load(token) {
    return axios.get(utils.apiUrl('embeds/embed', token))
  }
}
