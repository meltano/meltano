import Vue from 'vue';
import {
  FontAwesomeIcon,
  FontAwesomeLayers,
  FontAwesomeLayersText,
} from '@fortawesome/vue-fontawesome';

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

Vue.config.productionTip = false;
