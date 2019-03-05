import Vue from 'vue';
import axios from 'axios';
import { Service } from 'axios-middleware';


export class AuthMiddleware {
  constructor({ handler, router }) {
    this.auth = handler;
    this.router = router;
  }

  onRequest(req) {
    const token = this.auth.authToken;

    if (req.headers["Authorization"] === undefined) {
      req.headers["Authorization"] = `Bearer ${token}`;
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
      return this.auth.refresh().then(response => {
        delete err.config.headers["Authorization"];
        return axios(err.config);
      });
    }

    // 422 should be sent when the JWT is invalid
    if (err.response && err.response.status === 422) {
      window.location.href = "http://localhost:5000/auth/bootstrap";
    }

    throw err;
  }
}

class AuthHandler {
  authenticate(authToken, refreshToken) {
    this.authToken = authToken;
    this.refreshToken = refreshToken;
  }

  refresh() {
    const headers = { "Authorization": `Bearer ${this.refreshToken}` };
    return axios.get("http://localhost:5000/auth/refresh_token", { headers })
                .then(response => {
                  console.log("Refreshed the token.")
                  this.authenticate(response.data["auth_token"], this.refreshToken)
                })
  }

  get authToken() {
    if (!this._authToken) {
      this._authToken = window.localStorage.getItem("authToken");
    }

    return this._authToken
  }


  get refreshToken() {
    if (!this._refreshToken) {
      this._refreshToken = window.localStorage.getItem("refreshToken");
    }

    return this._refreshToken;
  }

  set authToken(token) {
    this._authToken = token;

    if (this._authToken) {
      window.localStorage.setItem("authToken", this.authToken);
    } else {
      window.localStorage.removeItem("authToken");
    }
  }

  set refreshToken(token) {
    this._refreshToken = token;

    if (this._refreshToken) {
      window.localStorage.setItem("refreshToken", this.refreshToken);
    } else {
      window.localStorage.removeItem("refreshToken");
    }
  }

  logout() {
    this.authToken = null;
    this.refreshToken = null;

    window.localStorage.removeItem("refreshToken");
    window.localStorage.removeItem("authToken");

    window.location.href = "http://localhost:5000/auth/logout";
  }

  authenticated() {
    return this.authToken !== undefined
        && this.refreshToken !== undefined;
  }

  ensureAuthenticated() {
    if (!this.authenticated()) {
      window.location.href = "http://localhost:5000/auth/bootstrap";
    }
  }
}


export default {
  install(Vue, options) {
    const service = new Service(axios);
    const handler = new AuthHandler();

    Vue.mixin({
      beforeRouteEnter(to, from, next) {
        const { auth_token, refresh_token } = to.query;

        if (auth_token && refresh_token) {
          handler.authenticate(auth_token, refresh_token);
        } else {
          handler.ensureAuthenticated();
        }

        next()
      }
    })

    Vue.prototype.$auth = handler;
    service.register(new AuthMiddleware({
      handler,
      router: options.router,
    }));
  }
};
