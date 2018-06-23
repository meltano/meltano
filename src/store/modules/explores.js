import exploreApi from '../../api/explore';
import utils from '../../api/utils';

const state = {
  explore: {
    settings: {
      label: 'loading...',
    },
    view: {},
  },
  currentModel: '',
  currentExplore: '',
  currentQuery: '',
  selectedDimensions: {},
};

const getters = {
  currentModelLabel() {
    return utils.titleCase(state.currentModel);
  },
  currentExploreLabel() {
    return utils.titleCase(state.currentModel);
  },
};

const actions = {
  getExplore({ commit }, { model, explore }) {
    state.currentModel = model;
    state.currentExplore = explore;
    exploreApi.index(model, explore)
      .then((data) => {
        commit('setExplore', data.data);
        commit('selectedDimensions', data.data.view.dimensions);
      });
  },

  expandRow({ commit }) {
    commit('toggleCollapsed');
  },

  toggleDimension({ commit }, dimension) {
    commit('toggleDimensionSelected', dimension);
  },

  runQuery({ commit }) {
    const baseView = state.explore.view;
    const dimensions = baseView
      .dimensions
      .filter(d => d.selected)
      .map(d => d.name);
    const postData = {
      view: baseView.name,
      dimensions,
    };
    exploreApi.run(state.currentModel, state.currentExplore, postData)
      .then((data) => {
        commit('queryResults', data.data);
      });
  },
};

const mutations = {

  queryResults(_, results) {
    state.currentQuery = results.query;
  },

  toggleDimensionSelected(_, dimension) {
    const selectedDimension = dimension;
    selectedDimension.selected = !dimension.selected;
  },

  selectedDimensions(_, dimensions) {
    dimensions.forEach((dimension) => {
      state.selectedDimensions[dimension.unique_name] = false;
    });
  },

  setExplore(_, exploreData) {
    state.explore = exploreData;
  },

  toggleCollapsed() {
    state.explore.view.collapsed = !state.explore.view.collapsed;
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
