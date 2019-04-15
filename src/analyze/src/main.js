import Vue from 'vue';
import { library } from '@fortawesome/fontawesome-svg-core';
import {
  faAngleDown,
  faAngleUp,
  faArrowRight,
  faCaretDown,
  faCaretUp,
  faCertificate,
  faChartArea,
  faChartBar,
  faChartLine,
  faChartPie,
  faDotCircle,
  faExclamationTriangle,
  faGlobeAmericas,
  faHashtag,
  faSearch,
  faUser,
} from '@fortawesome/free-solid-svg-icons';
import {
  FontAwesomeIcon,
  FontAwesomeLayers,
  FontAwesomeLayersText,
} from '@fortawesome/vue-fontawesome';
import Toasted from 'vue-toasted';
import App from './App';
import router from './router';
import store from './store';
import Auth from './auth';

Vue.config.productionTip = false;

library.add(faAngleDown);
library.add(faAngleUp);
library.add(faArrowRight);
library.add(faCaretDown);
library.add(faCaretUp);
library.add(faCertificate);
library.add(faChartArea);
library.add(faChartBar);
library.add(faChartLine);
library.add(faChartPie);
library.add(faDotCircle);
library.add(faExclamationTriangle);
library.add(faGlobeAmericas);
library.add(faHashtag);
library.add(faSearch);
library.add(faUser);

Vue.component('font-awesome-icon', FontAwesomeIcon);
Vue.component('font-awesome-layers', FontAwesomeLayers);
Vue.component('font-awesome-layers-text', FontAwesomeLayersText);

Vue.use(Toasted, {
  router,
  position: 'bottom-right',
  iconPack: 'fontawesome',
  duration: 6000,
});

Vue.use(Auth, {
  router,
  toasted: Vue.toasted,
});

// Lets Register a Global Error Notification Toast.
Vue.toasted.register('forbidden', "You can't access this resource at this moment.", {
  type: 'error',
});

/* eslint-disable no-new */
new Vue({
  el: '#app',
  store,
  router,
  render: h => h(App),
});

// Analytics SPA route change hook (no initial ping as the gtag init step does this automatically)
router.afterEach((to) => {
  if (window.gtag) {
    window.gtag('config', 'UA-132758957-2', {
      page_title: to.name,
      page_path: to.path,
    });
  }
});
