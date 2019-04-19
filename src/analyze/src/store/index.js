import Vue from 'vue';
import Vuex from 'vuex';
import repos from './modules/repos';
import designs from './modules/designs';
import dashboards from './modules/dashboards';
import settings from './modules/settings';
import orchestrations from './modules/orchestrations';

Vue.use(Vuex);

const debug = process.env.NODE_ENV !== 'production';

export default new Vuex.Store({
  modules: {
    repos,
    designs,
    dashboards,
    settings,
    orchestrations,
  },
  string: debug,
});
