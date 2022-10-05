import Router from 'vue-router'
import Vue from 'vue'

import axios from 'axios'

import Embed from '@/Embed'
import flaskContext from '@/utils/flask'
import router from '@/router/embed'

// Router config
Vue.use(Router)

// Axios config
axios.defaults.headers.common['X-JSON-SCHEME'] = 'camel'

// Flask context
Vue.prototype.$flask = flaskContext()

new Vue({
  el: '#app',
  router,
  render: (h) => h(Embed),
})
