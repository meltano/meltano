import SSF from 'ssf';
import Vue from 'vue';
import sqlFormatter from 'sql-formatter';
import lodash from 'lodash';

import utils from '@/utils/utils';
import designApi from '../../api/design';
import reportsApi from '../../api/reports';
import sqlApi from '../../api/sql';

const defaultState = utils.deepFreeze({
  activeReport: {},
  design: {
    relatedTable: {},
  },
  hasSQLError: false,
  sqlErrorMessage: [],
  currentModel: '',
  currentDesign: '',
  results: [],
  keys: [],
  queryAttributes: [],
  resultAggregates: {},
  loadingQuery: false,
  currentSQL: '',
  saveReportSettings: { name: null },
  reports: [],
  chartType: 'BarChart',
  limit: 50,
  dialect: null,
  filterOptions: [],
  filters: {
    columns: [],
    aggregates: [],
  },
  order: {
    assigned: [],
    unassigned: [],
  },
});

const helpers = {
  getFilterTypePlural(filterType) {
    return `${filterType}s`;
  },
  getQueryPayloadFromDesign(state) {
    // Inline fn helpers
    const selected = x => x.selected;
    const namesOfSelected = (arr) => {
      if (!Array.isArray(arr)) {
        return null;
      }
      return arr.filter(selected).map(x => x.name);
    };

    const baseTable = state.design.relatedTable;
    const columns = namesOfSelected(baseTable.columns);
    const aggregates = namesOfSelected(baseTable.aggregates) || [];

    // Join table(s) setup
    if (!state.design.joins) {
      state.design.joins = [];
    }
    const joins = state.design.joins
      .map((j) => {
        const table = j.relatedTable;
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

    // Ordering setup
    const order = state.order.assigned;

    // Filtering setup - Enforce number type for aggregates as v-model approach overwrites as string
    const filters = lodash.cloneDeep(state.filters);
    if (filters && filters.aggregates) {
      filters.aggregates = filters.aggregates
        .filter(aggregate => aggregate.isActive)
        .map((aggregate) => {
          aggregate.value = Number(aggregate.value);
          return aggregate;
        });
    }

    return {
      name: state.design.name,
      columns,
      aggregates,
      timeframes,
      joins,
      order,
      limit: state.limit,
      dialect: state.dialect,
      filters,
    };
  },
};

const getters = {
  filtersCount(state) {
    return state.filters.columns.length + state.filters.aggregates.length;
  },

  hasResults(state) {
    if (!state.results) {
      return false;
    }
    return !!state.results.length;
  },

  // eslint-disable-next-line
  hasChartableResults(state, getters) {
    return getters.hasResults && state.resultAggregates.length;
  },

  // eslint-disable-next-line
  hasFilters(_, getters) {
    return getters.filtersCount > 0;
  },

  getAllAttributes(state) {
    let attributes = [];
    const joinSources = state.design.joins || [];
    const sources = [state.design].concat(joinSources);
    const batchCollect = (table, attributeTypes) => {
      attributeTypes.forEach((attributeType) => {
        const attributesByType = table[attributeType];
        if (attributesByType) {
          attributes = attributes.concat(attributesByType);
        }
      });
    };

    sources.forEach((source) => {
      batchCollect(source.relatedTable, ['columns', 'aggregates', 'timeframes']);
    });

    return attributes;
  },

  // eslint-disable-next-line no-shadow
  getAttributeByQueryAttribute(state, getters) {
    return (queryAttribute) => {
      const finder = attr => attr.sourceName === queryAttribute.sourceName && attr.name === queryAttribute.attributeName;
      return getters.getAllAttributes.find(finder);
    };
  },

  getAttributesBySource(state) {
    const sources = [];
    const design = state.design;
    const attributeFilter = attr => !attr.hidden;
    if (design.label) {
      sources.push({
        tableLabel: design.label,
        sourceName: design.name,
        columns: design.relatedTable.columns
          ? design.relatedTable.columns.filter(attributeFilter)
          : [],
        aggregates: design.relatedTable.aggregates
          ? design.relatedTable.aggregates.filter(attributeFilter)
          : [],
      });
    }
    if (design.joins) {
      design.joins.forEach((join) => {
        sources.push({
          tableLabel: join.label,
          sourceName: join.name,
          columns: join.relatedTable.columns
            ? join.relatedTable.columns.filter(attributeFilter)
            : [],
          aggregates: join.relatedTable.aggregates
            ? join.relatedTable.aggregates.filter(attributeFilter)
            : [],
        });
      });
    }
    return sources;
  },

  // eslint-disable-next-line no-shadow
  getFilter(_, getters) {
    // eslint-disable-next-line
    return (sourceName, name, filterType) => getters.getFiltersByType(filterType).find(filter => filter.name === name && filter.sourceName === sourceName);
  },

  getFiltersByType(state) {
    return filterType => state.filters[helpers.getFilterTypePlural(filterType)] || [];
  },

  // eslint-disable-next-line no-shadow
  getIsAttributeInFilters(_, getters) {
    // eslint-disable-next-line
    return (sourceName, name, filterType) => !!getters.getFilter(sourceName, name, filterType);
  },

  getIsOrderableAttributeAscending() {
    return orderableAttribute => orderableAttribute.direction === 'asc';
  },

  // eslint-disable-next-line no-shadow
  getQueryAttributeFromCollectionByAttribute(state) {
    return (orderCollection, attribute) => {
      const finder = queryAttribute => attribute.sourceName === queryAttribute.sourceName && attribute.name === queryAttribute.attributeName;
      return state.order[orderCollection].find(finder);
    };
  },

  // eslint-disable-next-line no-shadow
  getSelectedAttributes(_, getters) {
    const selector = attribute => attribute.selected;
    return getters.getAllAttributes.filter(selector);
  },

  // eslint-disable-next-line no-shadow
  getSelectedAttributesCount(_, getters) {
    return getters.getSelectedAttributes.length;
  },

  resultsCount(state) {
    if (!state.results) {
      return 0;
    }
    return state.results.length;
  },

  getDialect: state => state.dialect,

  hasJoins(state) {
    return !!(state.design.joins && state.design.joins.length);
  },

  showJoinColumnAggregateHeader: () => obj => !!obj,

  joinIsExpanded: () => join => join.expanded,

  getChartYAxis(state) {
    if (!state.resultAggregates) {
      return [];
    }
    const aggregates = Object.keys(state.resultAggregates);
    return aggregates;
  },

  isColumnSelectedAggregate: state => columnName => columnName in state.resultAggregates,

  getFormattedValue: () => (fmt, value) => SSF.format(fmt, Number(value)),

  currentModelLabel(state) {
    return utils.titleCase(state.currentModel);
  },

  currentDesignLabel(state) {
    return utils.titleCase(state.currentModel);
  },

  currentLimit(state) {
    return state.limit;
  },

  formattedSql(state) {
    return sqlFormatter.format(state.currentSQL);
  },
};

const actions = {
  resetDefaults: ({ commit }) => commit('resetDefaults'),

  getDesign({ commit, dispatch, state }, { model, design, slug }) {
    state.currentSQL = '';
    state.currentModel = model;
    state.currentDesign = design;

    return designApi.index(model, design)
      .then((response) => {
        commit('setDesign', response.data);
      })
      .then(reportsApi.loadReports)
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
    if (join.relatedTable.columns.length) {
      return;
    }
    designApi.getTable(join.relatedTable.name)
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

  toggleColumn({ commit }, column) {
    commit('toggleSelected', column);
  },

  toggleTimeframe({ commit }, timeframe) {
    commit('toggleSelected', timeframe);
  },

  toggleTimeframePeriod({ commit }, timeframePeriod) {
    commit('toggleSelected', timeframePeriod);
  },

  // eslint-disable-next-line
  toggleAggregate({ commit, getters }, { aggregate, sourceName }) {
    commit('toggleSelected', aggregate);

    if (!aggregate.selected) {
      const filter = getters.getFilter(sourceName, aggregate.name, 'aggregate');
      if (filter) {
        commit('removeFilter', filter);
      }
    }
  },

  limitSet({ commit }, limit) {
    commit('setLimit', limit);
  },

  // TODO: remove and use `mapMutations`
  setChartType({ commit }, chartType) {
    commit('setChartType', chartType);
  },

  // eslint-disable-next-line no-shadow
  getSQL({ commit, getters, state }, { run, load }) {
    this.dispatch('designs/resetErrorMessage');
    state.loadingQuery = !!run;

    const queryPayload = Object.assign({}, helpers.getQueryPayloadFromDesign(state), load);
    const postData = Object.assign({ run }, queryPayload);
    sqlApi
      .getSql(state.currentModel, state.currentDesign, postData)
      .then((response) => {
        if (run) {
          commit('setQueryResults', response.data);
          commit('setSQLResults', response.data);
          state.loadingQuery = false;
          commit('setSorting', getters.getAllAttributes);
        } else {
          commit('setSQLResults', response.data);
        }
      })
      .catch((e) => {
        commit('setSqlErrorMessage', e);
        state.loadingQuery = false;
      });
  },

  loadReport({ commit, state }, { name }) {
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

  saveReport({ commit, state }, { name }) {
    const postData = {
      name,
      model: state.currentModel,
      design: state.currentDesign,
      chartType: state.chartType,
      queryPayload: helpers.getQueryPayloadFromDesign(state),
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

  updateReport({ commit, state }) {
    state.activeReport.queryPayload = helpers.getQueryPayloadFromDesign(state);
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

  resetSortAttributes({ commit }) {
    commit('resetSortAttributes');
  },

  runQuery() {
    this.dispatch('designs/getSQL', {
      run: true,
    });
  },

  toggleLoadReportOpen({ commit }) {
    commit('setLoadReportToggle');
  },

  // eslint-disable-next-line no-shadow
  updateSortAttribute({ commit, getters }, queryAttribute) {
    const attribute = getters.getAttributeByQueryAttribute(queryAttribute);
    const matchInAssigned = getters.getQueryAttributeFromCollectionByAttribute('assigned', attribute);
    const matchInUnassigned = getters.getQueryAttributeFromCollectionByAttribute('unassigned', attribute);
    if (matchInAssigned) {
      const direction = getters.getIsOrderableAttributeAscending(matchInAssigned) ? 'desc' : 'asc';
      commit('setSortableAttributeDirection', { orderableAttribute: matchInAssigned, direction });
    } else if (matchInUnassigned) {
      commit('assignSortableAttribute', attribute);
    }

    this.dispatch('designs/runQuery');
  },

  // eslint-disable-next-line
  addFilter({ commit }, { sourceName, attribute, filterType, expression = '', value = '', isActive = true }) {
    const filter = {
      sourceName,
      name: attribute.name,
      expression,
      value,
      attribute,
      filterType,
      isActive,
    };
    commit('addFilter', filter);

    const isValidToggleSelection = !attribute.hasOwnProperty('selected') || !attribute.selected;
    if (filterType === 'aggregate' && isValidToggleSelection) {
      commit('toggleSelected', attribute);
    }
  },

  removeFilter({ commit }, filter) {
    commit('removeFilter', filter);
  },
};

const mutations = {
  assignSortableAttribute(state, attribute) {
    const orderableAttribute = state.order.unassigned.find(orderableAttr => orderableAttr.attributeName === attribute.name && orderableAttr.sourceName === attribute.sourceName);
    const idx = state.order.unassigned.indexOf(orderableAttribute);
    state.order.unassigned.splice(idx, 1);
    state.order.assigned.push(orderableAttribute);
  },

  resetDefaults(state) {
    lodash.assign(state, lodash.cloneDeep(defaultState));
  },

  resetSortAttributes(state) {
    const assigned = state.order.assigned;
    state.order.unassigned = state.order.unassigned.concat(assigned);
    state.order.assigned = [];
  },

  setChartType(state, chartType) {
    state.chartType = chartType;
  },

  setCurrentReport(state, report) {
    state.activeReport = report;
  },

  setFilterOptions(state, options) {
    state.filterOptions = options;
  },

  setStateFromLoadedReport(state, report) {
    // General UI state updates
    state.currentModel = report.model;
    state.currentDesign = report.design;
    state.chartType = report.chartType;
    state.limit = report.queryPayload.limit;
    state.dialect = report.queryPayload.dialect;

    // UI selected state adornment helpers for columns, aggregates, filters, joins, & timeframes
    const baseTable = state.design.relatedTable;
    const queryPayload = report.queryPayload;
    const joinColumnGroups = state.design.joins.reduce((acc, curr) => {
      acc.push({
        name: curr.name,
        columns: curr.relatedTable.columns,
        aggregates: curr.relatedTable.aggregates,
        timeframes: curr.relatedTable.timeframes,
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
    state.filters = queryPayload.filters;
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
    state.order = queryPayload.order;
    // base_table timeframes
    // TODO
  },

  addFilter(state, filter) {
    state.filters[helpers.getFilterTypePlural(filter.filterType)].push(filter);
  },

  removeFilter(state, filter) {
    if (filter) {
      const filtersByType = state.filters[helpers.getFilterTypePlural(filter.filterType)];
      const idx = filtersByType.indexOf(filter);
      filtersByType.splice(idx, 1);
    }
  },

  addSavedReportToReports(state, report) {
    state.reports.push(report);
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

  resetSaveReportSettings(state) {
    state.saveReportSettings = { name: null };
  },

  setSQLResults(state, results) {
    state.currentSQL = results.sql;
  },

  setQueryResults(state, results) {
    state.results = results.results;
    state.keys = results.keys;
    state.queryAttributes = results.queryAttributes;
    state.resultAggregates = results.aggregates;
  },

  setSorting(state, allAttributes) {
    state.queryAttributes.forEach((queryAttribute) => {
      const accounted = state.order.assigned.concat(state.order.unassigned);
      const finder = orderableAttribute => orderableAttribute.sourceName === queryAttribute.sourceName && orderableAttribute.attributeName === queryAttribute.attributeName;
      const isAccountedFor = accounted.find(finder);
      if (!isAccountedFor) {
        const targetAttribute = allAttributes.find(attribute => attribute.sourceName === queryAttribute.sourceName && attribute.name === queryAttribute.attributeName);
        state.order.unassigned.push({
          sourceName: targetAttribute.sourceName,
          sourceLabel: targetAttribute.sourceLabel,
          attributeName: targetAttribute.name,
          attributeLabel: targetAttribute.label,
          direction: 'asc',
        });
      }
    });
  },

  setSqlErrorMessage(state, e) {
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

  setErrorState(state) {
    state.hasSQLError = false;
    state.sqlErrorMessage = [];
  },

  toggleSelected(state, attribute) {
    Vue.set(attribute, 'selected', !attribute.selected);
  },

  toggleCollapsed(state, collapsable) {
    Vue.set(collapsable, 'collapsed', !collapsable.collapsed);
  },

  setSortableAttributeDirection(_, { orderableAttribute, direction }) {
    orderableAttribute.direction = direction;
  },

  setDesign(state, designData) {
    const joinSources = designData.joins || [];
    const sources = [designData].concat(joinSources);
    const batchSourcer = (source, attributeTypes) => {
      const table = source.relatedTable;
      attributeTypes.forEach((attributeType) => {
        if (table[attributeType]) {
          table[attributeType].forEach((attribute) => {
            attribute.sourceName = source.name;
            attribute.sourceLabel = source.label;
          });
        }
      });
    };

    sources.forEach((source) => {
      batchSourcer(source, ['columns', 'aggregates', 'timeframes']);
    });

    state.design = designData;
  },

  setLimit(state, limit) {
    state.limit = limit;
  },

  setDialect(state, dialect) {
    state.dialect = dialect;
  },
};

export default {
  namespaced: true,
  helpers,
  state: lodash.cloneDeep(defaultState),
  getters,
  actions,
  mutations,
};
