import Vue from 'vue'

import axios from 'axios'
import utils from '@/utils/utils'

export default {
  dbtDocs() {
    return axios.get(Vue.prototype.$flask.dbtDocsUrl)
  },

  upgrade() {
    return axios.post(utils.root('/upgrade'))
  },

  version(params) {
    return axios.get(utils.root('/version'), { params })
  },

  identity() {
    return axios.get(utils.apiRoot('/identity'))
  }
}
