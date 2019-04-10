import projectsApi from '../../api/projects';

const state = {
  projects: [],
  createProjectName: '',
  cwdLoaded: false,
  existingPath: '',
  cwd: 'loading...',
  exists: false,
  creatingProject: false,
};

const getters = {
  hasProjects() {
    return state.projects.length;
  },
};

const actions = {
  getProjects({ commit }) {
    projectsApi.getProjects()
      .then((data) => {
        commit('setProjects', data.data);
      })
      .catch(() => {});
  },

  getProject(_, router) {
    projectsApi.hasProject()
      .then((data) => {
        if (!data.data.has_project) {
          router.push({ path: '/projects' });
        }
      })
      .catch(() => {});
  },

  getCwd({ commit }) {
    projectsApi.getCwd()
      .then((data) => {
        commit('setCwd', data.data.cwd);
      })
      .catch(() => {});
  },

  projectNameChanged({ commit }, projectInput) {
    const nonAlphaProjectName = projectInput.replace(/[^0-9A-Za-z\-_]/gi, '').toLowerCase();
    projectsApi.getExists(nonAlphaProjectName)
      .then((data) => {
        commit('setExists', data.data);
        commit('setProjectName', nonAlphaProjectName);
      })
      .catch(() => {});
  },

  createProject({ commit }) {
    const projectName = state.createProjectName;
    commit('setProjectName', '');
    return projectsApi.createProject(projectName);
  },
};

const mutations = {
  setProjects(_, projects) {
    state.projects = projects;
  },

  setCwd(_, cwd) {
    state.cwd = cwd;
    state.cwdLoaded = true;
  },

  setExists(_, existsData) {
    state.exists = existsData.exists;
    state.existingPath = existsData.path;
  },

  setProjectName(_, nonAlphaProjectName) {
    // hack because the state will appear unchanged
    // because of the replacing of letters and Vue only detects changes.
    state.createProjectName = 'loading...';
    state.createProjectName = nonAlphaProjectName;
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
