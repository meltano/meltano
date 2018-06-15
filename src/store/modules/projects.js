import projectApi from '../../api/project';

const state = {
  all: [],
};

const getters = {
  hasProjects() {
    return state.all.length;
  },
};

const actions = {
  getProjects({ commit }) {
    console.log('get projects')
    projectApi.index()
      .then((data) => {
        commit('setProjects', {
          projects: data.data,
        });
      });
  },
};

const mutations = {
  setProjects(_, { projects }) {
    state.all = projects;
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
