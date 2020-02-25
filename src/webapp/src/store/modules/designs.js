import Vue from 'vue'

import lodash from 'lodash'
import sqlFormatter from 'sql-formatter'
import SSF from 'ssf'

import designApi from '@/api/design'
import FilterModel from '@/store/models/FilterModel'
import sqlApi from '@/api/sql'
import utils from '@/utils/utils'
import { QUERY_ATTRIBUTE_DATA_TYPES } from '@/api/design'
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

  getAttributesOfDate(_, getters) {
    return getters.getAttributes(['columns']).filter(attribute => {
      return (
        attribute.type === QUERY_ATTRIBUTE_DATA_TYPES.DATE ||
        QUERY_ATTRIBUTE_DATA_TYPES.TIME
      )
    })
  },

  getOrderableAttributesIndex(state, getters) {
    const attributes = getters.getAttributes()

    let attributesIndex = {}
    attributes.forEach(attribute => {
      if (
        !getters.getIsOrderableAttribute({ attributeClass: attribute.class })
      ) {
        return
      }

      attributesIndex[
        helpers.buildKey(attribute.sourceName, attribute.name)
      ] = attribute
    })

    return attributesIndex
  },

  getAttributeByQueryAttribute(_, getters) {
    return queryAttribute => {
      const finder = attr =>
        attr.sourceName === queryAttribute.sourceName &&
        attr.name == queryAttribute.attributeName &&
        attr.class === queryAttribute.attributeClass
      return getters.getAttributes().find(finder)
    }
  },

  getFilters(_, getters) {
    return (sourceName, name, filterType) =>
      getters
        .getFiltersByType(filterType)
        .filter(
          filter => filter.name === name && filter.sourceName === sourceName
        )
  },

  getTableSources(state) {
    return isIncludeAttributesOfDate => {
      const sources = []
      const design = state.design
      let attributeFilter
      if (isIncludeAttributesOfDate) {
        attributeFilter = attr => !attr.hidden
      } else {
        attributeFilter = attr =>
          !attr.hidden &&
          (attr.type !== QUERY_ATTRIBUTE_DATA_TYPES.DATE ||
            attr.type !== QUERY_ATTRIBUTE_DATA_TYPES.TIME)
      }

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
    }
  },

  getFiltersByType(state) {
    return filterType =>
      state.filters[helpers.getFilterTypePlural(filterType)] || []
  },

  getFormattedValue: () => (fmt, value) => SSF.format(fmt, Number(value)),

  getIsAttributeInFilters(_, getters) {
    return (sourceName, name, filterType) =>
      getters.getFilters(sourceName, name, filterType).length > 0
  },

  // Timeframes are not sortable
  // https://gitlab.com/meltano/meltano/issues/1188
  getIsOrderableAttribute() {
    return queryAttribute => queryAttribute.attributeClass != 'timeframes'
  },

  getIsOrderableAttributeAscending() {
    return orderableAttribute => orderableAttribute.direction === 'asc'
  },

  getNonDateFiltersCount(_, getters) {
    return getters.getNonDateFlattenedFilters.length
  },

  getNonDateFlattenedFilters(state, getters) {
    const nonDateFilterColumns = state.filters.columns.filter(
      filter =>
        !getters.getAttributesOfDate.find(
          attribute =>
            filter.sourceName === attribute.sourceName &&
            filter.name === attribute.name
        )
    )
    return lodash.sortBy(
      nonDateFilterColumns.concat(state.filters.aggregates),
      'name'
    )
  },

  getOrderableAttributeFromCollectionByAttribute(state) {
    return (orderCollection, attribute) => {
      const finder = orderableAttribute => {
        return orderableAttribute.attribute === attribute
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
  addFilter({ commit }, payload) {
    const filter = new FilterModel(payload)
    commit('addFilter', filter)

    // Aggregates must be selected if they're used as a filter target where columns do not
    const isValidToggleSelection =
      !filter.attribute.hasOwnProperty('selected') || !filter.attribute.selected
    if (filter.filterType === 'aggregate' && isValidToggleSelection) {
      commit('toggleSelected', filter.attribute)
    }
  },

  cleanFiltering({ commit, getters }, { attribute, type }) {
    if (!attribute.selected) {
      const filters = getters.getFilters(
        attribute.sourceName,
        attribute.name,
        type
      )
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

    const uponLoadReports = dispatch('reports/loadReports', null, {
      root: true
    })

    return designApi
      .index(namespace, model, design)
      .then(response => {
        commit('setDesign', response.data)
      })
      .then(uponLoadReports)
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
        } else if (run) {
          commit('setHasCompletedFirstQueryRun', true)
          commit('setQueryResults', response.data)
          commit('setSQLResults', response.data)
          commit('setSorting', {
            attributesIndex: getters.getOrderableAttributesIndex
          })
        } else {
          commit('setSQLResults', response.data)
        }
      })
      .catch(e => {
        commit('setSqlErrorMessage', e)
      })
      .finally(() => commit('setIsLoadingQuery', false))
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

  saveReport({ commit, dispatch, rootGetters, state }, { name }) {
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
    dispatch('cleanFiltering', { attribute: aggregate, type: 'aggregate' })
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

  updateFilter({ commit }, payload) {
    commit('updateFilter', payload)
  },

  updateReport({ commit, dispatch, rootGetters, state }) {
    commit('updateActiveReport')
    return dispatch('reports/updateReport', state.activeReport, {
      root: true
    }).then(response => {
      const report = rootGetters['reports/getReportById'](response.data.id)
      commit('setCurrentReport', report)
    })
  },

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

  assignSortableAttribute(state, attribute) {
    const orderableAttribute = state.order.unassigned.find(
      orderableAttr => orderableAttr.attribute === attribute
    )
    const idx = state.order.unassigned.indexOf(orderableAttribute)
    Vue.delete(state.order.unassigned, idx)
    state.order.assigned.push(orderableAttribute)
  },

  removeFilter(state, filter) {
    if (filter) {
      const filtersByType =
        state.filters[helpers.getFilterTypePlural(filter.filterType)]
      const idx = filtersByType.indexOf(filter)
      Vue.delete(filtersByType, idx)
    }
  },

  removeOrder(_, { collection, queryAttribute }) {
    const idx = collection.indexOf(queryAttribute)
    Vue.delete(collection, idx)
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
            attribute.class = attributeType
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

  setSorting(state, { attributesIndex }) {
    state.queryAttributes.forEach(queryAttribute => {
      const attribute =
        attributesIndex[
          helpers.buildKey(
            queryAttribute.sourceName,
            queryAttribute.attributeName
          )
        ]

      // the index only contains attributes that are Orderable
      if (!attribute) {
        return
      }

      const finder = orderableAttribute =>
        orderableAttribute.attribute === attribute

      const accounted = state.order.assigned.concat(state.order.unassigned)
      const isAccountedFor = lodash.some(accounted, finder)

      if (!isAccountedFor) {
        state.order.unassigned.push({
          attribute,
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
  },

  updateFilter(state, { filter, value }) {
    if (filter) {
      filter.value = value
    }
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
