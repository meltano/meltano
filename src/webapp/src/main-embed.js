import Router from 'vue-router'
import Vue from 'vue'

import axios from 'axios'

import Embed from '@/Embed'
import router from '@/router/embed'

Vue.use(Router)

axios.defaults.headers.common['X-JSON-SCHEME'] = 'camel'

new Vue({
  el: '#app',
  router,
  render: h => h(Embed)
})
