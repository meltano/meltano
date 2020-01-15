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
      this.toasted.global.readonly()
    }

    throw err
  }
}

export default {
  install(Vue, { service, toasted }) {
    service.register(
      new FatalErrorMiddleware({
        toasted
      })
    )

    Vue.prototype.$error = {
      handle(err) {
        if (err.handled) {
          return
        }

        toasted.global.error(err.response.data.code)
        err.handled = true
      }
    }
  }
}
