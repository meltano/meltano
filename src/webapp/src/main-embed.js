import Vue from 'vue'

import axios from 'axios'

import Embed from '@/Embed'

axios.defaults.headers.common['X-JSON-SCHEME'] = 'camel'

new Vue({
  el: '#app',
  render: h => h(Embed)
})
