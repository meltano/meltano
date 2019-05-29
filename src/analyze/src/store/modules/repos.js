import _ from 'lodash';
import repoApi from '../../api/repo';

const initialState = {
  activeView: {
    is_markdown: false,
    file: '',
    populated: false,
  },
  loadingValidation: false,
  loadingUpdate: false,
  models: {},
  validated: false,
  errors: [],
  files: {},
};

const getters = {
  hasMarkdown(state) {
    return state.activeView.populated && state.activeView.is_markdown;
  },

  urlForModelDesign: () => (model, design) => `/analyze/${model}/${design}`,

  hasCode(state) {
    return state.activeView.populated && !state.activeView.is_markdown;
  },

  hasError(state) {
    return state.errors && state.errors.length;
  },

  hasFiles(state) {
    return Object.hasOwnProperty.call(state.files, 'topics') && state.files.topics.items;
  },

  hasModels(state) {
    return !_.isEmpty(state.models);
  },

  passedValidation(state) {
    return state.validated && state.errors && !state.errors.length;
  },
};

const actions = {
  getRepo({ state, commit }) {
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

  lint({ state, commit }) {
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

  sync({ state, commit, dispatch }) {
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
};

const mutations = {
  setModels(state, models) {
    state.models = models;
  },

  setRepoFiles(state, { files }) {
    state.files = files;
  },

  setCurrentFileTable(state, file) {
    state.activeView = file;
  },

  setValidatedState(state, validated) {
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
  state: initialState,
  getters,
  actions,
  mutations,
};
