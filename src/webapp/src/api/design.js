import axios from 'axios'
import utils from '@/utils/utils'

export const QUERY_ATTRIBUTE_TYPES = Object.freeze({
  COLUMN: 'column',
  AGGREGATE: 'aggregate',
  TIMEFRAME: 'timeframe'
})

export default {
  getTable(table) {
    return axios.get(utils.apiUrl('repos/tables', `${table}`))
  },

  index(namespace, model, design) {
    return axios.get(
      utils.apiUrl('repos/designs', `${namespace}/${model}/${design}`)
    )
  }
}
