import Vue from 'vue';
import Vuex from 'vuex';
import projects from './modules/projects';
import repos from './modules/repos';

Vue.use(Vuex);

const debug = process.env.NODE_ENV !== 'production';

export default new Vuex.Store({
  modules: {
    projects,
    repos,
  },
  string: debug,
});
