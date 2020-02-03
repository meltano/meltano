import Vue from 'vue'

import VueAnalytics from 'vue-analytics'

export default function setup(router, isEmbedApp = false) {
  const isDisabled =
    'hasDisabledTracking' in localStorage &&
    localStorage.getItem('hasDisabledTracking') === 'true'

  if (!isDisabled) {
    // GA property ID determined by GA console (2 = Meltano UI & 6 = Meltano Embed UI)
    const propertyId = isEmbedApp ? '6' : '2'
    Vue.use(VueAnalytics, {
      id: `UA-132758957-${propertyId}`,
      router,
      set: [
        {
          // Unfortunately custom dimensions don't allow a useful alias, dimension1 is projectId
          field: 'dimension1',
          value: Vue.prototype.$flask.projectId
        },
        {
          // Unfortunately custom dimensions don't allow a useful alias, dimension2 is the Meltano app version
          field: 'dimension2',
          value: Vue.prototype.$flask.version
        }
      ]
    })
  }
}
