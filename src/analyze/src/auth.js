import Vue from 'vue';
import axios from 'axios';
import { Service } from 'axios-middleware';
import jwtDecode from 'jwt-decode';


export class AuthMiddleware {
  constructor({ handler, router }) {
    this.auth = handler;
    this.router = router;
  }

  onRequest(req) {
    req.headers.Authorization = `Bearer ${this.auth.authToken}`;

    return req;
  }

  onResponseError(err) { // eslint-disable-line class-methods-use-this
    if (err.response && err.response.status === 403) {
      Vue.toasted.global.forbidden();
      throw err;
    }

    // 401 should be sent to login
    if (err.response && err.response.status === 401) {
      window.location.href = 'http://localhost:5000/auth/login';
    }

    // 422 should be sent when the JWT is invalid
    if (err.response && err.response.status === 422) {
      window.location.href = 'http://localhost:5000/auth/bootstrap';
    }

    throw err;
  }
}

class AuthHandler {
  constructor() {
    this.tokens = {};
  }

  authenticate(authToken) {
    this.tokens = {
      auth: authToken,
    };
  }

  get authToken() {
    if (!this.tokens.auth) {
      this.tokens.auth = window.localStorage.getItem('authToken');
    }

    return this.tokens.auth;
  }

  set authToken(token) {
    this.tokens.auth = token;

    if (token) {
      debugger;
      window.localStorage.setItem('authToken', token);
    } else {
      window.localStorage.removeItem('authToken');
    }
  }

  logout() {
    this.authToken = null;

    window.location.href = 'http://localhost:5000/auth/logout';
  }

  authenticated() {
    return this.authToken;
  }

  ensureAuthenticated() {
    if (!this.authenticated()) {
      window.location.href = 'http://localhost:5000/auth/bootstrap';
    }
  }

  get user() {
    if (!this.authToken) {
      return null;
    }

    const jwt = jwtDecode(this.authToken);

    if (jwt.identity.id === null) {
      return null;
    }

    return jwt.identity;
  }
}


export default {
  install(vue, options) {
    const service = new Service(axios);
    const handler = new AuthHandler();

    vue.mixin({
      beforeRouteEnter(to, from, next) {
        const {
          auth_token: authToken,
        } = to.query;

        if (authToken) {
          handler.authenticate(authToken);
        } else {
          handler.ensureAuthenticated();
        }

        next();
      },
    });

    vue.prototype.$auth = handler;
    service.register(new AuthMiddleware({
      handler,
      router: options.router,
    }));
  },
};
