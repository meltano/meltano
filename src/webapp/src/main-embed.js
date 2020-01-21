import Vue from 'vue'

import Embed from '@/Embed'
import store from '@/store'

new Vue({
  el: '#app',
  store,
  render: h => h(Embed)
})
