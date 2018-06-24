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
  results: [],
  keys: [],
  loadingQuery: false,
  currentDataTab: 'sql',
  selectedDimensions: {},
  currentSQL: '',
  filtersOpen: false,
  dataOpen: true,
  limit: 3,
};

const getters = {
  currentModelLabel() {
    return utils.titleCase(state.currentModel);
  },
  currentExploreLabel() {
    return utils.titleCase(state.currentModel);
  },

  isDataTab() {
    return state.currentDataTab === 'data';
  },

  isResultsTab() {
    return state.currentDataTab === 'results';
  },

  isSQLTab() {
    return state.currentDataTab === 'sql';
  },

  currentLimit() {
    return state.limit;
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

  toggleMeasure({ commit }, measure) {
    commit('toggleMeasureSelected', measure);
  },

  limitSet({ commit }, limit) {
    commit('setLimit', limit);
  },

  getSQL({ commit }, { run }) {
    const baseView = state.explore.view;
    const dimensions = baseView
      .dimensions
      .filter(d => d.selected)
      .map(d => d.name);
    const measures = baseView
      .measures
      .filter(m => m.selected)
      .map(m => m.name);

    const postData = {
      view: baseView.name,
      dimensions,
      measures,
      limit: state.limit,
      run,
    };
    if (run) state.loadingQuery = true;
    exploreApi.get_sql(state.currentModel, state.currentExplore, postData)
      .then((data) => {
        if (run) {
          commit('setQueryResults', data.data);
          state.loadingQuery = false;
        } else {
          commit('setSQLResults', data.data);
        }
      });
  },

  switchCurrentTab({ commit }, tab) {
    commit('setCurrentTab', tab);
  },

  toggleFilterOpen({ commit }) {
    commit('setFilterToggle');
  },

  toggleDataOpen({ commit }) {
    commit('setDataToggle');
  },
};

const mutations = {

  setFilterToggle() {
    state.filtersOpen = !state.filtersOpen;
  },

  setDataToggle() {
    state.dataOpen = !state.dataOpen;
  },

  setSQLResults(_, results) {
    state.currentSQL = results.sql;
  },

  setQueryResults(_, results) {
    state.results = results.results;
    state.keys = results.keys;
  },

  toggleDimensionSelected(_, dimension) {
    const selectedDimension = dimension;
    selectedDimension.selected = !dimension.selected;
  },

  toggleMeasureSelected(_, measure) {
    const selectedMeasure = measure;
    selectedMeasure.selected = !measure.selected;
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

  setCurrentTab(_, tab) {
    state.currentDataTab = tab;
  },

  setLimit(_, limit) {
    state.limit = limit;
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
