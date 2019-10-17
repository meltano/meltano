import Vue from 'vue'

import lodash from 'lodash'

export default {
  initialize(toastedOptions) {
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

    // Register an analytics tracking notification Toast.
    Vue.toasted.register(
      'acknowledgeAnalyticsTracking',
      'Meltano has anonymous usage tracking on.',
      {
        type: 'info',
        action: [
          {
            text: 'Learn more',
            onClick: () => {
              window.open(
                'https://www.meltano.com/docs/environment-variables.html#anonymous-usage-data'
              )
            }
          },
          {
            text: 'Got it',
            onClick: (e, toastObject) => {
              toastObject.goAway(0)
              localStorage.setItem('hasAcknowledgedTracking', true)
            }
          }
        ],
        duration: null
      }
    )

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

    // Register a Global error notification
    Vue.toasted.register(
      'upgrade',
      'A new version of Meltano is available, please refresh.',
      {
        action: [
          {
            text: 'Refresh!',
            onClick: () => document.location.reload()
          }
        ],
        duration: null,
        closeOnSwipe: false,
        singleton: true,
        type: 'info'
      }
    )
  }
}
