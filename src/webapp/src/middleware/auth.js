import utils from '@/utils/utils'

export class AuthMiddleware {
  constructor({ toasted }) {
    this.$toasted = toasted
  }

  onRequest(req) {
    // Enable the sending of cookie cross-domain,
    // which enables the API to use the Session
    //
    // As the Session cookie is set for a specific
    // domain, we can safely toggle this on for
    // all XHRs without fear of having the session
    // hijacked.
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
        toasted,
      })
    )
  },
}
