import axios from 'axios'
import utils from '@/utils/utils'

export default {
  getTable(table) {
    return axios.get(utils.apiUrl('repos/tables', `${table}`))
  },

  index(model, design) {
    return axios.get(utils.apiUrl('repos/designs', `${model}/${design}`))
  }
}
