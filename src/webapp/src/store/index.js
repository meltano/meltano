import Vue from 'vue'
import Vuex from 'vuex'

import designs from './modules/designs'
import dashboards from './modules/dashboards'
import orchestration from './modules/orchestration'
import plugins from './modules/plugins'
import repos from './modules/repos'
import settings from './modules/settings'
import system from './modules/system'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    designs,
    dashboards,
    orchestration,
    plugins,
    repos,
    settings,
    system
  },
  strict: process.env.NODE_ENV !== 'production'
})
