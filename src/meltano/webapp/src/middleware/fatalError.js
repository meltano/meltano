export class FatalErrorMiddleware {
  constructor({ toasted }) {
    this.toasted = toasted
  }

  onResponseError(err) {
    // eslint-disable-line class-methods-use-this
    if (err.response && err.response.status === 500) {
      err.handled = true
      this.toasted.global.oops()
    }

    if (err.response && err.response.status == 499) {
      err.handled = true
      const rawData = err.response.data
      const data = JSON.parse(rawData)
      this.toasted.global.readonly(data.code)
    }

    // Catch generic "Network Error"s that may indicate an Ad Blocker is in use
    if (
      !err.response &&
      err.message === 'Network Error' &&
      /adwords|ads|analytics/.test(err.config.url)
    ) {
      this.toasted.global.error(
        'The action was blocked, but the browser did not specify why. ' +
          'If you are using an extension to block ads or tracking tools, it may have been triggered accidentally. ' +
          'Consider disabling it for this domain, and try again.'
      )
    }

    throw err
  }
}

export default {
  install(Vue, { service, toasted }) {
    service.register(
      new FatalErrorMiddleware({
        toasted,
      })
    )

    Vue.prototype.$error = {
      handle(err) {
        if (!err.response) {
          throw err
        }

        if (err.handled) {
          return
        }

        toasted.global.error(err.response.data.code)
        err.handled = true
      },
    }
  },
}
