import utils from '@/utils/utils'

export class AuthMiddleware {
  constructor({ toasted }) {
    this.$toasted = toasted
  }

  onRequest(req) {
    // enable the sending of cookie
    req.withCredentials = true

    return req
  }

  onResponseError(err) {
    // eslint-disable-line class-methods-use-this
    if (!err.response) {
      throw err
    }

    switch (err.response.status) {
      case 401:
        window.location.href = utils.root('/auth/login')
        break
      case 403:
        this.$toasted.global.forbidden()
        break
      default:
        break
    }

    throw err
  }
}

export default {
  install(Vue, { service, toasted }) {
    service.register(
      new AuthMiddleware({
        toasted
      })
    )
  }
}
