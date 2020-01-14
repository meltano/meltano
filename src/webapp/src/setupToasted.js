import Vue from 'vue'

import lodash from 'lodash'
import Toasted from 'vue-toasted'

import router from './router'

export default function setup() {
  const toastedOptions = {
    router,
    position: 'bottom-right',
    iconPack: 'fontawesome',
    theme: 'outline',
    duration: 9000
  }
  Vue.use(Toasted, toastedOptions)

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
        text: 'Get Help',
        onClick: () => {
          window.open('https://meltano.com/docs/getting-help.html')
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
          text: 'Disable',
          onClick: (e, toastObject) => {
            toastObject.goAway(0)
            localStorage.setItem('hasDisabledTracking', true)
            localStorage.setItem('hasAcknowledgedTracking', true)
          }
        },
        {
          text: 'Got it',
          onClick: (e, toastObject) => {
            toastObject.goAway(0)
            localStorage.setItem('hasDisabledTracking', false)
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
      type: 'success'
    })
  )

  // Register a Global error notification
  Vue.toasted.register(
    'error',
    message => message,
    Object.assign(lodash.cloneDeep(toastedOptions), {
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

  // Register the `read-only` killswitch notification
  Vue.toasted.register(
    'readonly',
    'Meltano currently runs in read-only mode.',
    {
      type: 'warning',
      duration: 1250,
      singleton: true
    }
  )
}
