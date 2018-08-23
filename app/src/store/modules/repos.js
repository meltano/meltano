import repoApi from '../../api/repo';

const state = {
  activeView: { is_markdown: false, file: '', populated: false },
  validated: false,
  loadingValidation: false,
  loadingUpdate: false,
  importResults: {},
  models: [],
  navbarClicked: false,
  errors: [],
  files: {
    dashboards:
    [{
      abs: 'loading',
      path: 'loading',
      visual: 'loading',
    }],
  },
};

const getters = {

  hasMarkdown() {
    return state.activeView.populated && state.activeView.is_markdown;
  },

  hasCode() {
    return state.activeView.populated && !state.activeView.is_markdown;
  },

  hasError() {
    return state.validated && state.errors.length;
  },

  passedValidation() {
    return state.validated && !state.errors.length;
  },
};

const actions = {
  getRepo({ commit }) {
    repoApi.index()
      .then((data) => {
        const files = data.data;
        commit('setRepoFiles', { files });
      });
  },


  getFile({ commit }, file) {
    repoApi.file(file.unique)
      .then((data) => {
        commit('setCurrentFileView', data.data);
      });
  },

  lint({ commit }) {
    state.loadingValidation = true;
    repoApi.lint()
      .then((data) => {
        commit('setValidatedState', data.data);
        state.loadingValidation = false;
      });
  },

  update({ commit }) {
    state.loadingUpdate = true;
    repoApi.update()
      .then((data) => {
        commit('setUpdateResults', data.data);
        state.loadingUpdate = false;
      });
  },

  getModels({ commit }) {
    repoApi.models()
      .then((data) => {
        commit('setModels', data.data);
      });
  },

  navbarHideDropdown({ commit }) {
    commit('setHiddenDropdown');
  },
};

const mutations = {
  setHiddenDropdown() {
    state.navbarClicked = true;
    setTimeout(() => {
      state.navbarClicked = false;
    }, 500);
  },

  setModels(_, models) {
    state.models = models;
  },

  setRepoFiles(_, { files }) {
    state.files = files;
  },

  setCurrentFileView(_, file) {
    state.activeView = file;
  },

  setValidatedState(_, validated) {
    state.validated = true;
    state.errors = [];
    // validation failed, so there will be errors
    if (!validated.result) {
      state.errors = validated.errors;
    }
  },

  setUpdateResults(_, results) {
    state.setImportResults = results;
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
