import Router from 'vue-router'
import VCalendar from 'v-calendar'
import Vue from 'vue'
import VueIntercom from 'vue-intercom'

import { Service } from 'axios-middleware'
import axios from 'axios'

import App from '@/App'
import Auth from '@/middleware/auth'
import FatalError from '@/middleware/fatalError'
import flaskContext from '@/utils/flask'
import FontAwesome from '@/utils/font-awesome'
import router from '@/router/app'
import setupToasted from '@/utils/setupToasted'
import store from '@/store'
import Upgrade from '@/middleware/upgrade'

Vue.config.productionTip = false

Vue.use(VCalendar)
Vue.use(FontAwesome)
Vue.use(Router)
Vue.use(VueIntercom, { appId: 'ir946q00' })

// Toast setup
setupToasted()

// Middleware setup
const service = new Service(axios)
Vue.use(Upgrade, {
  service,
  router,
  toasted: Vue.toasted,
})
Vue.use(FatalError, {
  service,
  router,
  toasted: Vue.toasted,
})
Vue.use(Auth, {
  service,
  toasted: Vue.toasted,
})

// Axios config
axios.defaults.headers.common['X-JSON-SCHEME'] = 'camel'

// Flask context
Vue.prototype.$flask = Object.freeze(flaskContext())

/* eslint-disable no-new */
new Vue({
  el: '#app',
  store,
  router,
  render: (h) => h(App),
})
