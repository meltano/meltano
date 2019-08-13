import axios from 'axios'
import utils from '@/utils/utils'

export default {
  getSql(model, design, data) {
    return axios.post(utils.apiUrl('sql/get', `${model}/${design}`), data)
  },

  getDistinct(model, design, field) {
    return axios.post(utils.apiUrl('sql/distinct', `${model}/${design}`), {
      field
    })
  },

  getDialect(model) {
    return axios.get(utils.apiUrl('sql/get', `${model}/dialect`))
  },

  getFilterOptions() {
    return axios.get(utils.apiUrl('sql/get', 'filter-options'))
  }
}
