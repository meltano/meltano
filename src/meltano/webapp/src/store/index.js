import Vue from 'vue'
import Vuex from 'vuex'

import orchestration from './modules/orchestration'
import plugins from './modules/plugins'
import repos from './modules/repos'
import settings from './modules/settings'
import system from './modules/system'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    orchestration,
    plugins,
    repos,
    settings,
    system,
  },
  strict: process.env.NODE_ENV !== 'production',
})
