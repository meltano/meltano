import Vue from 'vue';
import Vuex from 'vuex';
import repos from './modules/repos';
import designs from './modules/designs';
import settings from './modules/settings';
import orchestrations from './modules/orchestrations';

Vue.use(Vuex);

const debug = process.env.NODE_ENV !== 'production';

export default new Vuex.Store({
  modules: {
    repos,
    designs,
    settings,
    orchestrations,
  },
  string: debug,
});
