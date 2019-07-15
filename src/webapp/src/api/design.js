import axios from 'axios'
import utils from '@/utils/utils'

export default {
  index(model, design) {
    return axios.get(utils.apiUrl('repos/designs', `${model}/${design}`))
  },

  getTable(table) {
    return axios.get(utils.apiUrl('repos/tables', `${table}`))
  }
}
