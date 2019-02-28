import axios from 'axios';
import { Service } from 'axios-middleware';


export class AuthMiddleware {
  constructor(handler) {
    this.auth = handler;
  }

  onRequest(req) {
    // this.auth.ensureToken();
    req.headers["Authorization"] = `Bearer ${this.auth.token}`;
    return req;
  }

  onResponseError(err) {
    if (err.response && err.response.status !== 401) {
      return err.response;
    }
  }
}

class AuthHandler {
  authenticate(token) {
    this.token = token;

    window.localStorage.setItem("auth_token", this.token);
  }

  logout() {
    debugger
    this.token = undefined;
    window.localStorage.removeItem("auth_token");
    window.location.href = "http://localhost:5000/auth/logout"
  }

  ensureToken() {
    if (this.token !== undefined) {
      return;
    }

    const savedToken = window.localStorage.getItem("auth_token");

    if (savedToken !== undefined) {
      this.authenticate(savedToken);
      return;
    }

    // or try to authenticate
    window.location.href = "http://localhost:5000/auth/login";
  }
}


export default {
  install(Vue, options) {
    const service = new Service(axios);
    const handler = new AuthHandler();

    Vue.mixin({
      beforeRouteEnter(to, from, next) {
        const token = to.query.auth_token;

        if (token !== undefined) {
          handler.authenticate(token);
        } else {
          handler.ensureToken();
        }

        next();
      }
    })

    Vue.prototype.$auth = handler;
    service.register(new AuthMiddleware(handler));
  }
};
