import Vue from 'vue'

import lodash from 'lodash'
import sqlFormatter from 'sql-formatter'
import SSF from 'ssf'

import designApi from '../../api/design'
import reportsApi from '../../api/reports'
import sqlApi from '../../api/sql'
import utils from '@/utils/utils'

const defaultState = utils.deepFreeze({
  activeReport: {},
  chartType: 'BarChart',
  currentDesign: '',
  currentModel: '',
  currentSQL: '',
  design: {
    relatedTable: {}
  },
  dialect: null,
  filterOptions: [],
  filters: {
    aggregates: [],
    columns: []
  },
  hasSQLError: false,
  keys: [],
  limit: 50,
  loadingQuery: false,
  order: {
    assigned: [],
    unassigned: []
  },
  queryAttributes: [],
  reports: [],
  resultAggregates: {},
  results: [],
  saveReportSettings: { name: null },
  sqlErrorMessage: []
})

const helpers = {
  getFilterTypePlural(filterType) {
    return `${filterType}s`
  },

  getQueryPayloadFromDesign(state) {
    // Inline fn helpers
    const selected = x => x.selected
    const namesOfSelected = arr => {
      if (!Array.isArray(arr)) {
        return null
      }
      return arr.filter(selected).map(x => x.name)
    }

    const baseTable = state.design.relatedTable
    const columns = namesOfSelected(baseTable.columns)
    const aggregates = namesOfSelected(baseTable.aggregates) || []

    // Join table(s) setup
    if (!state.design.joins) {
      state.design.joins = []
    }
    const joins = state.design.joins
      .map(j => {
        const table = j.relatedTable
        const newJoin = {}

        newJoin.name = j.name
        newJoin.columns = namesOfSelected(table.columns) || []
        newJoin.aggregates = namesOfSelected(table.aggregates) || []

        if (table.timeframes) {
          newJoin.timeframes = table.timeframes
            .filter(selected)
            .map(({ name, periods }) => ({
              name,
              periods: periods.filter(selected)
            }))
        }

        return newJoin
      })
      .filter(j => !!(j.columns || j.aggregates))

    // TODO update default empty array likely
    // in the ma_file_parser to set proper defaults
    // if user's exclude certain properties in their models
    const timeframes =
      baseTable.timeframes ||
      []
        .map(tf => ({
          name: tf.name,
          periods: tf.periods.filter(selected)
        }))
        .filter(tf => tf.periods.length)

    // Ordering setup
    const order = state.order.assigned

    // Filtering setup - Enforce number type for aggregates as v-model approach overwrites as string
    const filters = lodash.cloneDeep(state.filters)
    if (filters && filters.aggregates) {
      filters.aggregates = filters.aggregates
        .filter(aggregate => aggregate.isActive)
        .map(aggregate => {
          aggregate.value = Number(aggregate.value)
          return aggregate
        })
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
      filters
    }
  }
}

const getters = {
  currentDesignLabel(state) {
    return utils.titleCase(state.currentModel)
  },

  currentLimit(state) {
    return state.limit
  },

  currentModelLabel(state) {
    return utils.titleCase(state.currentModel)
  },

  filtersCount(state) {
    return state.filters.columns.length + state.filters.aggregates.length
  },

  formattedSql(state) {
    return sqlFormatter.format(state.currentSQL)
  },

  getAllAttributes(state) {
    let attributes = []
    const joinSources = state.design.joins || []
    const sources = [state.design].concat(joinSources)
    const batchCollect = (table, attributeTypes) => {
      attributeTypes.forEach(attributeType => {
        const attributesByType = table[attributeType]
        if (attributesByType) {
          attributes = attributes.concat(attributesByType)
        }
      })
    }

    sources.forEach(source => {
      batchCollect(source.relatedTable, ['columns', 'aggregates', 'timeframes'])
    })

    return attributes
  },

  // eslint-disable-next-line no-shadow
  getAttributeByQueryAttribute(state, getters) {
    return queryAttribute => {
      const finder = attr =>
        attr.sourceName === queryAttribute.sourceName &&
        attr.name === queryAttribute.attributeName
      return getters.getAllAttributes.find(finder)
    }
  },

  getChartYAxis(state) {
    if (!state.resultAggregates) {
      return []
    }
    const aggregates = Object.keys(state.resultAggregates)
    return aggregates
  },

  getDialect: state => state.dialect,

  // eslint-disable-next-line no-shadow
  getFilter(_, getters) {
    // eslint-disable-next-line
    return (sourceName, name, filterType) =>
      getters
        .getFiltersByType(filterType)
        .find(
          filter => filter.name === name && filter.sourceName === sourceName
        )
  },

  getFilterAttributes(state) {
    const sources = []
    const design = state.design
    const attributeFilter = attr => !attr.hidden
    if (design.label) {
      sources.push({
        tableLabel: design.label,
        sourceName: design.name,
        columns: design.relatedTable.columns
          ? design.relatedTable.columns.filter(attributeFilter)
          : [],
        aggregates: design.relatedTable.aggregates
          ? design.relatedTable.aggregates.filter(attributeFilter)
          : []
      })
    }
    if (design.joins) {
      design.joins.forEach(join => {
        sources.push({
          tableLabel: join.label,
          sourceName: join.name,
          columns: join.relatedTable.columns
            ? join.relatedTable.columns.filter(attributeFilter)
            : [],
          aggregates: join.relatedTable.aggregates
            ? join.relatedTable.aggregates.filter(attributeFilter)
            : []
        })
      })
    }
    return sources
  },

  getFiltersByType(state) {
    return filterType =>
      state.filters[helpers.getFilterTypePlural(filterType)] || []
  },

  getFormattedValue: () => (fmt, value) => SSF.format(fmt, Number(value)),

  // eslint-disable-next-line no-shadow
  getIsAttributeInFilters(_, getters) {
    // eslint-disable-next-line
    return (sourceName, name, filterType) =>
      !!getters.getFilter(sourceName, name, filterType)
  },

  getIsOrderableAttributeAscending() {
    return orderableAttribute => orderableAttribute.direction === 'asc'
  },

  // eslint-disable-next-line no-shadow
  getQueryAttributeFromCollectionByAttribute(state) {
    return (orderCollection, attribute) => {
      const finder = queryAttribute =>
        attribute.sourceName === queryAttribute.sourceName &&
        attribute.name === queryAttribute.attributeName
      return state.order[orderCollection].find(finder)
    }
  },

  // eslint-disable-next-line no-shadow
  getSelectedAttributes(_, getters) {
    const selector = attribute => attribute.selected
    return getters.getAllAttributes.filter(selector)
  },

  // eslint-disable-next-line no-shadow
  getSelectedAttributesCount(_, getters) {
    return getters.getSelectedAttributes.length
  },

  // eslint-disable-next-line
  hasChartableResults(state, getters) {
    return getters.hasResults && state.resultAggregates.length
  },

  // eslint-disable-next-line
  hasFilters(_, getters) {
    return getters.filtersCount > 0
  },

  hasJoins(state) {
    return !!(state.design.joins && state.design.joins.length)
  },

  hasResults(state) {
    if (!state.results) {
      return false
    }
    return !!state.results.length
  },

  isColumnSelectedAggregate: state => columnName =>
    columnName in state.resultAggregates,

  joinIsExpanded: () => join => join.expanded,

  resultsCount(state) {
    if (!state.results) {
      return 0
    }
    return state.results.length
  },

  showJoinColumnAggregateHeader: () => obj => !!obj
}

const actions = {
  // eslint-disable-next-line
  addFilter(
    { commit },
    {
      sourceName,
      attribute,
      filterType,
      expression = '',
      value = '',
      isActive = true
    }
  ) {
    const filter = {
      sourceName,
      name: attribute.name,
      expression,
      value,
      attribute,
      filterType,
      isActive
    }
    commit('addFilter', filter)

    const isValidToggleSelection =
      !attribute.hasOwnProperty('selected') || !attribute.selected
    if (filterType === 'aggregate' && isValidToggleSelection) {
      commit('toggleSelected', attribute)
    }
  },

  checkAutoRun({ dispatch, state }) {
    if (state.results.length > 0) {
      dispatch('runQuery')
    }
  },

  // eslint-disable-next-line no-shadow
  cleanFiltering({ commit, getters }, { attribute, type }) {
    if (!attribute.selected) {
      const filter = getters.getFilter(
        attribute.sourceName,
        attribute.name,
        type
      )
      if (filter) {
        commit('removeFilter', filter)
      }
    }
  },

  // eslint-disable-next-line no-shadow
  cleanOrdering({ commit, getters, state }, attribute) {
    if (!attribute.selected) {
      const matchAssigned = getters.getQueryAttributeFromCollectionByAttribute(
        'assigned',
        attribute
      )
      const matchUnassigned = getters.getQueryAttributeFromCollectionByAttribute(
        'unassigned',
        attribute
      )
      if (matchAssigned || matchUnassigned) {
        commit('removeOrder', {
          collection: state.order[matchAssigned ? 'assigned' : 'unassigned'],
          queryAttribute: matchAssigned || matchUnassigned
        })
      }
    }
  },

  expandJoinRow({ commit }, join) {
    // already fetched columns
    commit('toggleCollapsed', join)
    if (join.relatedTable.columns.length) {
      return
    }
    designApi.getTable(join.relatedTable.name).then(response => {
      commit('setJoinColumns', {
        columns: response.data.columns,
        join
      })
      commit('setJoinTimeframes', {
        timeframes: response.data.timeframes,
        join
      })
      commit('setJoinAggregates', {
        aggregates: response.data.aggregates,
        join
      })
    })
  },

  expandRow({ commit }, row) {
    commit('toggleCollapsed', row)
  },

  getDesign({ commit, dispatch, state }, { model, design, slug }) {
    state.currentSQL = ''
    state.currentModel = model
    state.currentDesign = design

    return designApi
      .index(model, design)
      .then(response => {
        commit('setDesign', response.data)
      })
      .then(reportsApi.loadReports)
      .then(response => {
        state.reports = response.data
        if (slug) {
          const reportMatch = state.reports.find(report => report.slug === slug)
          if (reportMatch) {
            dispatch('loadReport', reportMatch)
          }
        }
      })
      .catch(e => {
        commit('setSqlErrorMessage', e)
        state.loadingQuery = false
      })
  },

  getFilterOptions({ commit }) {
    sqlApi.getFilterOptions().then(response => {
      commit('setFilterOptions', response.data)
    })
  },

  // eslint-disable-next-line no-shadow
  getSQL({ commit, getters, state }, { run, load }) {
    this.dispatch('designs/resetErrorMessage')
    state.loadingQuery = !!run

    const queryPayload = Object.assign(
      {},
      helpers.getQueryPayloadFromDesign(state),
      load
    )
    const postData = Object.assign({ run }, queryPayload)
    sqlApi
      .getSql(state.currentModel, state.currentDesign, postData)
      .then(response => {
        if (run) {
          commit('setQueryResults', response.data)
          commit('setSQLResults', response.data)
          state.loadingQuery = false
          commit('setSorting', getters.getAllAttributes)
        } else {
          commit('setSQLResults', response.data)
        }
      })
      .catch(e => {
        commit('setSqlErrorMessage', e)
        state.loadingQuery = false
      })
  },

  loadReport({ commit, state }, { name }) {
    reportsApi
      .loadReport(name)
      .then(response => {
        const report = response.data
        this.dispatch('designs/getSQL', {
          run: true,
          load: report.queryPayload
        })
        commit('setCurrentReport', report)
        commit('setStateFromLoadedReport', report)
      })
      .catch(e => {
        commit('setSqlErrorMessage', e)
        state.loadingQuery = false
      })
  },

  limitSet({ commit }, limit) {
    commit('setLimit', limit)
  },

  removeFilter({ commit }, filter) {
    commit('removeFilter', filter)
  },

  resetDefaults: ({ commit }) => commit('resetDefaults'),

  resetErrorMessage({ commit }) {
    commit('setErrorState')
  },

  resetSortAttributes({ commit, dispatch }) {
    commit('resetSortAttributes')
    dispatch('checkAutoRun')
  },

  runQuery() {
    this.dispatch('designs/getSQL', {
      run: true
    })
  },

  saveReport({ commit, state }, { name }) {
    const postData = {
      chartType: state.chartType,
      design: state.currentDesign,
      filters: state.filters,
      model: state.currentModel,
      name,
      order: state.order,
      queryPayload: helpers.getQueryPayloadFromDesign(state)
    }
    return reportsApi.saveReport(postData).then(response => {
      commit('resetSaveReportSettings')
      commit('setCurrentReport', response.data)
      commit('addSavedReportToReports', response.data)
    })
  },

  // TODO: remove and use `mapMutations`
  setChartType({ commit }, chartType) {
    commit('setChartType', chartType)
  },

  toggleAggregate({ commit, dispatch }, aggregate) {
    commit('toggleSelected', aggregate)
    dispatch('cleanOrdering', aggregate)
    dispatch('cleanFiltering', { attribute: aggregate, type: 'aggregate' })
    dispatch('checkAutoRun')
  },

  toggleColumn({ commit, dispatch }, column) {
    commit('toggleSelected', column)
    dispatch('cleanOrdering', column)
    dispatch('checkAutoRun')
  },

  toggleLoadReportOpen({ commit }) {
    commit('setLoadReportToggle')
  },

  toggleTimeframe({ commit, dispatch }, timeframe) {
    commit('toggleSelected', timeframe)
    dispatch('cleanOrdering', timeframe)
    dispatch('checkAutoRun')
  },

  toggleTimeframePeriod({ commit, dispatch }, timeframePeriod) {
    commit('toggleSelected', timeframePeriod)
    dispatch('cleanOrdering', timeframePeriod)
    dispatch('checkAutoRun')
  },

  updateReport({ commit, state }) {
    state.activeReport.queryPayload = helpers.getQueryPayloadFromDesign(state)
    state.activeReport.chartType = state.chartType
    return reportsApi.updateReport(state.activeReport).then(response => {
      commit('resetSaveReportSettings')
      commit('setCurrentReport', response.data)
    })
  },

  // eslint-disable-next-line no-shadow
  updateSortAttribute({ commit, getters }, queryAttribute) {
    const attribute = getters.getAttributeByQueryAttribute(queryAttribute)
    const matchInAssigned = getters.getQueryAttributeFromCollectionByAttribute(
      'assigned',
      attribute
    )
    const matchInUnassigned = getters.getQueryAttributeFromCollectionByAttribute(
      'unassigned',
      attribute
    )
    if (matchInAssigned) {
      const direction = getters.getIsOrderableAttributeAscending(
        matchInAssigned
      )
        ? 'desc'
        : 'asc'
      commit('setSortableAttributeDirection', {
        orderableAttribute: matchInAssigned,
        direction
      })
    } else if (matchInUnassigned) {
      commit('assignSortableAttribute', attribute)
    }

    this.dispatch('designs/runQuery')
  }
}

const mutations = {
  addFilter(state, filter) {
    state.filters[helpers.getFilterTypePlural(filter.filterType)].push(filter)
  },

  addSavedReportToReports(state, report) {
    state.reports.push(report)
  },

  assignSortableAttribute(state, attribute) {
    const orderableAttribute = state.order.unassigned.find(
      orderableAttr =>
        orderableAttr.attributeName === attribute.name &&
        orderableAttr.sourceName === attribute.sourceName
    )
    const idx = state.order.unassigned.indexOf(orderableAttribute)
    state.order.unassigned.splice(idx, 1)
    state.order.assigned.push(orderableAttribute)
  },

  removeFilter(state, filter) {
    if (filter) {
      const filtersByType =
        state.filters[helpers.getFilterTypePlural(filter.filterType)]
      const idx = filtersByType.indexOf(filter)
      filtersByType.splice(idx, 1)
    }
  },

  removeOrder(state, { collection, queryAttribute }) {
    const idx = collection.indexOf(queryAttribute)
    collection.splice(idx, 1)
  },

  resetDefaults(state) {
    lodash.assign(state, lodash.cloneDeep(defaultState))
  },

  resetSaveReportSettings(state) {
    state.saveReportSettings = { name: null }
  },

  resetSortAttributes(state) {
    const assigned = state.order.assigned
    state.order.unassigned = state.order.unassigned.concat(assigned)
    state.order.assigned = []
  },

  setChartType(state, chartType) {
    state.chartType = chartType
  },

  setCurrentReport(state, report) {
    state.activeReport = report
  },

  setDesign(state, designData) {
    const joinSources = designData.joins || []
    const sources = [designData].concat(joinSources)
    const batchSourcer = (source, attributeTypes) => {
      const table = source.relatedTable
      attributeTypes.forEach(attributeType => {
        if (table[attributeType]) {
          table[attributeType].forEach(attribute => {
            attribute.sourceName = source.name
            attribute.sourceLabel = source.label
          })
        }
      })
    }

    sources.forEach(source => {
      batchSourcer(source, ['columns', 'aggregates', 'timeframes'])
    })

    state.design = designData
  },

  setDialect(state, dialect) {
    state.dialect = dialect
  },

  setErrorState(state) {
    state.hasSQLError = false
    state.sqlErrorMessage = []
  },

  setFilterOptions(state, options) {
    state.filterOptions = options
  },

  setLimit(state, limit) {
    state.limit = limit
  },

  setJoinAggregates(_, { aggregates, join }) {
    join.aggregates = aggregates
  },

  setJoinColumns(_, { columns, join }) {
    join.columns = columns
  },

  setJoinTimeframes(_, { timeframes, join }) {
    join.timeframes = timeframes
  },

  setQueryResults(state, results) {
    state.results = results.results
    state.keys = results.keys
    state.queryAttributes = results.queryAttributes
    state.resultAggregates = results.aggregates
  },

  setSortableAttributeDirection(_, { orderableAttribute, direction }) {
    orderableAttribute.direction = direction
  },

  setSorting(state, allAttributes) {
    state.queryAttributes.forEach(queryAttribute => {
      const accounted = state.order.assigned.concat(state.order.unassigned)
      const finder = orderableAttribute =>
        orderableAttribute.sourceName === queryAttribute.sourceName &&
        orderableAttribute.attributeName === queryAttribute.attributeName
      const isAccountedFor = accounted.find(finder)
      if (!isAccountedFor) {
        const targetAttribute = allAttributes.find(
          attribute =>
            attribute.sourceName === queryAttribute.sourceName &&
            attribute.name === queryAttribute.attributeName
        )
        state.order.unassigned.push({
          sourceName: targetAttribute.sourceName,
          sourceLabel: targetAttribute.sourceLabel,
          attributeName: targetAttribute.name,
          attributeLabel: targetAttribute.label,
          direction: 'asc'
        })
      }
    })
  },

  setSqlErrorMessage(state, e) {
    state.hasSQLError = true
    if (!e.response) {
      state.sqlErrorMessage = [
        "Something went wrong on our end. We'll check our error logs and get back to you."
      ]
      return
    }
    const error = e.response.data
    state.sqlErrorMessage = [error.code, error.orig, error.statement]
  },

  setSQLResults(state, results) {
    state.currentSQL = results.sql
  },

  setStateFromLoadedReport(state, report) {
    // General UI state updates
    state.chartType = report.chartType
    state.currentModel = report.model
    state.currentDesign = report.design
    state.dialect = report.queryPayload.dialect
    state.filters = report.filters
    state.limit = report.queryPayload.limit
    state.order = report.order

    // UI selected state adornment helpers for columns, aggregates, joins, & timeframes
    const baseTable = state.design.relatedTable
    const queryPayload = report.queryPayload
    const joinColumnGroups = state.design.joins.reduce((acc, curr) => {
      acc.push({
        name: curr.name,
        columns: curr.relatedTable.columns,
        aggregates: curr.relatedTable.aggregates,
        timeframes: curr.relatedTable.timeframes
      })
      return acc
    }, [])
    const nameMatcher = (source, target) => source.name === target.name
    const nameMapper = item => item.name
    const setSelected = (sourceCollection, targetCollection) => {
      sourceCollection.forEach(item => {
        item.selected = targetCollection.includes(item.name)
      })
    }

    // columns
    setSelected(baseTable.columns, queryPayload.columns)
    // aggregates
    setSelected(baseTable.aggregates, queryPayload.aggregates)
    // joins, timeframes, and periods
    joinColumnGroups.forEach(joinGroup => {
      // joins - columns
      const targetJoin = queryPayload.joins.find(j => nameMatcher(j, joinGroup))
      setSelected(joinGroup.columns, targetJoin.columns)
      // joins - aggregates
      if (joinGroup.aggregates) {
        setSelected(joinGroup.aggregates, targetJoin.aggregates)
      }
      // timeframes
      if (targetJoin && targetJoin.timeframes) {
        setSelected(joinGroup.timeframes, targetJoin.timeframes.map(nameMapper))
        // periods
        joinGroup.timeframes.forEach(timeframe => {
          const targetTimeframe = targetJoin.timeframes.find(tf =>
            nameMatcher(tf, timeframe)
          )
          if (targetTimeframe && targetTimeframe.periods) {
            setSelected(
              timeframe.periods,
              targetTimeframe.periods.map(nameMapper)
            )
          }
        })
      }
    })
  },

  toggleCollapsed(state, collapsable) {
    Vue.set(collapsable, 'collapsed', !collapsable.collapsed)
  },

  toggleSelected(state, attribute) {
    Vue.set(attribute, 'selected', !attribute.selected)
  }
}

export default {
  namespaced: true,
  helpers,
  state: lodash.cloneDeep(defaultState),
  getters,
  actions,
  mutations
}
