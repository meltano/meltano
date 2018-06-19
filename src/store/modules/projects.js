import router from '../../router';
import projectApi from '../../api/project';

const state = {
  project: { name: '', git_url: '' },
};

const getters = {
  hasProjects() {
    return state.project.name !== '';
  },
};

const actions = {
  getProjects(context) {
    projectApi.index()
      .then((data) => {
        context.commit('setProjects', {
          project: data.data,
        });
        if (context.state.project.git_url) {
          this.dispatch('repos/getRepo');
        }
      });
  },
  saveProject(context, payload) {
    projectApi.add(payload)
      .then((data) => {
        context.commit('addProject', {
          project: data.data,
        });
        router.push('/project');
      });
  },
};

const mutations = {
  setProjects(_, { project }) {
    state.project = project;
  },
  addProject(_, { project }) {
    state.project = project;
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
