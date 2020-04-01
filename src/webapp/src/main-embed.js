import Router from 'vue-router'
import Vue from 'vue'

import axios from 'axios'

import Embed from '@/Embed'
import flaskContext from '@/utils/flask'
import router from '@/router/embed'
import setupAnalytics from '@/utils/setupAnalytics'

// Router config
Vue.use(Router)

// Axios config
axios.defaults.headers.common['X-JSON-SCHEME'] = 'camel'

// Flask context
Vue.prototype.$flask = flaskContext()

// Conditional analytics using flask context
if (Vue.prototype.$flask.isSendAnonymousUsageStats) {
  setupAnalytics({ id: Vue.prototype.$flask.embedTrackingID, router })
}

new Vue({
  el: '#app',
  router,
  render: h => h(Embed)
})
