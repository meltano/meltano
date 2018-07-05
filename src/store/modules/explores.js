import SSF from 'ssf';
import Vue from 'vue';
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
  resultMeasures: {},
  loadingQuery: false,
  currentDataTab: 'sql',
  selectedDimensions: {},
  currentSQL: '',
  filtersOpen: false,
  dataOpen: true,
  chartsOpen: false,
  limit: 3,
  distincts: {},
};

const getters = {
  hasResults() {
    return !!state.results.length;
  },
  getDistinctsForField: () => field => state.distincts[field],
  getResultsFromDistinct: () => (field) => {
    const thisDistinct = state.distincts[field];
    if (!thisDistinct) {
      return null;
    }
    return thisDistinct.results;
  },
  getKeyFromDistinct: () => (field) => {
    const thisDistinct = state.distincts[field];
    if (!thisDistinct) {
      return null;
    }
    return thisDistinct.keys[0];
  },
  getSelectionsFromDistinct: () => (field) => {
    const thisDistinct = state.distincts[field];
    if (!thisDistinct) {
      return [];
    }
    const thisDistinctSelections = thisDistinct.selections;
    if (!thisDistinctSelections) {
      return [];
    }
    return thisDistinctSelections;
  },

  getChartYAxis() {
    const measures = Object.keys(state.resultMeasures);
    return measures;
  },

  isColumnSelectedMeasure: () => columnName => columnName in state.resultMeasures,

  getFormattedValue: () => (fmt, value) => SSF.format(fmt, Number(value)),

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

    const filters = JSON.parse(JSON.stringify(state.distincts));
    const filtersKeys = Object.keys(filters);
    filtersKeys.forEach((prop) => {
      delete filters[prop].results;
      delete filters[prop].sql;
    });

    const postData = {
      view: baseView.name,
      dimensions,
      measures,
      limit: state.limit,
      filters,
      run,
    };
    if (run) state.loadingQuery = true;
    exploreApi.getSql(state.currentModel, state.currentExplore, postData)
      .then((data) => {
        if (run) {
          commit('setQueryResults', data.data);
          state.loadingQuery = false;
        } else {
          commit('setSQLResults', data.data);
        }
      })
      .catch((e) => {
        console.log('e', e);
      });
  },

  getDistinct({ commit }, field) {
    exploreApi.getDistinct(state.currentModel, state.currentExplore, field)
      .then((data) => {
        commit('setDistincts', {
          data: data.data,
          field,
        });
      });
  },

  addDistinctSelection({ commit }, data) {
    commit('setSelectedDistincts', data);
  },

  addDistinctModifier({ commit }, data) {
    commit('setModifierDistincts', data);
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

  toggleChartsOpen({ commit }) {
    commit('setChartToggle');
  },
};

const mutations = {

  setDistincts(_, { data, field }) {
    Vue.set(state.distincts, field, data);
  },

  setSelectedDistincts(_, { item, field }) {
    if (!state.distincts[field].selections) {
      Vue.set(state.distincts[field], 'selections', []);
    }
    if (state.distincts[field].selections.indexOf(item) === -1) {
      state.distincts[field].selections.push(item);
    }
  },

  setModifierDistincts(_, { item, field }) {
    Vue.set(state.distincts[field], 'modifier', item);
  },

  setFilterToggle() {
    state.filtersOpen = !state.filtersOpen;
  },

  setDataToggle() {
    state.dataOpen = !state.dataOpen;
  },

  setChartToggle() {
    state.chartsOpen = !state.chartsOpen;
  },

  setSQLResults(_, results) {
    state.currentSQL = results.sql;
  },

  setQueryResults(_, results) {
    state.results = results.results;
    state.keys = results.keys;
    state.resultMeasures = results.measures;
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
