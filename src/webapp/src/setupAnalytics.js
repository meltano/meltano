import Vue from 'vue'

import VueAnalytics from 'vue-analytics'

import router from './router'

export default function setup() {
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
