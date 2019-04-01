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

console.log(router);

// Analytics SPA route change hook (no initial ping as the gtag init step does this automatically)
router.afterEach((to) => {
  if (window.gtag) {
    window.gtag('config', 'UA-132758957-2', {
      page_title: to.name,
      page_path: to.path,
    });
  }
});
