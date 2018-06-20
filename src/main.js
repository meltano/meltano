import Vue from 'vue';
import App from './App';
import router from './router';
import store from './store';

Vue.config.productionTip = false;

/* eslint-disable no-new */
new Vue({
  el: '#app',
  store,
  router,
  render: h => h(App),
});

Vue.filter('capitalize', (value) => {
  if (!value) return '';
  let newVal = value;
  newVal = newVal.toString();
  return newVal.charAt(0).toUpperCase() + newVal.slice(1);
});

Vue.filter('titleCase', value => value
  .replace(
    /\w\S*/g, txt => txt
      .charAt(0)
      .toUpperCase() + txt.substr(1)
      .toLowerCase()));

Vue.filter('camelToRegular', value => value.replace(/([A-Z])/g, ' $1'));
Vue.filter('underscoreToSpace', value => value.replace(/_/g, ' '));
