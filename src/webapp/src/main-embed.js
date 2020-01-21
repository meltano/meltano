import Vue from 'vue'
import store from '@/store'

import Embed from '@/Embed'

new Vue({
  el: '#app',
  store,
  render: h => h(Embed)
})
