import Vue from 'vue'
import Vuex from 'vuex'

import configuration from './modules/configuration'
import designs from './modules/designs'
import dashboards from './modules/dashboards'
import plugins from './modules/plugins'
import repos from './modules/repos'
import settings from './modules/settings'

Vue.use(Vuex)

const debug = process.env.NODE_ENV !== 'production'

export default new Vuex.Store({
  modules: {
    configuration,
    designs,
    dashboards,
    plugins,
    repos,
    settings
  },
  string: debug
})
