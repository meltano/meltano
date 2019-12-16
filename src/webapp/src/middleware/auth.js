import utils from '@/utils/utils'
import jwtDecode from 'jwt-decode'

export class AuthMiddleware {
  constructor({ handler, router, toasted }) {
    this.auth = handler
    this.router = router
    this.toasted = toasted
  }

  onRequest(req) {
    if (req.url.startsWith(utils.apiRoot())) {
      // enable the sending of cookies
      req.withCredentials = true
    }

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
        this.toasted.global.forbidden()
        break
      default:
        break
    }

    throw err
  }
}

class AuthHandler {
  constructor() {
    this.tokens = {
      auth: null
    }
  }

  authenticate(authToken) {
    this.authToken = authToken
  }

  get authToken() {
    if (!this.tokens.auth) {
      this.tokens.auth = window.localStorage.getItem('authToken')
    }

    return this.tokens.auth
  }

  set authToken(token) {
    this.tokens.auth = token

    if (token) {
      window.localStorage.setItem('authToken', token)
    } else {
      window.localStorage.removeItem('authToken')
    }
  }

  logout() {
    this.authToken = null

    window.location.href = utils.root('/auth/logout')
  }

  authenticated() {
    return this.authToken
  }

  get user() {
    if (!this.authToken) {
      return null
    }

    const jwt = jwtDecode(this.authToken)

    // that means the current token is either invalid
    // we should ignore it
    if (!jwt.identity.id) {
      return null
    }

    return jwt.identity
  }
}

export default {
  install(Vue, { router, service, toasted }) {
    const handler = new AuthHandler()

    Vue.mixin({
      beforeRouteEnter(to, from, next) {
        const { auth_token: authToken } = to.query

        if (authToken) {
          handler.authenticate(authToken)
        }

        next()
      }
    })

    Vue.prototype.$auth = handler
    service.register(
      new AuthMiddleware({
        handler,
        router,
        toasted
      })
    )
  }
}
