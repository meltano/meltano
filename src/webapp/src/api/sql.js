import axios from 'axios'
import utils from '@/utils/utils'

export default {
  getDialect(model) {
    return axios.get(utils.apiUrl('sql/get', `${model}/dialect`))
  },

  getDistinct(model, design, field) {
    return axios.post(utils.apiUrl('sql/distinct', `${model}/${design}`), {
      field
    })
  },

  getFilterOptions() {
    return axios.get(utils.apiUrl('sql/get', 'filter-options'))
  },

  getSql(model, design, data) {
    return axios.post(utils.apiUrl('sql/get', `${model}/${design}`), data)
  }
}
