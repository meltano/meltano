import Router from 'vue-router'
import Toasted from 'vue-toasted'
import Vue from 'vue'
import VueAnalytics from 'vue-analytics'
import axios from 'axios'
import { Service } from 'axios-middleware'

import App from './App'
import Auth from '@/middleware/auth'
import FatalError from '@/middleware/fatalError'
import FontAwesome from '@/font-awesome'
import flaskContext from '@/flask'
import toastedHelper from '@/toastedHelper'
import router from './router'
import store from './store'
import Upgrade from '@/middleware/upgrade'

Vue.config.productionTip = false

Vue.use(FontAwesome)
Vue.use(Router)

const toastedOptions = {
  router,
  position: 'bottom-right',
  iconPack: 'fontawesome',
  theme: 'outline',
  duration: 9000
}
Vue.use(Toasted, toastedOptions)
toastedHelper.initialize(toastedOptions)

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
  router,
  toasted: Vue.toasted
})

// Axios config
axios.defaults.headers.common['X-JSON-SCHEME'] = 'camel'

// Flask context
Vue.prototype.$flask = flaskContext()

// Conditional analytics using flask context
if (Vue.prototype.$flask.isSendAnonymousUsageStats) {
  Vue.use(VueAnalytics, {
    id: 'UA-132758957-2',
    router,
    set: [
      {
        field: 'appVersion',
        value: Vue.prototype.$flask.version
      },
      {
        // Unfortunately custom dimensions don't allow a useful alias, dimension1 is projectId
        field: 'dimension1',
        value: Vue.prototype.$flask.projectId
      }
    ]
  })
}

/* eslint-disable no-new */
new Vue({
  el: '#app',
  store,
  router,
  render: h => h(App)
})
