import Vue from 'vue'

import lodash from 'lodash'
import sqlFormatter from 'sql-formatter'
import SSF from 'ssf'

import designApi from '@/api/design'
import FilterModel from '@/store/models/FilterModel'
import sqlApi from '@/api/sql'
import utils from '@/utils/utils'
import { isDateAttribute } from '@/components/analyze/utils'
import { CHART_MODELS } from '@/components/analyze/charts/ChartModels'
import { QUERY_ATTRIBUTE_TYPES } from '@/api/design'
import { selected } from '@/utils/predicates'
import { namer } from '@/utils/mappers'

const defaultState = utils.deepFreeze({
  activeReport: {},
  chartType: CHART_MODELS.HORIZONTAL_BAR.type,
  currentDesign: '',
  currentModel: '',
  currentNamespace: '',
  currentSQL: '',
  design: {
    relatedTable: {}
  },
  filterOptions: [],
  filters: [],
  isLastRunResultsEmpty: false,
  hasCompletedFirstQueryRun: false,
  hasSQLError: false,
  isAutoRunQuery:
    'isAutoRunQuery' in localStorage
      ? localStorage.getItem('isAutoRunQuery') === 'true'
      : true,
  isLoadingQuery: false,
  limit: 50,
  order: {
    assigned: [],
    unassigned: []
  },
  queryAttributes: [],
  reports: [],
  resultAggregates: [],
  results: [],
  sqlErrorMessage: []
})

const helpers = {
  buildKey: (...parts) => lodash.join(parts, '.'),
  debouncedAutoRun: null,

  getFilterTypePlural(filterType) {
    return `${filterType}s`
  },

  getQueryPayloadFromDesign(state) {
    const selectedAttributeKeys = []

    // Inline fn helpers
    const namesOfSelected = arr => {
      if (!Array.isArray(arr)) {
        return null
      }
      return arr.filter(selected).map(({ name, key }) => {
        selectedAttributeKeys.push(key)
        return name
      })
    }

    const baseTable = state.design.relatedTable
    const columns = namesOfSelected(baseTable.columns)
    const aggregates = namesOfSelected(baseTable.aggregates) || []

    // Join table(s) setup
    if (!state.design.joins) {
      state.design.joins = []
    }
    const joins = state.design.joins.map(j => {
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
            periods: namesOfSelected(periods).map(name => ({ name }))
          }))
          .filter(tf => tf.periods.length)
      }

      return newJoin
    })

    // TODO update default empty array likely
    // in the ma_file_parser to set proper defaults
    // if user's exclude certain properties in their models
    const timeframes = (baseTable.timeframes || [])
      .map(({ name, periods }) => ({
        name: name,
        periods: namesOfSelected(periods).map(name => ({ name }))
      }))
      .filter(tf => tf.periods.length)

    // Ordering setup
    // We need to filter out attributes that are not actually selected,
    // since the ordering state is partially dependent on the most recent query
    // results, which could have included more selected attributes.
    const order = state.order.assigned
      .filter(({ attribute }) => selectedAttributeKeys.includes(attribute.key))
      .map(({ direction, attribute }) => ({
        key: attribute.key,
        direction: direction
      }))

    // Filtering setup - Enforce number type for aggregates as v-model approach overwrites as string
    const activeFilters = state.filters.filter(({ isActive }) => isActive)

    const filters = {
      columns: [],
      aggregates: []
    }

    filters.columns = activeFilters
      .filter(({ filterType }) => filterType === QUERY_ATTRIBUTE_TYPES.COLUMN)
      .map(({ attribute, expression, value }) => ({
        key: attribute.key,
        expression,
        value
      }))

    filters.aggregates = activeFilters
      .filter(
        ({ filterType }) => filterType === QUERY_ATTRIBUTE_TYPES.AGGREGATE
      )
      .map(({ attribute, expression, value }) => ({
        key: attribute.key,
        expression,
        value: Number(value)
      }))

    return {
      name: state.design.name,
      columns,
      aggregates,
      timeframes,
      joins,
      order,
      limit: state.limit,
      filters
    }
  }
}

const getters = {
  currentDesignLabel(state) {
    return utils.titleCase(state.currentDesign)
  },

  currentExtractor(state) {
    return state.currentNamespace.replace('model', 'tap')
  },

  currentLimit(state) {
    return state.limit
  },

  currentModelID(state) {
    return lodash.join([state.currentNamespace, state.currentModel], '/')
  },

  currentModelLabel(state) {
    return utils.titleCase(state.currentModel)
  },

  formattedSql(state) {
    return sqlFormatter.format(state.currentSQL)
  },

  getAttributes(state) {
    return (types = ['columns', 'aggregates', 'timeframes']) => {
      let attributes = []
      const joinSources = state.design.joins || []
      const sources = [state.design].concat(joinSources)
      const batchCollect = (table, attributeTypes) => {
        attributeTypes.forEach(attributeType => {
          attributes = attributes.concat(table[attributeType] || [])
        })
      }

      sources.forEach(source => {
        batchCollect(source.relatedTable, types)
      })

      return attributes
    }
  },

  getDateAttributes(_, getters) {
    return getters
      .getAttributes(['columns'])
      .filter(attribute => getters.getIsDateAttribute(attribute))
  },

  getIsDateAttribute() {
    return isDateAttribute
  },

  getFilters(state) {
    return attribute =>
      state.filters.filter(filter => filter.attribute.key === attribute.key)
  },

  getTableSources(state) {
    const sources = []
    const design = state.design
    const attributeFilter = attribute => !attribute.hidden

    if (design.label) {
      sources.push({
        name: design.name,
        label: design.label,
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
          name: join.name,
          label: join.label,
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

  getFormattedValue: () => (fmt, value) => SSF.format(fmt, Number(value)),

  getIsAttributeInFilters(_, getters) {
    return attribute => getters.getFilters(attribute).length > 0
  },

  getIsOrderableAttributeAscending() {
    return orderableAttribute => orderableAttribute.direction === 'asc'
  },

  getNonDateFiltersCount(_, getters) {
    return getters.getNonDateFilters.length
  },

  getNonDateFilters(state, getters) {
    const nonDateFilters = state.filters.filter(
      filter => !getters.getIsDateAttribute(filter.attribute)
    )
    return lodash.sortBy(nonDateFilters, 'name')
  },

  getOrderableAttributeFromCollectionByAttribute(state) {
    return (orderCollection, attribute) => {
      const finder = orderable => {
        return orderable.attribute.key === attribute.key
      }
      return state.order[orderCollection].find(finder)
    }
  },

  getSelectedAttributes(_, getters) {
    return getters.getAttributes().filter(selected)
  },

  getSelectedAttributesCount(_, getters) {
    return getters.getSelectedAttributes.length
  },

  hasChartableResults(state, getters) {
    return getters.hasResults && state.resultAggregates.length
  },

  hasJoins(state) {
    return !!(state.design.joins && state.design.joins.length)
  },

  hasNonDateFilters(_, getters) {
    return getters.getNonDateFiltersCount > 0
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

  showAttributesHeader: () => attributes => attributes && attributes.length
}

const actions = {
  addFilter({ commit, dispatch }, payload) {
    const filter = new FilterModel(payload)
    commit('addFilter', filter)

    // Aggregates must be selected if they're used as a filter target where columns do not
    const isValidToggleSelection =
      !filter.attribute.hasOwnProperty('selected') || !filter.attribute.selected
    if (
      filter.filterType === QUERY_ATTRIBUTE_TYPES.AGGREGATE &&
      isValidToggleSelection
    ) {
      commit('toggleSelected', filter.attribute)
    }

    dispatch('tryAutoRun')
  },

  cleanFiltering({ commit, getters }, attribute) {
    if (!attribute.selected) {
      const filters = getters.getFilters(attribute)
      if (filters.length > 0) {
        filters.forEach(filter => commit('removeFilter', filter))
      }
    }
  },

  cleanOrdering({ commit, getters, state }, attribute) {
    if (!attribute.selected) {
      const matchAssigned = getters.getOrderableAttributeFromCollectionByAttribute(
        'assigned',
        attribute
      )
      const matchUnassigned = getters.getOrderableAttributeFromCollectionByAttribute(
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

  deleteReport({ commit, dispatch, state }) {
    return dispatch(
      'dashboards/removeReportFromDashboards',
      state.activeReport.id,
      { root: true }
    )
      .then(() =>
        dispatch('reports/deleteReport', state.activeReport, {
          root: true
        })
      )
      .then(() => commit('setCurrentReport', null))
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

  getDesign(
    { commit, dispatch, rootGetters },
    { namespace, model, design, slug }
  ) {
    commit('resetSQLResults')
    commit('setCurrentMetadata', { namespace, model, design })

    const uponGetReports = dispatch('reports/getReports', null, {
      root: true
    })

    const uponGetDesign = designApi
      .index(namespace, model, design)
      .then(response => {
        commit('setDesign', response.data)
      })

    return Promise.all([uponGetDesign, uponGetReports])
      .then(() => {
        if (slug) {
          const reportMatch = rootGetters['reports/getReportBySlug']({
            design,
            model,
            namespace,
            slug
          })

          if (reportMatch) {
            dispatch('loadReport', reportMatch)
          }
        }
      })
      .catch(e => {
        commit('setSqlErrorMessage', e)
        commit('setIsLoadingQuery', false)
      })
  },

  getFilterOptions({ commit }) {
    sqlApi.getFilterOptions().then(response => {
      commit('setFilterOptions', response.data)
    })
  },

  getSQL({ commit, dispatch, state }, { run, payload }) {
    this.dispatch('designs/resetErrorMessage')
    commit('setIsLoadingQuery', !!run)

    const postData = Object.assign(
      { run },
      payload || helpers.getQueryPayloadFromDesign(state)
    )

    sqlApi
      .getSql(
        state.currentNamespace,
        state.currentModel,
        state.currentDesign,
        postData
      )
      .then(response => {
        // No response means empty query
        if (response.status === 204) {
          commit('resetQueryResults')
          commit('resetSQLResults')
        } else if (run) {
          commit('setHasCompletedFirstQueryRun', true)
          commit('setQueryResults', response.data)
          commit('setSQLResults', response.data)
          dispatch('setSorting', postData.order)
        } else {
          commit('setSQLResults', response.data)
        }
      })
      .catch(e => {
        commit('setSqlErrorMessage', e)
      })
      .finally(() => commit('setIsLoadingQuery', false))
  },

  loadReport({ state, commit, dispatch }, report) {
    const nameMatcher = (source, target) => source.name === target.name

    // UI selected state adornment helpers for columns, aggregates, joins, & timeframes
    const baseTable = state.design.relatedTable
    const queryPayload = report.queryPayload
    let joinColumnGroups = []
    if (state.design.joins) {
      joinColumnGroups = state.design.joins.reduce((acc, curr) => {
        acc.push({
          name: curr.name,
          columns: curr.relatedTable.columns,
          aggregates: curr.relatedTable.aggregates,
          timeframes: curr.relatedTable.timeframes
        })
        return acc
      }, [])
    }

    const setSelected = (sourceCollection, targetCollection) => {
      if (!(sourceCollection && targetCollection)) {
        return
      }

      sourceCollection.forEach(item => {
        if (targetCollection.includes(item.name)) {
          commit('toggleSelected', item)
        }
      })
    }

    // toggle the selected items
    setSelected(baseTable.columns, queryPayload.columns)
    setSelected(baseTable.aggregates, queryPayload.aggregates)
    setSelected(baseTable.timeframes, queryPayload.timeframes.map(namer))

    // timeframes periods
    queryPayload.timeframes.forEach(queryTimeframe => {
      const timeframe = baseTable.timeframes.find(tf =>
        nameMatcher(tf, queryTimeframe)
      )
      setSelected(timeframe.periods, queryTimeframe.periods.map(namer))
    })

    // joins, timeframes, and periods
    joinColumnGroups.forEach(joinGroup => {
      // joins - columns
      const targetJoin = queryPayload.joins.find(j => nameMatcher(j, joinGroup))

      if (targetJoin) {
        setSelected(joinGroup.columns, targetJoin.columns)
        setSelected(joinGroup.aggregates, targetJoin.aggregates)
        setSelected(joinGroup.timeframes, targetJoin.timeframes.map(namer))

        // timeframes periods
        targetJoin.timeframes.forEach(queryTimeframe => {
          const timeframe = joinGroup.timeframes.find(tf =>
            nameMatcher(tf, queryTimeframe)
          )
          setSelected(timeframe.periods, queryTimeframe.periods.map(namer))
        })
      }
    })

    dispatch('setFiltersFromQuery', queryPayload.filters)

    commit('setCurrentReport', report)
    this.dispatch('designs/getSQL', {
      run: true,
      payload: queryPayload
    })
  },

  limitSet({ commit }, limit) {
    commit('setLimit', limit)
  },

  removeFilter({ commit, dispatch }, filter) {
    commit('removeFilter', filter)
    dispatch('tryAutoRun')
  },

  resetDefaults: ({ commit }) => commit('resetDefaults'),

  resetErrorMessage({ commit }) {
    commit('setErrorState')
  },

  resetSortAttributes({ commit, dispatch }) {
    commit('resetSortAttributes')
    dispatch('tryAutoRun')
  },

  runQuery(_, isRun = true) {
    this.dispatch('designs/getSQL', {
      run: isRun
    })
  },

  saveReport({ commit, dispatch, rootGetters, state }, { name }) {
    const postData = {
      chartType: state.chartType,
      design: state.currentDesign,
      model: state.currentModel,
      namespace: state.currentNamespace,
      name,
      queryPayload: helpers.getQueryPayloadFromDesign(state)
    }
    return dispatch('reports/saveReport', postData, { root: true }).then(
      response => {
        const report = rootGetters['reports/getReportById'](response.data.id)
        commit('setCurrentReport', report)
      }
    )
  },

  // TODO: remove and use `mapMutations`
  setChartType({ commit }, chartType) {
    commit('setChartType', chartType)
  },

  toggleAggregate({ commit, dispatch }, aggregate) {
    commit('toggleSelected', aggregate)
    dispatch('cleanOrdering', aggregate)
    dispatch('cleanFiltering', aggregate)
    dispatch('tryAutoRun')
  },

  tryAutoRun({ dispatch, state }) {
    if (helpers.debouncedAutoRun) {
      helpers.debouncedAutoRun.cancel()
    }
    helpers.debouncedAutoRun = lodash.debounce(() => {
      const hasRan = state.results.length > 0 || state.isLastRunResultsEmpty
      dispatch('runQuery', state.isAutoRunQuery && hasRan)
    }, 500)
    helpers.debouncedAutoRun()
  },

  toggleAttribute({ commit, dispatch }, attribute) {
    commit('toggleSelected', attribute)
    dispatch('cleanOrdering', attribute)
    dispatch('tryAutoRun')
  },

  toggleIsAutoRunQuery({ commit, state }) {
    commit('setIsAutoRunQuery', !state.isAutoRunQuery)
  },

  toggleLoadReportOpen({ commit }) {
    commit('setLoadReportToggle')
  },

  toggleTimeframe({ commit }, timeframe) {
    commit('toggleSelected', timeframe)
  },

  updateReport({ commit, dispatch, rootGetters, state }, payload) {
    commit('updateActiveReport')
    const postData = {
      ...state.activeReport,
      ...payload
    }
    return dispatch('reports/updateReport', postData, { root: true }).then(
      response => {
        const report = rootGetters['reports/getReportById'](response.data.id)
        return commit('setCurrentReport', report)
      }
    )
  },

  updateSortAttribute({ commit, dispatch, getters }, queryAttribute) {
    const matchInAssigned = getters.getOrderableAttributeFromCollectionByAttribute(
      'assigned',
      queryAttribute
    )
    const matchInUnassigned = getters.getOrderableAttributeFromCollectionByAttribute(
      'unassigned',
      queryAttribute
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
      commit('assignSortableAttribute', queryAttribute)
    }

    dispatch('runQuery')
  },

  setOrderAssigned({ commit, dispatch }, value) {
    commit('setOrderAssigned', value)
    dispatch('runQuery')
  },

  setOrderUnassigned({ commit }, value) {
    commit('setOrderUnassigned', value)
  },

  setSorting({ commit, state }, queryOrder) {
    const orderAssigned = []
    queryOrder.forEach(queryOrderAttribute => {
      const queryAttribute = state.queryAttributes.find(queryAttribute =>
        queryOrderAttribute.key
          ? queryOrderAttribute.key === queryAttribute.key
          : queryOrderAttribute.sourceName === queryAttribute.sourceName &&
            queryOrderAttribute.attributeName === queryAttribute.attributeName
      )
      if (queryAttribute) {
        orderAssigned.push({
          attribute: queryAttribute,
          direction: queryOrderAttribute.direction
        })
      }
    })

    const orderUnassigned = []
    state.queryAttributes.forEach(queryAttribute => {
      if (
        !orderAssigned.find(
          orderable => orderable.attribute.key === queryAttribute.key
        )
      ) {
        orderUnassigned.push({
          attribute: queryAttribute,
          direction: 'asc'
        })
      }
    })

    commit('setOrderAssigned', orderAssigned)
    commit('setOrderUnassigned', orderUnassigned)
  },

  setFiltersFromQuery({ commit, getters }, queryFilters) {
    commit('resetFilters')

    const filterTypes = [
      QUERY_ATTRIBUTE_TYPES.COLUMN,
      QUERY_ATTRIBUTE_TYPES.AGGREGATE
    ]
    filterTypes.forEach(filterType => {
      const filterTypePlural = helpers.getFilterTypePlural(filterType)
      queryFilters[filterTypePlural].forEach(queryFilter => {
        let attribute
        if (queryFilter.key) {
          for (let source of getters.getTableSources) {
            attribute = source[filterTypePlural].find(
              attribute => attribute.key === queryFilter.key
            )

            if (attribute) {
              break
            }
          }
        } else {
          const source = getters.getTableSources.find(
            source => source.name === queryFilter.sourceName
          )
          if (!source) {
            return
          }

          attribute = source[filterTypePlural].find(
            attribute => attribute.name === queryFilter.name
          )
        }

        if (!attribute) {
          return
        }

        const filter = new FilterModel({
          attribute,
          filterType,
          expression: queryFilter.expression,
          value: queryFilter.value
        })
        commit('addFilter', filter)
      })
    })
  }
}

const mutations = {
  addFilter(state, filter) {
    state.filters.push(filter)
  },

  assignSortableAttribute(state, queryAttribute) {
    const orderableAttribute = state.order.unassigned.find(
      orderable => orderable.attribute.key === queryAttribute.key
    )
    const idx = state.order.unassigned.indexOf(orderableAttribute)
    Vue.delete(state.order.unassigned, idx)
    state.order.assigned.push(orderableAttribute)
  },

  removeFilter(state, filter) {
    if (filter) {
      const idx = state.filters.indexOf(filter)
      Vue.delete(state.filters, idx)
    }
  },

  removeOrder(_, { collection, queryAttribute }) {
    const idx = collection.indexOf(queryAttribute)
    Vue.delete(collection, idx)
  },

  resetDefaults(state) {
    lodash.assign(state, lodash.cloneDeep(defaultState))
  },

  resetFilters(state) {
    state.filters = []
  },

  resetQueryResults(state) {
    state.isLastRunResultsEmpty = false
    state.results = []
    state.queryAttributes = []
    state.resultAggregates = []
  },

  resetSortAttributes(state) {
    const assigned = state.order.assigned
    state.order.unassigned = state.order.unassigned.concat(assigned)
    state.order.assigned = []
  },

  resetSQLResults(state) {
    state.currentSQL = ''
  },

  setChartType(state, chartType) {
    state.chartType = chartType
  },

  setCurrentMetadata(state, { namespace, model, design }) {
    state.currentNamespace = namespace
    state.currentModel = model
    state.currentDesign = design
  },

  setCurrentReport(state, report) {
    if (report) {
      state.activeReport = report
      state.chartType = report.chartType
      state.limit = report.queryPayload.limit

      // state.{order,filters} is now set based on
      // report.queryPayload.{order,filters}, not
      // report.{order,filters}
      delete report.order
      delete report.filters
    } else {
      state.activeReport = {}
    }
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
          })
        }
      })
    }

    sources.forEach(source => {
      batchSourcer(source, ['columns', 'aggregates', 'timeframes'])
    })

    state.design = designData
  },

  setIsAutoRunQuery(state, value) {
    state.isAutoRunQuery = value
    localStorage.setItem('isAutoRunQuery', state.isAutoRunQuery)
  },

  setErrorState(state) {
    state.hasSQLError = false
    state.sqlErrorMessage = []
  },

  setFilterOptions(state, options) {
    state.filterOptions = options
  },

  setHasCompletedFirstQueryRun(state, value) {
    state.hasCompletedFirstQueryRun = value
  },

  setIsLoadingQuery(state, value) {
    state.isLoadingQuery = value
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

  setLimit(state, limit) {
    state.limit = limit
  },

  setOrderAssigned(state, value) {
    state.order.assigned = value
  },

  setOrderUnassigned(state, value) {
    state.order.unassigned = value
  },

  setQueryResults(state, payload) {
    state.isLastRunResultsEmpty = payload.empty
    state.results = payload.results
    state.queryAttributes = payload.queryAttributes
    state.resultAggregates = payload.aggregates
  },

  setSortableAttributeDirection(_, { orderableAttribute, direction }) {
    orderableAttribute.direction = direction
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

  setSQLResults(state, payload) {
    state.currentSQL = payload.sql
  },

  toggleCollapsed(state, collapsable) {
    Vue.set(collapsable, 'collapsed', !collapsable.collapsed)
  },

  toggleSelected(state, attribute) {
    Vue.set(attribute, 'selected', !attribute.selected)
  },

  updateActiveReport(state) {
    state.activeReport.queryPayload = helpers.getQueryPayloadFromDesign(state)
    state.activeReport.chartType = state.chartType
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
