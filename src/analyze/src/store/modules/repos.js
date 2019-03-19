import repoApi from '../../api/repo';

const state = {
  activeView: { is_markdown: false, file: '', populated: false },
  loadingValidation: false,
  loadingUpdate: false,
  models: [],
  validated: false,
  navbarClicked: false,
  errors: [],
  files: {},
};

const getters = {

  hasMarkdown() {
    return state.activeView.populated && state.activeView.is_markdown;
  },

  urlForModelDesign: () => (model, design) => `/analyze/${model}/${design}`,

  hasCode() {
    return state.activeView.populated && !state.activeView.is_markdown;
  },

  hasError() {
    return state.errors && state.errors.length;
  },

  hasFiles() {
    return Object.hasOwnProperty.call(state.files, 'topics') && state.files.topics.items;
  },

  passedValidation() {
    return state.validated && state.errors && !state.errors.length;
  },

};

const actions = {
  getRepo({ commit }) {
    repoApi.index()
      .then((response) => {
        const files = response.data;
        commit('setValidatedState', response.data);
        state.loadingValidation = false;
        commit('setRepoFiles', { files });
      });
  },

  getFile({ commit }, file) {
    repoApi.file(file.id)
      .then((response) => {
        commit('setCurrentFileTable', response.data);
      });
  },

  lint({ commit }) {
    state.loadingValidation = true;
    repoApi
      .lint()
      .then((response) => {
        commit('setValidatedState', response.data);
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
      .then((response) => {
        dispatch('getModels');
        commit('setValidatedState', response.data);
        state.loadingUpdate = false;
      })
      .catch(() => {
        state.loadingUpdate = false;
      });
  },

  getModels({ commit }) {
    repoApi.models()
      .then((response) => {
        commit('setModels', response.data);
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

  setCurrentFileTable(_, file) {
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
