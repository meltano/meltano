import Vue from 'vue'

import lodash from 'lodash'
import sqlFormatter from 'sql-formatter'
import SSF from 'ssf'

import designApi from '../../api/design'
import reportsApi from '../../api/reports'
import sqlApi from '../../api/sql'
import utils from '@/utils/utils'
import { selected } from '@/utils/predicates'
import { namer } from '@/utils/mappers'

const defaultState = utils.deepFreeze({
  activeReport: {},
  chartType: 'BarChart',
  currentDesign: '',
  currentModel: '',
  currentNamespace: '',
  currentSQL: '',
  design: {
    relatedTable: {}
  },
  filterOptions: [],
  filters: {
    aggregates: [],
    columns: []
  },
  isLastRunResultsEmpty: false,
  hasSQLError: false,
  isAutoRunQuery: true,
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
  saveReportSettings: { name: null },
  sqlErrorMessage: []
})

const helpers = {
  getFilterTypePlural(filterType) {
    return `${filterType}s`
  },

  getQueryPayloadFromDesign(state) {
    // Inline fn helpers
    const namesOfSelected = arr => {
      if (!Array.isArray(arr)) {
        return null
      }
      return arr.filter(selected).map(namer)
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
            .filter(tf => tf.periods.length)
        }

        return newJoin
      })
      .filter(j => !!(j.columns || j.aggregates))

    // TODO update default empty array likely
    // in the ma_file_parser to set proper defaults
    // if user's exclude certain properties in their models
    const timeframes = (baseTable.timeframes || [])
      .map(tf => ({
        name: tf.name,
        periods: tf.periods.filter(selected)
      }))
      .filter(tf => tf.periods.length)

    // Ordering setup
    const order = state.order.assigned.map(orderable => {
      return {
        direction: orderable.direction,
        sourceName: orderable.attribute.sourceName,
        attributeName: orderable.attribute.name
      }
    })

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
      filters
    }
  }
}

const getters = {
  currentDesignLabel(state) {
    return utils.titleCase(state.currentDesign)
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

  filtersCount(state) {
    return state.filters.columns.length + state.filters.aggregates.length
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
          const attributesByType = table[attributeType]
          if (attributesByType) {
            attributes = attributes.concat(attributesByType)
          }
        })
      }

      sources.forEach(source => {
        batchCollect(source.relatedTable, types)
      })

      return attributes
    }
  },

  // eslint-disable-next-line no-shadow
  getAttributeByQueryAttribute(_, getters) {
    return queryAttribute => {
      const finder = attr =>
        attr.sourceName === queryAttribute.sourceName &&
        attr.name === queryAttribute.attributeName
      return getters.getAttributes().find(finder)
    }
  },

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
  getOrderableAttributeFromCollectionByAttribute(state) {
    return (orderCollection, attribute) => {
      const finder = orderableAttribute => {
        return orderableAttribute.attribute === attribute
      }
      return state.order[orderCollection].find(finder)
    }
  },

  // eslint-disable-next-line no-shadow
  getSelectedAttributes(_, getters) {
    return getters.getAttributes().filter(selected)
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

  tryAutoRun({ dispatch, state }) {
    const hasRan = state.results.length > 0 || state.isLastRunResultsEmpty
    dispatch('runQuery', state.isAutoRunQuery && hasRan)
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

  getDesign({ commit, dispatch, state }, { namespace, model, design, slug }) {
    commit('resetSQLResults')
    commit('setCurrentMetadata', { namespace, model, design })

    return designApi
      .index(namespace, model, design)
      .then(response => {
        commit('setDesign', response.data)
      })
      .then(reportsApi.loadReports)
      .then(response => {
        commit('setReports', response.data)
        if (slug) {
          const reportMatch = state.reports.find(
            report =>
              report.namespace === namespace &&
              report.model === model &&
              report.design === design &&
              report.slug === slug
          )

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

  getSQL({ commit, getters, state }, { run, payload }) {
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
          commit('setIsLoadingQuery', false)
        } else if (run) {
          commit('setQueryResults', response.data)
          commit('setSQLResults', response.data)
          commit('setIsLoadingQuery', false)
          commit('setSorting', getters.getAttributes())
        } else {
          commit('setSQLResults', response.data)
        }
      })
      .catch(e => {
        commit('setSqlErrorMessage', e)
        commit('setIsLoadingQuery', false)
      })
  },

  loadReport({ state, commit }, report) {
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
      if (!sourceCollection) {
        return
      }

      sourceCollection.forEach(item => {
        item.selected = targetCollection.includes(item.name)
      })
    }

    // toggle the selected items
    setSelected(baseTable.columns, queryPayload.columns)
    setSelected(baseTable.aggregates, queryPayload.aggregates)

    // joins, timeframes, and periods
    joinColumnGroups.forEach(joinGroup => {
      // joins - columns
      const targetJoin = queryPayload.joins.find(j => nameMatcher(j, joinGroup))

      setSelected(joinGroup.columns, targetJoin.columns)
      setSelected(joinGroup.aggregates, targetJoin.aggregates)

      // timeframes
      if (targetJoin.timeframes) {
        setSelected(joinGroup.timeframes, targetJoin.timeframes.map(namer))
        // periods
        joinGroup.timeframes.forEach(timeframe => {
          const targetTimeframe = targetJoin.timeframes.find(tf =>
            nameMatcher(tf, timeframe)
          )

          if (targetTimeframe) {
            setSelected(timeframe.periods, targetTimeframe.periods.map(namer))
          }
        })
      }
    })

    commit('setCurrentReport', report)

    this.dispatch('designs/getSQL', {
      run: true,
      payload: report.queryPayload
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
    dispatch('tryAutoRun')
  },

  runQuery(_, isRun = true) {
    this.dispatch('designs/getSQL', {
      run: isRun
    })
  },

  saveReport({ commit, state }, { name }) {
    const postData = {
      chartType: state.chartType,
      design: state.currentDesign,
      filters: state.filters,
      model: state.currentModel,
      namespace: state.currentNamespace,
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
    dispatch('tryAutoRun')
  },

  toggleColumn({ commit, dispatch }, column) {
    commit('toggleSelected', column)
    dispatch('cleanOrdering', column)
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

  toggleTimeframePeriod({ commit, dispatch }, { timeframe, period }) {
    commit('toggleSelected', period)
    dispatch('cleanOrdering', timeframe)
    dispatch('tryAutoRun')
  },

  updateReport({ commit, state }) {
    commit('updateActiveReport')
    return reportsApi.updateReport(state.activeReport).then(response => {
      commit('resetSaveReportSettings')
      commit('setCurrentReport', response.data)
    })
  },

  updateSaveReportSettings({ commit }, name) {
    commit('setSaveReportSettingsName', name)
  },

  // eslint-disable-next-line no-shadow
  updateSortAttribute({ commit, getters }, queryAttribute) {
    const attribute = getters.getAttributeByQueryAttribute(queryAttribute)
    const matchInAssigned = getters.getOrderableAttributeFromCollectionByAttribute(
      'assigned',
      attribute
    )
    const matchInUnassigned = getters.getOrderableAttributeFromCollectionByAttribute(
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
      orderableAttr => orderableAttr.attribute === attribute
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

  resetQueryResults(state) {
    state.isLastRunResultsEmpty = false
    state.results = []
    state.queryAttributes = []
    state.resultAggregates = []
  },

  resetSaveReportSettings(state) {
    state.saveReportSettings = { name: null }
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
    state.activeReport = report

    state.chartType = report.chartType
    state.filters = report.filters
    state.order = report.order
    state.limit = report.queryPayload.limit
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

  setIsLoadingQuery(state, value) {
    state.isLoadingQuery = value
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

  setReports(state, reports) {
    state.reports = reports
  },

  setSaveReportSettingsName(state, name) {
    state.saveReportSettings.name = name
  },

  setSortableAttributeDirection(_, { orderableAttribute, direction }) {
    orderableAttribute.direction = direction
  },

  setSorting(state, allAttributes) {
    state.queryAttributes.forEach(queryAttribute => {
      const getName = attribute => {
        // Account for timeframes matching
        let period = null
        if (attribute.periods) {
          period = attribute.periods.find(
            period => period.name === queryAttribute.attributeName
          )
        }
        return period ? period.name : attribute.name
      }
      const finder = orderableAttribute =>
        orderableAttribute.attribute.sourceName === queryAttribute.sourceName &&
        getName(orderableAttribute.attribute) === queryAttribute.attributeName

      const accounted = state.order.assigned.concat(state.order.unassigned)
      const isAccountedFor = accounted.find(finder)
      if (!isAccountedFor) {
        const targetAttribute = allAttributes.find(attribute => {
          return (
            attribute.sourceName === queryAttribute.sourceName &&
            getName(attribute) === queryAttribute.attributeName
          )
        })
        state.order.unassigned.push({
          attribute: targetAttribute,
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
