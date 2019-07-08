import SSF from 'ssf';
import Vue from 'vue';
import sqlFormatter from 'sql-formatter';
import utils from '@/utils/utils';
import designApi from '../../api/design';
import reportsApi from '../../api/reports';
import sqlApi from '../../api/sql';

const state = {
  activeReport: {},
  design: {
    related_table: {},
  },
  hasSQLError: false,
  sqlErrorMessage: [],
  currentModel: '',
  currentDesign: '',
  results: [],
  keys: [],
  columnHeaders: [],
  columnNames: [],
  resultAggregates: {},
  loadingQuery: false,
  currentSQL: '',
  saveReportSettings: { name: null },
  reports: [],
  chartType: 'BarChart',
  limit: 50,
  distincts: {},
  sortColumn: null,
  sortDesc: false,
  dialect: null,
  filterOptions: null,
  filters: {
    columns: [],
    aggregates: [],
  },
};

const helpers = {
  getQueryPayloadFromDesign() {
    const selected = x => x.selected;
    const namesOfSelected = (arr) => {
      if (!Array.isArray(arr)) {
        return null;
      }

      return arr.filter(selected).map(x => x.name);
    };

    const baseTable = state.design.related_table;
    const columns = namesOfSelected(baseTable.columns);
    const aggregates = namesOfSelected(baseTable.aggregates) || [];

    let sortColumn = baseTable.columns.find(d => d.name === state.sortColumn);
    if (!sortColumn) {
      sortColumn = baseTable.aggregates.find(d => d.name === state.sortColumn);
    }
    let order = null;
    if (sortColumn && sortColumn.selected) {
      order = {
        column: sortColumn.name,
        direction: state.sortDesc ? 'desc' : 'asc',
      };
    }

    const filters = JSON.parse(JSON.stringify(state.distincts));
    const filtersKeys = Object.keys(filters);
    filtersKeys.forEach((prop) => {
      delete filters[prop].results;
      delete filters[prop].sql;
    });

    if (!state.design.joins) {
      state.design.joins = [];
    }
    const joins = state.design.joins
      .map((j) => {
        const table = j.related_table;
        const newJoin = {};

        newJoin.name = j.name;
        newJoin.columns = namesOfSelected(table.columns) || [];
        newJoin.aggregates = namesOfSelected(table.aggregates) || [];

        if (table.timeframes) {
          newJoin.timeframes = table.timeframes
            .filter(selected)
            .map(({ name, periods }) => ({
              name,
              periods: periods.filter(selected),
            }));
        }

        return newJoin;
      })
      .filter(j => !!(j.columns || j.aggregates));

    // TODO update default empty array likely
    // in the ma_file_parser to set proper defaults
    // if user's exclude certain properties in their models
    const timeframes = baseTable.timeframes || []
      .map(tf => ({
        name: tf.name,
        periods: tf.periods.filter(selected),
      }))
      .filter(tf => tf.periods.length);

    return {
      table: baseTable.name,
      columns,
      aggregates,
      timeframes,
      joins,
      order,
      limit: state.limit,
      filters,
      dialect: state.dialect,
    };
  },
};

const getters = {
  filtersCount() {
    return state.filters.columns.length + state.filters.aggregates.length;
  },

  hasResults() {
    if (!state.results) {
      return false;
    }
    return !!state.results.length;
  },

  hasChartableResults() {
    return getters.hasResults() && state.resultAggregates.length;
  },

  hasFilters() {
    return getters.filtersCount() > 0;
  },

  resultsCount() {
    if (!state.results) {
      return 0;
    }
    return state.results.length;
  },

  getDialect: () => state.dialect,

  getDistinctsForField: () => field => state.distincts[field],

  getResultsFromDistinct: () => (field) => {
    const thisDistinct = state.distincts[field];
    if (!thisDistinct) {
      return null;
    }
    return thisDistinct.results;
  },

  hasJoins() {
    return !!(state.design.joins && state.design.joins.length);
  },

  isColumnSorted: () => key => state.sortColumn === key,

  showJoinColumnAggregateHeader: () => obj => !!obj,

  joinIsExpanded: () => join => join.expanded,

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
    if (!state.resultAggregates) {
      return [];
    }
    const aggregates = Object.keys(state.resultAggregates);
    return aggregates;
  },

  isColumnSelectedAggregate: () => columnName => columnName in state.resultAggregates,

  getFormattedValue: () => (fmt, value) => SSF.format(fmt, Number(value)),

  currentModelLabel() {
    return utils.titleCase(state.currentModel);
  },

  currentDesignLabel() {
    return utils.titleCase(state.currentModel);
  },

  currentLimit() {
    return state.limit;
  },

  formattedSql() {
    return sqlFormatter.format(state.currentSQL);
  },
};

const actions = {
  getDesign({ dispatch, commit }, { model, design, slug }) {
    state.currentSQL = '';
    state.currentModel = model;
    state.currentDesign = design;

    // TODO: chain callbacks to keep a single Promise
    const index = designApi.index(model, design)
      .then((response) => {
        commit('setDesign', response.data);
      });

    reportsApi.loadReports()
      .then((response) => {
        state.reports = response.data;
        if (slug) {
          const reportMatch = state.reports.find(report => report.slug === slug);
          if (reportMatch) {
            dispatch('loadReport', reportMatch);
          }
        }
      })
      .catch((e) => {
        commit('setSqlErrorMessage', e);
        state.loadingQuery = false;
      });

    return index;
  },

  getFilterOptions({ commit }) {
    sqlApi.getFilterOptions()
      .then((response) => {
        commit('setFilterOptions', response.data);
      });
  },

  expandRow({ commit }, row) {
    commit('toggleCollapsed', row);
  },

  expandJoinRow({ commit }, join) {
    // already fetched columns
    commit('toggleCollapsed', join);
    if (join.related_table.columns.length) {
      return;
    }
    designApi.getTable(join.related_table.name)
      .then((response) => {
        commit('setJoinColumns', {
          columns: response.data.columns,
          join,
        });
        commit('setJoinTimeframes', {
          timeframes: response.data.timeframes,
          join,
        });
        commit('setJoinAggregates', {
          aggregates: response.data.aggregates,
          join,
        });
      });
  },

  removeSort({ commit }, column) {
    if (!state.sortColumn || state.sortColumn !== column.name) {
      return;
    }
    commit('setRemoveSort', column);
  },

  toggleColumn({ commit }, column) {
    commit('toggleSelected', column);
  },

  toggleTimeframe({ commit }, timeframe) {
    commit('toggleSelected', timeframe);
  },

  toggleTimeframePeriod({ commit }, timeframePeriod) {
    commit('toggleSelected', timeframePeriod);
  },

  toggleAggregate({ commit }, aggregate) {
    commit('toggleSelected', aggregate);
  },

  limitSet({ commit }, limit) {
    commit('setLimit', limit);
  },

  // TODO: remove and use `mapMutations`
  setChartType({ commit }, chartType) {
    commit('setChartType', chartType);
  },

  getSQL({ commit }, { run, load }) {
    this.dispatch('designs/resetErrorMessage');
    state.loadingQuery = !!run;

    const queryPayload = Object.assign({}, helpers.getQueryPayloadFromDesign(), load);
    const postData = Object.assign({ run }, queryPayload);
    sqlApi
      .getSql(state.currentModel, state.currentDesign, postData)
      .then((response) => {
        if (run) {
          commit('setQueryResults', response.data);
          commit('setSQLResults', response.data);
          state.loadingQuery = false;
        } else {
          commit('setSQLResults', response.data);
        }
      })
      .catch((e) => {
        commit('setSqlErrorMessage', e);
        state.loadingQuery = false;
      });
  },

  loadReport({ commit }, { name }) {
    reportsApi.loadReport(name)
      .then((response) => {
        const report = response.data;
        this.dispatch('designs/getSQL', {
          run: true,
          load: report.queryPayload,
        });
        commit('setCurrentReport', report);
        commit('setStateFromLoadedReport', report);
      })
      .catch((e) => {
        commit('setSqlErrorMessage', e);
        state.loadingQuery = false;
      });
  },

  saveReport({ commit }, { name }) {
    const postData = {
      name,
      model: state.currentModel,
      design: state.currentDesign,
      chartType: state.chartType,
      queryPayload: helpers.getQueryPayloadFromDesign(),
    };
    reportsApi.saveReport(postData)
      .then((response) => {
        commit('resetSaveReportSettings');
        commit('setCurrentReport', response.data);
        commit('addSavedReportToReports', response.data);
      })
      .catch((e) => {
        commit('setSqlErrorMessage', e);
        state.loadingQuery = false;
      });
  },

  updateReport({ commit }) {
    state.activeReport.queryPayload = helpers.getQueryPayloadFromDesign();
    state.activeReport.chartType = state.chartType;
    reportsApi.updateReport(state.activeReport)
      .then((response) => {
        commit('resetSaveReportSettings');
        commit('setCurrentReport', response.data);
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
    sqlApi
      .getDistinct(state.currentModel, state.currentDesign, field)
      .then((response) => {
        commit('setDistincts', {
          data: response.data,
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

  toggleLoadReportOpen({ commit }) {
    commit('setLoadReportToggle');
  },

  sortBy({ commit }, name) {
    commit('setSortColumn', name);
    this.dispatch('designs/getSQL', {
      run: true,
    });
  },

  toggleFilter({ commit }, { attribute, filterType }) {
    const filter = {
      tableName: 'TABLE_NAME',
      attributeName: attribute.name,
      operation: '',
      value: '',
      nullState: '',
    };
    commit('addFilter', { filter, filterType });
  },

  removeFilter() {
    return true;
  },
};

const mutations = {
  setRemoveSort() {
    state.sortColumn = null;
  },

  setChartType(context, chartType) {
    state.chartType = chartType;
  },

  setCurrentReport(_, report) {
    state.activeReport = report;
  },

  setFilterOptions(_, options) {
    state.filterOptions = options;
  },

  setStateFromLoadedReport(_, report) {
    // General UI state updates
    state.currentModel = report.model;
    state.currentDesign = report.design;
    state.chartType = report.chartType;
    state.limit = report.queryPayload.limit;
    state.dialect = report.queryPayload.dialect;

    // UI selected state adornment helpers for columns, aggregates, filters, joins, & timeframes
    const baseTable = state.design.related_table;
    const queryPayload = report.queryPayload;
    const joinColumnGroups = state.design.joins.reduce((acc, curr) => {
      acc.push({
        name: curr.name,
        columns: curr.related_table.columns,
        aggregates: curr.related_table.aggregates,
        timeframes: curr.related_table.timeframes,
      });
      return acc;
    }, []);
    const nameMatcher = (source, target) => source.name === target.name;
    const nameMapper = item => item.name;
    const setSelected = (sourceCollection, targetCollection) => {
      sourceCollection.forEach((item) => {
        item.selected = targetCollection.includes(item.name);
      });
    };

    // columns
    setSelected(baseTable.columns, queryPayload.columns);
    // aggregates
    setSelected(baseTable.aggregates, queryPayload.aggregates);
    // filters
    // TODO
    // joins, timeframes, and periods
    joinColumnGroups.forEach((joinGroup) => {
      // joins - columns
      const targetJoin = queryPayload.joins.find(j => nameMatcher(j, joinGroup));
      setSelected(joinGroup.columns, targetJoin.columns);
      // joins - aggregates
      if (joinGroup.aggregates) {
        setSelected(joinGroup.aggregates, targetJoin.aggregates);
      }
      // timeframes
      if (targetJoin && targetJoin.timeframes) {
        setSelected(joinGroup.timeframes, targetJoin.timeframes.map(nameMapper));
        // periods
        joinGroup.timeframes.forEach((timeframe) => {
          const targetTimeframe = targetJoin.timeframes.find(tf => nameMatcher(tf, timeframe));
          if (targetTimeframe && targetTimeframe.periods) {
            setSelected(timeframe.periods, targetTimeframe.periods.map(nameMapper));
          }
        });
      }
    });
    // order
    // TODO
    // base_table timeframes
    // TODO
  },

  addFilter(_, { filter, filterType }) {
    state.filters[`${filterType}s`].push(filter);
  },

  addSavedReportToReports(_, report) {
    state.reports.push(report);
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

  setJoinColumns(_, { columns, join }) {
    join.columns = columns;
  },

  setJoinTimeframes(_, { timeframes, join }) {
    join.timeframes = timeframes;
  },

  setJoinAggregates(_, { aggregates, join }) {
    join.aggregates = aggregates;
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

  resetSaveReportSettings() {
    state.saveReportSettings = { name: null };
  },

  setSQLResults(_, results) {
    state.currentSQL = results.sql;
  },

  setQueryResults(_, results) {
    state.results = results.results;
    state.keys = results.keys;
    state.columnHeaders = results.column_headers;
    state.columnNames = results.column_names;
    state.resultAggregates = results.aggregates;
  },

  setSqlErrorMessage(_, e) {
    state.hasSQLError = true;
    if (!e.response) {
      state.sqlErrorMessage = [
        "Something went wrong on our end. We'll check our error logs and get back to you.",
      ];
      return;
    }
    const error = e.response.data;
    state.sqlErrorMessage = [error.code, error.orig, error.statement];
  },

  setErrorState() {
    state.hasSQLError = false;
    state.sqlErrorMessage = [];
  },

  toggleSelected(_, selectable) {
    Vue.set(selectable, 'selected', !selectable.selected);
  },

  toggleCollapsed(_, collapsable) {
    Vue.set(collapsable, 'collapsed', !collapsable.collapsed);
  },

  setDesign(_, designData) {
    state.design = designData;
  },

  setLimit(_, limit) {
    state.limit = limit;
  },

  setDialect(_, dialect) {
    state.dialect = dialect;
  },
};

export default {
  namespaced: true,
  helpers,
  state,
  getters,
  actions,
  mutations,
};
