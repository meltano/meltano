import Vue from 'vue';
import { library } from '@fortawesome/fontawesome-svg-core';
import {
  faChartBar,
  faChartLine,
  faChartArea,
  faChartPie,
  faGlobeAmericas,
  faCertificate,
  faDotCircle,
  faCaretDown,
  faCaretUp,
  faAngleDown,
  faAngleUp,
  faSearch,
  faHashtag,
  faExclamationTriangle,
  faArrowRight,
} from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon,
  FontAwesomeLayers,
  FontAwesomeLayersText } from '@fortawesome/vue-fontawesome';
import App from './App';
import router from './router';
import store from './store';

import axios from 'axios';
import { Service } from 'axios-middleware';


Vue.config.productionTip = false;

library.add(faChartBar);
library.add(faChartLine);
library.add(faChartArea);
library.add(faChartPie);
library.add(faGlobeAmericas);
library.add(faCertificate);
library.add(faDotCircle);
library.add(faCaretDown);
library.add(faCaretUp);
library.add(faAngleDown);
library.add(faAngleUp);
library.add(faSearch);
library.add(faHashtag);
library.add(faExclamationTriangle);
library.add(faArrowRight);

Vue.component('font-awesome-icon', FontAwesomeIcon);
Vue.component('font-awesome-layers', FontAwesomeLayers);
Vue.component('font-awesome-layers-text', FontAwesomeLayersText);

const service = new Service(axios);

class AuthMiddleware {
  constructor(handler) {
    this.auth = handler;
  }

  onRequest(req) {
    // this.auth.ensureToken();
    req.headers["authentication-token"] = this.auth.token;
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
    window.location.href = "http://localhost:5000/auth/token?redirect=http://localhost:8080";
  }
}


const Auth = {
  install(Vue, options) {
    const handler = new AuthHandler();

    Vue.mixin({
      beforeRouteEnter(to, from, next) {
        const token = to.query.auth_token;

        if (token !== undefined) {
          next(vm => vm.$auth.authenticate(token));
        } else {
          handler.ensureToken();
          next()
        }
      }
    })

    Vue.prototype.$auth = handler;
    service.register(new AuthMiddleware(handler));
  }
};

Vue.use(Auth);

/* eslint-disable no-new */
new Vue({
  el: '#app',
  store,
  router,
  render: h => h(App),
});

Vue.filter('capitalize', (value) => {
  if (!value) {
    return '';
  }
  let newVal = value;
  newVal = newVal.toString();
  return newVal.charAt(0).toUpperCase() + newVal.slice(1);
});

Vue.filter('camelToRegular', value => value.replace(/([A-Z])/g, ' $1'));
Vue.filter('underscoreToSpace', value => value.replace(/_/g, ' '));
