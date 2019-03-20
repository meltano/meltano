import startApi from '../../api/start';

const state = {
  project: '',
  cwdLoaded: false,
  existingPath: '',
  cwd: 'loading...',
  exists: false,
  creatingProject: false,
};

const getters = {};

const actions = {
  getCwd({ commit }) {
    startApi.getCwd()
      .then((data) => {
        commit('setCwd', data.data.cwd);
      })
      .catch(() => {});
  },

  projectNameChanged({ commit }, project) {
    const nonAlphaProject = project.replace(/[^0-9A-Za-z\-_]/gi, '').toLowerCase();
    startApi.getExists(nonAlphaProject)
      .then((data) => {
        commit('setExists', data.data);
        commit('setProjectName', nonAlphaProject);
      })
      .catch(() => {});
  },

  createProject() {
    return startApi.createProject(state.project);
  },
};

const mutations = {
  setCwd(_, cwd) {
    state.cwd = cwd;
    state.cwdLoaded = true;
  },

  setExists(_, existsData) {
    state.exists = existsData.exists;
    state.existingPath = existsData.path;
  },

  setProjectName(_, project) {
    // hack because the state will appear unchanged
    // because of the replacing of letters and Vue only detects changes.
    state.project = 'loading...';
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
