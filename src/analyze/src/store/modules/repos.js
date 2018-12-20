import repoApi from '../../api/repo';

const state = {
  activeView: { is_markdown: false, file: '', populated: false },
  loadingValidation: false,
  loadingUpdate: false,
  models: [],
  validated: false,
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

  urlForModelExplore: () => (model, explore) => `repos/explores/${model}/${explore}`,

  hasCode() {
    return state.activeView.populated && !state.activeView.is_markdown;
  },

  hasError() {
    return state.errors.length;
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
    repoApi
      .lint()
      .then((data) => {
        commit('setValidatedState', data.data);
        state.loadingValidation = false;
      })
      .catch(() => {
        state.loadingValidation = false;
      });
  },

  sync({ commit, dispatch }) {
    state.loadingUpdate = true;
    repoApi
      .sync()
      .then((data) => {
        dispatch('getModels');
        commit('setValidatedState', data.data);
        state.loadingUpdate = false;
      })
      .catch(() => {
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
    state.errors = [];
    state.validated = true;
    // validation failed, so there will be errors
    if (!validated.result) {
      state.errors = validated.errors;
    }
  },

};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
