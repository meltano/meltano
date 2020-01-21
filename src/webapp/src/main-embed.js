import Vue from 'vue'
import store from './store'

// here you can use all our components as if
// you were in the app
import Logo from '@/components/navigation/Logo'

new Vue({
  el: "#app",
  store,
  render: h => h(Logo)
})
