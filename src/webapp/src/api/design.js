import axios from 'axios'
import utils from '@/utils/utils'

export const QUERY_ATTRIBUTE_TYPES = Object.freeze({
  COLUMN: 'column',
  AGGREGATE: 'aggregate',
  TIMEFRAME: 'timeframe'
})

export const QUERY_ATTRIBUTE_DATA_TYPES = Object.freeze({
  DATE: 'date',
  STRING: 'string',
  TIME: 'time'
})

export default {
  getTable(table) {
    return axios.get(utils.apiUrl('repos/tables', `${table}`))
  },

  getTopic(namespace, model) {
    return axios.get(utils.apiUrl('repos/models', `${namespace}/${model}`))
  },

  index(namespace, model, design) {
    return axios.get(
      utils.apiUrl('repos/designs', `${namespace}/${model}/${design}`)
    )
  }
}
