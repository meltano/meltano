import Router from 'vue-router'
import Toasted from 'vue-toasted'
import Vue from 'vue'
import axios from 'axios'
import lodash from 'lodash'

import Auth from '@/middleware/auth'
import FatalError from '@/middleware/fatalError'
import flaskContext from '@/flask'

import FontAwesome from './font-awesome'
import App from './App'
import router from './router'
import store from './store'

Vue.config.productionTip = false

Vue.use(Router)
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

Vue.use(Auth, {
  router,
  toasted: Vue.toasted
})

Vue.use(FatalError, {
  router,
  toasted: Vue.toasted
})

// Register a Global Forbidden Error Notification Toast.
Vue.toasted.register(
  'forbidden',
  "You can't access this resource at this moment.",
  {
    type: 'error'
  }
)
// Register a Global General Error Notification Toast.
Vue.toasted.register('oops', 'Oops! Something went wrong.', {
  type: 'error',
  action: [
    {
      text: 'Submit Bug',
      onClick: () => {
        window.open(
          'https://gitlab.com/meltano/meltano/issues/new?issue%5Bassignee_id%5D=&issue%5Bmilestone_id%5D=&issuable_template=bugs'
        )
      }
    },
    {
      text: 'Close',
      onClick: (e, toastObject) => {
        toastObject.goAway(0)
      }
    }
  ]
})

// Register a Global success notification
Vue.toasted.register(
  'success',
  message => message,
  Object.assign(lodash.cloneDeep(toastedOptions), {
    duration: 4000,
    type: 'success'
  })
)

// Register a Global error notification
Vue.toasted.register(
  'error',
  message => message,
  Object.assign(lodash.cloneDeep(toastedOptions), {
    duration: 5000,
    type: 'error'
  })
)

// Axios config
axios.defaults.headers.common['X-JSON-SCHEME'] = 'camel'

// Flask context
Vue.prototype.$flask = flaskContext()

/* eslint-disable no-new */
new Vue({
  el: '#app',
  store,
  router,
  render: h => h(App)
})

// Analytics SPA route change hook (no initial ping as the gtag init step does this automatically)
router.afterEach(to => {
  if (window.gtag) {
    window.gtag('config', 'UA-132758957-2', {
      page_title: to.name,
      page_path: to.path
    })
  }
})
