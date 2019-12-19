import Router from 'vue-router'
import Vue from 'vue'

import { Service } from 'axios-middleware'
import axios from 'axios'

import App from './App'
import Auth from '@/middleware/auth'
import FatalError from '@/middleware/fatalError'
import FontAwesome from '@/font-awesome'
import flaskContext from '@/flask'
import setupAnalytics from '@/setupAnalytics'
import setupToasted from '@/setupToasted'
import router from './router'
import store from './store'
import Upgrade from '@/middleware/upgrade'

Vue.config.productionTip = false

Vue.use(FontAwesome)
Vue.use(Router)

// Toast setup
setupToasted()

// Middleware setup
const service = new Service(axios)
Vue.use(Upgrade, {
  service,
  router,
  toasted: Vue.toasted
})
Vue.use(FatalError, {
  service,
  router,
  toasted: Vue.toasted
})
Vue.use(Auth, {
  service,
  toasted: Vue.toasted
})

// Axios config
axios.defaults.headers.common['X-JSON-SCHEME'] = 'camel'

// Flask context
Vue.prototype.$flask = flaskContext()

// Conditional analytics using flask context
if (Vue.prototype.$flask.isSendAnonymousUsageStats) {
  setupAnalytics()
}

/* eslint-disable no-new */
new Vue({
  el: '#app',
  store,
  router,
  render: h => h(App)
})
