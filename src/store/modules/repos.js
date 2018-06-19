import repoApi from '../../api/repo';

const state = {
  activeView: { is_markdown: false, blob: '', populated: false },
  validated: false,
  loadingValidation: false,
  loadingUpdate: false,
  importResults: {},
  errors: [],
  blobs: {
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
        const blobs = data.data;
        commit('setRepoBlobs', { blobs });
      });
  },

  getBlob({ commit }, blob) {
    repoApi.blob(blob.hexsha)
      .then((data) => {
        commit('setCurrentBlobView', data.data);
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
};

const mutations = {
  setRepoBlobs(_, { blobs }) {
    state.blobs = blobs;
  },

  setCurrentBlobView(_, blob) {
    state.activeView = blob;
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
