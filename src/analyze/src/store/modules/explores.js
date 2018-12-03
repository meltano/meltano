import SSF from 'ssf';
import Vue from 'vue';
import sqlFormatter from 'sql-formatter';
import exploreApi from '../../api/explore';
import utils from '../../api/utils';

const state = {
  explore: {
    settings: {
      label: 'loading...',
    },
    view: {},
  },
  hasSQLError: false,
  sqlErrorMessage: [],
  currentModel: '',
  currentExplore: '',
  results: [],
  keys: [],
  columnHeaders: [],
  names: [],
  exploreJoins: {
    dimensions: [],
    dimension_groups: [],
    measures: [],
  },
  resultMeasures: {},
  loadingQuery: false,
  currentDataTab: 'sql',
  selectedDimensions: {},
  currentSQL: '',
  filtersOpen: false,
  dataOpen: true,
  chartsOpen: false,
  chartType: 'BarChart',
  limit: 3,
  distincts: {},
  sortColumn: null,
  sortDesc: false,
};

const getters = {
  hasResults() {
    if (!state.results) return false;
    return !!state.results.length;
  },

  numResults() {
    if (!state.results) return 0;
    return state.results.length;
  },

  getDistinctsForField: () => field => state.distincts[field],

  getResultsFromDistinct: () => (field) => {
    const thisDistinct = state.distincts[field];
    if (!thisDistinct) {
      return null;
    }
    return thisDistinct.results;
  },

  hasJoins() {
    return !!(state.explore.joins && state.explore.joins.length);
  },

  isColumnSorted: () => key => state.sortColumn === key,

  showJoinDimensionMeasureHeader: () => arr => !!(arr && arr.length),

  joinIsExpanded: () => join => join.expanded,
  getLabelForJoin: () => join => ('view_label' in join.settings ? join.settings.view_label : join.name),
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
    if (!state.resultMeasures) return [];
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

  formattedSql() {
    return sqlFormatter.format(state.currentSQL);
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

  expandJoinRow({ commit }, join) {
    // already fetched dimensions
    commit('toggleJoinOpen', join);
    if (join.dimensions.length) return;
    exploreApi.getView(join.name)
      .then((data) => {
        commit('setJoinDimensions', {
          dimensions: data.data.dimensions,
        });
        commit('setJoinDimensionGroups', {
          dimensionGroups: data.data.dimension_groups,
        });
        commit('setJoinMeasures', {
          measures: data.data.measures,
        });
      });
  },

  removeSort({ commit }, dimension) {
    if (!state.sortColumn || state.sortColumn !== dimension.name) return;
    commit('setRemoveSort', dimension);
  },

  toggleDimension({ commit }, dimension) {
    commit('toggleDimensionSelected', dimension);
  },

  toggleDimensionGroup({ commit }, dimensionGroup) {
    commit('toggleDimensionGroupSelected', dimensionGroup);
  },

  toggleDimensionGroupTimeframe({ commit }, dimensionGroupObj) {
    commit('toggleDimensionGroupTimeframeSelected', dimensionGroupObj);
  },

  toggleMeasure({ commit }, measure) {
    commit('toggleMeasureSelected', measure);
  },

  limitSet({ commit }, limit) {
    commit('setLimit', limit);
  },

  setChartType({ commit }, chartType) {
    commit('setChartType', chartType);
  },

  getSQL({ commit }, { run }) {
    this.dispatch('explores/resetErrorMessage');
    const baseView = state.explore.view;
    const dimensions = baseView
      .dimensions
      .filter(d => d.selected)
      .map(d => d.name);
    let sortColumn = baseView
      .dimensions
      .find(d => d.name === state.sortColumn);
    if (!sortColumn) {
      sortColumn = baseView
        .measures
        .find(d => d.name === state.sortColumn);
    }
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

    const joins = state.explore
      .joins
      .map((j) => {
        const newJoin = {};
        newJoin.name = j.name;
        if (j.dimensions) {
          newJoin.dimensions = j.dimensions
            .filter(d => d.selected)
            .map(d => d.name);
          if (!newJoin.dimensions.length) delete newJoin.dimensions;
        }
        if (j.measures) {
          newJoin.measures = j.measures
            .filter(m => m.selected)
            .map(m => m.name);
          if (!newJoin.measures.length) delete newJoin.measures;
        }
        return newJoin;
      })
      .filter(j => !!(j.dimensions || j.measures));

    let order = null;
    const dimensionGroups = baseView
      .dimension_groups
      .map(dg => ({
        name: dg.name,
        timeframes: dg.timeframes
          .filter(tf => tf.selected)
          .map(tf => tf.name),
      }))
      .filter(dg => dg.timeframes.length);

    if (sortColumn) {
      order = {
        column: sortColumn.name,
        direction: state.sortDesc ? 'desc' : 'asc',
      };
    }

    const postData = {
      view: baseView.name,
      dimensions,
      dimension_groups: dimensionGroups,
      measures,
      joins,
      order,
      limit: state.limit,
      filters,
      run,
    };
    if (run) state.loadingQuery = true;
    exploreApi.getSql(state.currentModel, state.currentExplore, postData)
      .then((data) => {
        if (run) {
          commit('setQueryResults', data.data);
          commit('setSQLResults', data.data);
          state.loadingQuery = false;
        } else {
          commit('setSQLResults', data.data);
        }
      })
      .catch((e) => {
        commit('setSqlErrorMessage', e);
        state.loadingQuery = false;
      });
  },

  resetErrorMessage({ commit }) {
    commit('setErrorState');
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

  sortBy({ commit }, name) {
    commit('setSortColumn', name);
    this.dispatch('explores/getSQL', {
      run: true,
    });
  },
};

const mutations = {

  setRemoveSort() {
    state.sortColumn = null;
  },

  setChartType(context, chartType) {
    state.chartType = chartType;
  },

  setSortColumn(context, name) {
    if (state.sortColumn === name) {
      state.sortDesc = !state.sortDesc;
    }
    state.sortColumn = name;
  },

  setDistincts(_, { data, field }) {
    Vue.set(state.distincts, field, data);
  },

  setJoinDimensions(_, { dimensions }) {
    state.exploreJoins.dimensions = dimensions;
  },

  setJoinDimensionGroups(_, { dimensionGroups }) {
    state.exploreJoins.dimension_groups = dimensionGroups;
  },

  setJoinMeasures(_, { measures }) {
    state.exploreJoins.measures = measures;
  },

  toggleJoinOpen(_, join) {
    const thisJoin = join;
    thisJoin.collapsed = !thisJoin.collapsed;
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
    state.columnHeaders = results.column_headers;
    state.names = results.names;
    state.resultMeasures = results.measures;
  },

  setSqlErrorMessage(_, e) {
    state.hasSQLError = true;
    if (!e.response) {
      state.sqlErrorMessage = ['Something went wrong on our end. We\'ll check our error logs and get back to you.'];
      return;
    }
    const error = e.response.data;
    state.sqlErrorMessage = [error.code, error.orig, error.statement];
  },

  setErrorState() {
    state.hasSQLError = false;
    state.sqlErrorMessage = [];
  },

  toggleDimensionSelected(_, dimension) {
    const selectedDimension = dimension;
    selectedDimension.selected = !dimension.selected;
  },

  toggleDimensionGroupSelected(_, dimensionGroup) {
    const selectedDimensionGroup = dimensionGroup;
    selectedDimensionGroup.selected = !selectedDimensionGroup.selected;
  },

  toggleDimensionGroupTimeframeSelected(_, { timeframe }) {
    const selectedTimeframe = timeframe;
    selectedTimeframe.selected = !selectedTimeframe.selected;
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
