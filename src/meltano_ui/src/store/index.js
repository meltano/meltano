import Vue from 'vue';
import Vuex from 'vuex';
import projects from './modules/projects';
import repos from './modules/repos';
import explores from './modules/explores';
import settings from './modules/settings';
import orchestrations from './modules/orchestrations';

Vue.use(Vuex);

const debug = process.env.NODE_ENV !== 'production';

export default new Vuex.Store({
  modules: {
    projects,
    repos,
    explores,
    settings,
    orchestrations,
  },
  string: debug,
});
