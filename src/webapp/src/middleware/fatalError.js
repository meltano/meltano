export class FatalErrorMiddleware {
  constructor({ toasted }) {
    this.toasted = toasted
  }

  onResponseError(err) {
    // eslint-disable-line class-methods-use-this
    if (err.response && err.response.status === 500) {
      this.toasted.global.oops()
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
  }
}
