import projectsApi from '../../api/projects';

const state = {
  projects: [],
  project: '',
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

  projectNameChanged({ commit }, project) {
    const nonAlphaProject = project.replace(/[^0-9A-Za-z\-_]/gi, '').toLowerCase();
    projectsApi.getExists(nonAlphaProject)
      .then((data) => {
        commit('setExists', data.data);
        commit('setProjectName', nonAlphaProject);
      })
      .catch(() => {});
  },

  createProject() {
    return projectsApi.createProject(state.project);
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
