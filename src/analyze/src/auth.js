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
    const token = this.auth.authToken;

    if (req.headers.Authorization === undefined) {
      req.headers.Authorization = `Bearer ${token}`;
    }

    return req;
  }

  onResponseError(err) {
    if (err.response && err.response.status === 403) {
      Vue.toasted.global.forbidden();
      throw err;
    }

    while (err.response
        && !err.config.retried
        && err.response.status === 401) {
      err.config.retried = true;
      return this.auth.refresh().then(() => {
        // let's retry the call
        delete err.config.headers.Authorization;
        return axios(err.config);
      });
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

  authenticate(authToken, refreshToken) {
    this.tokens = {
      auth: authToken,
      refresh: refreshToken,
    };
  }

  refresh() {
    const headers = { Authorization: `Bearer ${this.refreshToken}` };
    return axios.get('http://localhost:5000/auth/refresh_token', { headers })
      .then((response) => {
        this.authenticate(response.data.auth_token, this.refreshToken);
      });
  }

  get authToken() {
    if (!this.tokens.auth) {
      this.tokens.auth = window.localStorage.getItem('authToken');
    }

    return this.tokens.auth;
  }


  get refreshToken() {
    if (!this.tokens.refresh) {
      this.tokens.refresh = window.localStorage.getItem('refreshToken');
    }

    return this.tokens.refresh;
  }

  set authToken(token) {
    this.tokens.auth = token;

    if (token) {
      window.localStorage.setItem('authToken', token);
    } else {
      window.localStorage.removeItem('authToken');
    }
  }

  set refreshToken(token) {
    this.tokens.refresh = token;

    if (token) {
      window.localStorage.setItem('refreshToken', token);
    } else {
      window.localStorage.removeItem('refreshToken');
    }
  }

  logout() {
    this.authToken = null;
    this.refreshToken = null;

    window.location.href = 'http://localhost:5000/auth/logout';
  }

  authenticated() {
    return this.authToken && this.refreshToken;
  }

  ensureAuthenticated() {
    if (!this.authenticated()) {
      window.location.href = 'http://localhost:5000/auth/bootstrap';
    }
  }

  get user() {
    const jwt = jwtDecode(this.tokens.auth);

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
          refresh_token: refreshToken,
        } = to.query;

        if (authToken && refreshToken) {
          handler.authenticate(authToken, refreshToken);
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
