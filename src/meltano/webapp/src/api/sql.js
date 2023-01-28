import axios from 'axios'
import utils from '@/utils/utils'

export default {
  getFilterOptions() {
    return axios.get(utils.apiUrl('sql/get', 'filter-options'))
  },

  getSql(namespace, model, design, data) {
    return axios.post(
      utils.apiUrl('sql/get', `${namespace}/${model}/${design}`),
      data
    )
  },
}
