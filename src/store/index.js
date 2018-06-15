import Vue from 'vue';
import Vuex from 'vuex';
import projects from './modules/projects';

Vue.use(Vuex);

const debug = process.env.NODE_ENV !== 'production';

export default new Vuex.Store({
  modules: {
    projects,
  },
  string: debug,
});
