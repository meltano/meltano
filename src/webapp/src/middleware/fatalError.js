import axios from 'axios'
import { Service } from 'axios-middleware'

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
  install(Vue, options) {
    const service = new Service(axios)

    service.register(
      new FatalErrorMiddleware({
        toasted: options.toasted
      })
    )
  }
}
