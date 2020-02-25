<script>
import { mapActions, mapGetters, mapMutations, mapState } from 'vuex'
import Vue from 'vue'

import lodash from 'lodash'

import capitalize from '@/filters/capitalize'
import CreateDashboardModal from '@/components/dashboards/CreateDashboardModal'
import DateRangePicker from '@/components/analyze/date-range-picker/DateRangePicker'
import Dropdown from '@/components/generic/Dropdown'
import EmbedShareButton from '@/components/generic/EmbedShareButton'
import LoadingOverlay from '@/components/generic/LoadingOverlay'
import QueryFilters from '@/components/analyze/QueryFilters'
import ResultChart from '@/components/analyze/ResultChart'
import ResultTable from '@/components/analyze/ResultTable'
import TableAttributeButton from '@/components/analyze/TableAttributeButton'
import { QUERY_ATTRIBUTE_TYPES } from '@/api/design'
import utils from '@/utils/utils'

export default {
  name: 'Design',
  filters: {
    capitalize
  },
  components: {
    CreateDashboardModal,
    DateRangePicker,
    Dropdown,
    EmbedShareButton,
    LoadingOverlay,
    QueryFilters,
    ResultChart,
    ResultTable,
    TableAttributeButton
  },
  data() {
    return {
      isCreateDashboardModalOpen: false,
      isInitialized: false
    }
  },
  computed: {
    ...mapState('designs', [
      'activeReport',
      'chartType',
      'currentDesign',
      'currentSQL',
      'design',
      'filterOptions',
      'filters',
      'hasCompletedFirstQueryRun',
      'hasSQLError',
      'isAutoRunQuery',
      'isLoadingQuery',
      'resultAggregates',
      'results',
      'sqlErrorMessage'
    ]),
    ...mapGetters('designs', [
      'currentDesignLabel',
      'currentExtractor',
      'currentModelLabel',
      'getNonDateFiltersCount',
      'formattedSql',
      'getSelectedAttributesCount',
      'getAttributesOfDate',
      'getTableSources',
      'hasChartableResults',
      'hasJoins',
      'hasNonDateFilters',
      'hasResults',
      'resultsCount',
      'showAttributesHeader'
    ]),
    ...mapGetters('orchestration', ['lastUpdatedDate', 'startDate']),
    ...mapState('dashboards', ['dashboards']),
    ...mapState('reports', ['reports', 'saveReportSettings']),

    dataLastUpdatedDate() {
      const date = this.lastUpdatedDate(this.currentExtractor)

      return date ? date : 'Missing data'
    },

    dataStartDate() {
      const startDate = this.startDate(this.currentExtractor)

      return startDate ? startDate : 'Not available'
    },

    getAttributeTypeAggregate() {
      return QUERY_ATTRIBUTE_TYPES.AGGREGATE
    },

    getAttributeTypeColumn() {
      return QUERY_ATTRIBUTE_TYPES.COLUMN
    },

    getAttributeTypeTimeframe() {
      return QUERY_ATTRIBUTE_TYPES.TIMEFRAME
    },

    hasActiveReport() {
      return Object.keys(this.activeReport).length > 0
    },

    isActiveReportInDashboard() {
      return dashboard => dashboard.reportIds.includes(this.activeReport.id)
    },

    isShowLoader() {
      return (
        (this.isAutoRunQuery && !this.hasCompletedFirstQueryRun) ||
        this.isLoadingQuery
      )
    },

    getKey() {
      return utils.key
    },

    limit: {
      get() {
        return this.$store.getters['designs/currentLimit']
      },
      set(value) {
        this.$store.dispatch('designs/limitSet', value)
        this.$store.dispatch('designs/getSQL', { run: false })
      }
    }
  },
  beforeDestroy() {
    this.$store.dispatch('designs/resetDefaults')
  },
  /*
  These beforeRouteEnter|Update lifecycle hooks work in tandem with changeReport()'s route update.
  Both hooks are required (Update for locally sourced route changes & Enter for globally sourced route changes)
  */
  beforeRouteEnter(to, from, next) {
    next(vm => {
      vm.reinitialize()
    })
  },
  /*
  These beforeRouteEnter|Update lifecycle hooks work in tandem with changeReport()'s route update.
  Both hooks are required (Update for locally sourced route changes & Enter for globally sourced route changes)
  */
  beforeRouteUpdate(to, from, next) {
    next()

    // it is crucial to wait after `next` is called so
    // the route parameters are updated.
    this.reinitialize()
  },
  methods: {
    ...mapActions('dashboards', ['getDashboards']),
    ...mapActions('designs', [
      'resetErrorMessage',
      'runQuery',
      'toggleIsAutoRunQuery'
    ]),
    ...mapActions('reports', ['updateSaveReportSettings']),
    ...mapMutations('designs', ['setIsAutoRunQuery']),

    aggregateSelected(aggregate) {
      this.$store.dispatch('designs/toggleAggregate', aggregate)
    },

    changeReport(report) {
      // Let route lifecycle hooks delegate update responsibility
      this.$router.push({ name: 'report', params: report })
    },

    columnSelected(column) {
      this.$store.dispatch('designs/toggleColumn', column)
    },

    goToDashboard(dashboard) {
      this.$router.push({ name: 'dashboard', params: dashboard })
    },

    initializeDesign() {
      this.isInitialized = false

      const { slug, namespace, model, design } = this.$route.params
      const uponDesign = this.$store.dispatch('designs/getDesign', {
        namespace,
        model,
        design,
        slug
      })

      uponDesign.then(() => {
        // conditional attribute preselections
        this.tryPreselect(!slug)

        // validate initialization so UI can display while removing the loading bar
        this.isInitialized = true
      })

      // additional requests to faciliate core click-to-code experience
      this.$store.dispatch('designs/getFilterOptions')
      if (slug) {
        this.getDashboards()
      }
    },

    jumpToDateFilters() {
      utils.scrollToTop()
      /*
        TODO likely refactor to use Ben's recommeded GlobalEvents approach (https://github.com/shentao/vue-global-events#readme)
        In doing so, likely refactor all dropdowns to auto generate their own `ref` so this global event approach can ensure
        only one dropdown is open at a time
      */
      const childComponent = this.$children.find(
        child => child.$refs['date-range-dropdown']
      )
      const dateRangeDropdown = childComponent.$refs['date-range-dropdown']
      dateRangeDropdown.open()
    },

    jumpToFilters() {
      utils.scrollToTop()
      this.$refs['filter-dropdown'].open()
    },

    joinAggregateSelected(join, aggregate) {
      this.$store.dispatch('designs/toggleAggregate', aggregate)
    },

    joinColumnSelected(join, column) {
      this.$store.dispatch('designs/toggleColumn', column)
    },

    joinRowClicked(join) {
      this.$store.dispatch('designs/expandJoinRow', join)
    },

    reinitialize() {
      return this.$store
        .dispatch('designs/resetDefaults')
        .then(this.initializeDesign)
    },

    saveReport() {
      const reportName = this.saveReportSettings.name
      this.$store
        .dispatch('designs/saveReport', this.saveReportSettings)
        .then(() => {
          Vue.toasted.global.success(`Report Saved - ${reportName}`)
        })
        .catch(this.$error.handle)
    },

    setChartType(chartType) {
      this.$store.dispatch('designs/setChartType', chartType)
    },

    setReportName(name) {
      this.updateSaveReportSettings(name)
    },

    tableRowClicked(relatedTable) {
      this.$store.dispatch('designs/expandRow', relatedTable)
    },

    timeframePeriodSelected(timeframe, period) {
      this.$store.dispatch('designs/toggleTimeframePeriod', {
        timeframe,
        period
      })
    },

    timeframeSelected(timeframe) {
      this.$store.dispatch('designs/toggleTimeframe', timeframe)
    },

    toggleActiveReportInDashboard(dashboard) {
      const methodName = this.isActiveReportInDashboard(dashboard)
        ? 'removeReportFromDashboard'
        : 'addReportToDashboard'
      this.$store
        .dispatch(`dashboards/${methodName}`, {
          reportId: this.activeReport.id,
          dashboardId: dashboard.id
        })
        .then(() => {
          Vue.toasted.global.success(
            `${this.activeReport.name} successful saved to ${dashboard.name}.`
          )
        })
        .catch(error => {
          Vue.toasted.global.error(
            `${this.activeReport.name} was not saved to ${
              // eslint-disable-next-line
              dashboard.name
            }. [Error code: ${error.response.data.code}]`
          )
        })
    },

    toggleCreateDashboardModal() {
      this.isCreateDashboardModalOpen = !this.isCreateDashboardModalOpen
    },

    tryPreselect(isNoSlug) {
      let hasDefaultPreselections = false
      let hasRequiredPreselections = false

      // preselect if not loading a report
      if (isNoSlug) {
        hasDefaultPreselections = this.tryPreselectDefaultAttributes()
      }
      // preselect requireds (temporary until calculated and derived attributes are added https://gitlab.com/meltano/meltano/issues/1714)
      hasRequiredPreselections = this.tryPreselectRequiredAttributes()

      const hasPreselections =
        hasDefaultPreselections || hasRequiredPreselections
      if (this.isAutoRunQuery && hasPreselections) {
        this.runQuery()
      }
    },

    tryPreselectDefaultAttributes() {
      const finder = collectionName =>
        this.design.relatedTable[collectionName].find(
          attribute => !attribute.hidden
        )

      const column = finder('columns')
      if (column) {
        this.columnSelected(column)
      }

      const aggregate = finder('aggregates')
      if (aggregate) {
        this.aggregateSelected(aggregate)
      }

      const hasPreselection = column || aggregate
      return hasPreselection
    },

    tryPreselectRequiredAttributes() {
      const baseTableColumns = this.design.relatedTable['columns']
      const joinTableColumns = this.design.joins
        ? this.design.joins.map(join => join.relatedTable['columns'])
        : []
      const allAttributes = lodash.flatten(
        [baseTableColumns].concat(joinTableColumns)
      )
      const requireds = allAttributes.filter(
        attribute => attribute.required && !attribute.hidden
      )
      const hasRequireds = requireds.length > 0

      if (hasRequireds) {
        requireds.forEach(columnAttribute => {
          if (!columnAttribute.selected) {
            this.columnSelected(columnAttribute)
          }
        })
      }
      return hasRequireds
    },

    updateReport() {
      this.$store.dispatch('designs/updateReport').then(() => {
        Vue.toasted.global.success(`Report Updated - ${this.activeReport.name}`)
      })
    }
  }
}
</script>

<template>
  <section>
    <div class="columns is-vcentered v-min-4-5r">
      <div class="column">
        <div class="is-grouped">
          <div
            class="has-text-weight-bold"
            :class="{ 'is-italic': !hasActiveReport }"
          >
            <span>{{
              hasActiveReport ? activeReport.name : 'Untitled Report'
            }}</span>
          </div>
          <div v-if="design.description">{{ design.description }}</div>
          <p class="has-text-grey">Data starting from: {{ dataStartDate }}</p>
        </div>
      </div>

      <div class="column">
        <div class="field is-grouped is-grouped-right">
          <p v-if="getAttributesOfDate.length" class="control">
            <DateRangePicker
              :attributes="getAttributesOfDate"
              :column-filters="filters.columns"
              :table-sources="getTableSources(false)"
            />
          </p>
          <div
            class="control field"
            :class="{ 'has-addons': hasActiveReport }"
            data-test-id="dropdown-save-report"
          >
            <p class="control">
              <button
                v-if="hasActiveReport"
                class="button is-interactive-primary"
                :disabled="!hasChartableResults"
                @click="updateReport()"
              >
                <span>Save Report</span>
              </button>
            </p>
            <p class="control">
              <Dropdown
                :disabled="!hasChartableResults"
                :label="hasActiveReport ? '' : 'Save Report'"
                button-classes="is-interactive-primary"
                is-right-aligned
                @dropdown:open="setReportName(`report-${new Date().getTime()}`)"
              >
                <div class="dropdown-content">
                  <div class="dropdown-item">
                    <div class="field">
                      <label class="label"
                        >Save {{ hasActiveReport ? 'as' : '' }}</label
                      >
                      <div class="control">
                        <input
                          :value="saveReportSettings.name"
                          class="input"
                          type="text"
                          placeholder="Name your report"
                          @input="setReportName($event.target.value)"
                        />
                      </div>
                    </div>
                    <div class="buttons is-right">
                      <button class="button is-text" data-dropdown-auto-close>
                        Cancel
                      </button>
                      <button
                        data-test-id="button-save-report"
                        class="button"
                        :disabled="!saveReportSettings.name"
                        data-dropdown-auto-close
                        @click="saveReport"
                      >
                        Save
                      </button>
                    </div>
                  </div>
                  <template v-if="reports.length">
                    <hr class="dropdown-divider" />
                    <div class="dropdown-item">
                      <div class="field">
                        <label class="label">Load Report</label>
                      </div>
                    </div>
                    <a
                      v-for="report in reports"
                      :key="report.name"
                      :class="{
                        'is-active': activeReport.id === report.id
                      }"
                      class="dropdown-item"
                      data-dropdown-auto-close
                      @click="changeReport(report)"
                    >
                      {{ report.name }}
                    </a>
                  </template>
                </div>
              </Dropdown>
            </p>
          </div>
        </div>
        <div class="field is-grouped is-grouped-right">
          <p
            class="control"
            data-test-id="dropdown-add-to-dashboard"
            @click="getDashboards"
          >
            <Dropdown
              label="Add to Dashboard"
              :disabled="!hasChartableResults || !hasActiveReport"
              button-classes="is-small"
              is-right-aligned
            >
              <div class="dropdown-content">
                <a
                  data-test-id="button-new-dashboard"
                  class="dropdown-item"
                  data-dropdown-auto-close
                  @click="toggleCreateDashboardModal()"
                >
                  Create Dashboard
                </a>

                <template v-if="dashboards.length">
                  <hr class="dropdown-divider" />
                  <div
                    v-for="dashboard in dashboards"
                    :key="dashboard.id"
                    class="dropdown-item"
                  >
                    <div class="h-space-between">
                      <label
                        class="h-space-between-primary has-cursor-pointer is-unselectable"
                        for="'checkbox-' + dashboard.id"
                        @click.stop="toggleActiveReportInDashboard(dashboard)"
                      >
                        <input
                          :id="'checkbox-' + dashboard.id"
                          type="checkbox"
                          :checked="isActiveReportInDashboard(dashboard)"
                        />
                        {{ dashboard.name }}
                      </label>
                      <button
                        class="button is-small tooltip is-tooltip-right"
                        :data-tooltip="`Go to ${dashboard.name}`"
                        @click="goToDashboard(dashboard)"
                      >
                        <span class="icon is-small">
                          <font-awesome-icon
                            icon="th-large"
                          ></font-awesome-icon>
                        </span>
                      </button>
                    </div>
                  </div>
                </template>
              </div>
            </Dropdown>
          </p>

          <div class="control">
            <EmbedShareButton
              button-classes="is-small"
              :is-disabled="!hasActiveReport"
              :resource="activeReport"
              resource-type="report"
            />
          </div>
        </div>
      </div>
    </div>

    <div class="columns">
      <aside class="column is-one-quarter">
        <div class="box">
          <div class="level is-flex-wrap">
            <div class="level-left">
              <h2 class="title is-5">Query</h2>
            </div>
            <div class="level-right">
              <div class="level-item field is-grouped">
                <div class="control">
                  <Dropdown
                    class="tooltip"
                    data-tooltip="Show generated SQL query"
                    label="SQL"
                    button-classes="button is-text is-small"
                    :disabled="!currentSQL"
                  >
                    <div class="dropdown-content">
                      <div class="level">
                        <div class="level-item">
                          <textarea
                            v-model="formattedSql"
                            class="has-text-grey-dark is-size-7 is-family-code is-borderless"
                            readonly
                            rows="20"
                            @focus="$event.target.select()"
                          >
                          </textarea>
                        </div>
                      </div>
                    </div>
                  </Dropdown>
                </div>

                <div class="control">
                  <div class="field has-addons">
                    <div class="control">
                      <button
                        data-test-id="run-query-button"
                        class="button is-success"
                        :class="{
                          'is-loading': isLoadingQuery
                        }"
                        :disabled="!currentSQL || isLoadingQuery"
                        @click="runQuery"
                      >
                        Run
                      </button>
                    </div>
                    <div class="control">
                      <button
                        class="button tooltip"
                        :data-tooltip="
                          `Toggle autorun queries ${
                            isAutoRunQuery ? 'off' : 'on'
                          }`
                        "
                        :class="{
                          'has-text-grey-light': !isAutoRunQuery,
                          'is-active has-text-interactive-primary': isAutoRunQuery
                        }"
                        :disabled="!currentSQL || isLoadingQuery"
                        @click="toggleIsAutoRunQuery"
                      >
                        <span class="icon is-small is-size-7">
                          <font-awesome-icon icon="sync"></font-awesome-icon>
                        </span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <template v-if="isInitialized">
            <div class="columns is-vcentered">
              <div class="column">
                <div class="field">
                  <label class="label">Limit</label>
                  <div class="control is-expanded">
                    <input
                      v-model="limit"
                      class="input is-small has-text-interactive-secondary"
                      type="text"
                      placeholder="Limit"
                      @focus="$event.target.select()"
                    />
                  </div>
                </div>
              </div>
              <div class="column">
                <div class="field">
                  <label class="label">
                    <span>Filters</span>
                    <span
                      v-if="hasNonDateFilters"
                      class="has-text-weight-light has-text-grey-light is-size-7"
                      >({{ getNonDateFiltersCount }})</span
                    >
                  </label>
                  <div class="control is-expanded">
                    <Dropdown
                      ref="filter-dropdown"
                      :label="hasNonDateFilters ? 'Edit' : 'None'"
                      :button-classes="
                        `is-small ${
                          hasNonDateFilters
                            ? 'has-text-interactive-secondary'
                            : ''
                        }`
                      "
                      :menu-classes="'dropdown-menu-600'"
                      is-full-width
                    >
                      <div class="dropdown-content">
                        <div class="dropdown-item">
                          <QueryFilters></QueryFilters>
                        </div>
                      </div>
                    </Dropdown>
                  </div>
                </div>
              </div>
            </div>

            <div class="field">
              <label class="label">
                <span>Attributes</span>
                <span
                  v-if="getSelectedAttributesCount > 0"
                  class="has-text-weight-light has-text-grey-light is-size-7"
                  >({{ getSelectedAttributesCount }})</span
                >
              </label>
            </div>

            <div class="is-relative">
              <LoadingOverlay
                :is-loading="isAutoRunQuery && !hasCompletedFirstQueryRun"
              ></LoadingOverlay>

              <nav class="panel is-size-7	is-unselectable">
                <!-- Base table first followed by join tables -->
                <template>
                  <a
                    class="panel-block
                  table-heading
                  is-expandable"
                    :class="{ 'is-collapsed': design.relatedTable.collapsed }"
                    @click="tableRowClicked(design.relatedTable)"
                  >
                    <span class="icon is-small">
                      <font-awesome-icon
                        :icon="
                          design.relatedTable.collapsed ? 'caret-down' : 'table'
                        "
                      ></font-awesome-icon>
                    </span>
                    <span class="has-text-weight-bold">
                      {{ design.label }}
                    </span>
                  </a>
                </template>
                <template v-if="!design.relatedTable.collapsed">
                  <a
                    v-if="showAttributesHeader(design.relatedTable.columns)"
                    class="panel-block
                    attribute-heading
                    has-text-weight-semibold
                    has-background-white"
                  >
                    Columns
                  </a>
                  <template v-for="column in design.relatedTable.columns">
                    <TableAttributeButton
                      v-if="!column.hidden"
                      :key="
                        getKey(
                          design.relatedTable,
                          getAttributeTypeColumn,
                          column
                        )
                      "
                      :data-test-id="`column-${column.label}`.toLowerCase()"
                      :attribute="column"
                      :attribute-type="getAttributeTypeColumn"
                      :design="design"
                      :is-disabled="Boolean(column.required)"
                      @attribute-selected="columnSelected(column)"
                      @calendar-click="jumpToDateFilters"
                      @filter-click="jumpToFilters"
                    />
                  </template>
                  <!-- eslint-disable-next-line vue/require-v-for-key -->
                  <a
                    v-if="showAttributesHeader(design.relatedTable.timeframes)"
                    class="panel-block
                         attribute-heading
                         has-text-weight-semibold
                         has-background-white"
                  >
                    Timeframes
                  </a>
                  <template v-for="timeframe in design.relatedTable.timeframes">
                    <TableAttributeButton
                      v-if="!timeframe.hidden"
                      :key="
                        getKey(
                          design.relatedTable,
                          getAttributeTypeTimeframe,
                          timeframe
                        )
                      "
                      :attribute="timeframe"
                      :attribute-type="getAttributeTypeTimeframe"
                      :design="design"
                      @attribute-selected="timeframeSelected(timeframe)"
                    />
                    <template v-for="period in timeframe.periods">
                      <a
                        v-if="timeframe.selected"
                        :key="period.label"
                        class="panel-block indented"
                        :class="{ 'is-active': period.selected }"
                        @click="timeframePeriodSelected(timeframe, period)"
                      >
                        {{ period.label }}
                      </a>
                    </template>
                  </template>
                  <!-- eslint-disable-next-line vue/require-v-for-key -->
                  <a
                    v-if="showAttributesHeader(design.relatedTable.aggregates)"
                    class="panel-block
                    attribute-heading
                    has-text-weight-semibold
                    has-background-white"
                  >
                    Aggregates
                  </a>
                  <template v-for="aggregate in design.relatedTable.aggregates">
                    <TableAttributeButton
                      v-if="!aggregate.hidden"
                      :key="
                        getKey(
                          design.relatedTable,
                          getAttributeTypeAggregate,
                          aggregate
                        )
                      "
                      :data-test-id="
                        `aggregate-${aggregate.label}`.toLowerCase()
                      "
                      :attribute="aggregate"
                      :attribute-type="getAttributeTypeAggregate"
                      :design="design"
                      @attribute-selected="aggregateSelected(aggregate)"
                      @filter-click="jumpToFilters"
                    />
                  </template>
                </template>

                <!-- Join table(s) second, preceded by the base table -->
                <!-- no v-ifs with v-fors https://vuejs.org/v2/guide/conditional.html#v-if-with-v-for -->
                <template v-if="hasJoins">
                  <template v-for="join in design.joins">
                    <a
                      :key="getKey(join.relatedTable)"
                      class="panel-block
                      table-heading
                      analyze-join-table
                      is-expandable"
                      :class="{ 'is-collapsed': join.collapsed }"
                      @click="joinRowClicked(join)"
                    >
                      <span class="icon is-small">
                        <font-awesome-icon
                          :icon="join.collapsed ? 'caret-down' : 'table'"
                        ></font-awesome-icon>
                      </span>
                      <span class="has-text-weight-bold">
                        {{ join.label }}
                      </span>
                    </a>
                    <template v-if="!join.collapsed">
                      <!-- eslint-disable-next-line vue/require-v-for-key -->
                      <a
                        v-if="showAttributesHeader(join.relatedTable.columns)"
                        class="panel-block
                      attribute-heading
                      has-text-weight-semibold
                      has-background-white"
                      >
                        Columns
                      </a>
                      <template v-for="column in join.relatedTable.columns">
                        <TableAttributeButton
                          v-if="!column.hidden"
                          :key="
                            getKey(
                              join.relatedTable,
                              getAttributeTypeColumn,
                              column
                            )
                          "
                          :data-test-id="`column-${column.label}`.toLowerCase()"
                          :attribute="column"
                          :attribute-type="getAttributeTypeColumn"
                          :design="join"
                          :is-disabled="Boolean(column.required)"
                          @attribute-selected="joinColumnSelected(join, column)"
                          @calendar-click="jumpToDateFilters"
                          @filter-click="jumpToFilters"
                        />
                      </template>

                      <!-- eslint-disable-next-line vue/require-v-for-key -->
                      <a
                        v-if="
                          showAttributesHeader(join.relatedTable.timeframes)
                        "
                        class="panel-block
                            attribute-heading
                            has-text-weight-semibold
                            has-background-white"
                      >
                        Timeframes
                      </a>
                      <template
                        v-for="timeframe in join.relatedTable.timeframes"
                      >
                        <TableAttributeButton
                          v-if="!timeframe.hidden"
                          :key="
                            getKey(
                              join.relatedTable,
                              getAttributeTypeTimeframe,
                              timeframe
                            )
                          "
                          :attribute="timeframe"
                          :attribute-type="getAttributeTypeTimeframe"
                          :design="join"
                          @attribute-selected="timeframeSelected(timeframe)"
                        />
                        <template v-if="timeframe.selected">
                          <template v-for="period in timeframe.periods">
                            <a
                              :key="
                                getKey(
                                  join.relatedTable,
                                  'timeframe',
                                  timeframe,
                                  'period',
                                  period
                                )
                              "
                              class="panel-block indented"
                              :class="{ 'is-active': period.selected }"
                              @click="
                                timeframePeriodSelected(timeframe, period)
                              "
                            >
                              {{ period.label }}
                            </a>
                          </template>
                        </template>
                      </template>

                      <!-- eslint-disable-next-line vue/require-v-for-key -->
                      <a
                        v-if="
                          showAttributesHeader(join.relatedTable.aggregates)
                        "
                        class="panel-block
                      attribute-heading
                      has-text-weight-semibold
                      has-background-white"
                      >
                        Aggregates
                      </a>
                      <template
                        v-for="aggregate in join.relatedTable.aggregates"
                      >
                        <TableAttributeButton
                          v-if="!aggregate.hidden"
                          :key="
                            getKey(
                              join.relatedTable,
                              getAttributeTypeAggregate,
                              aggregate
                            )
                          "
                          :data-test-id="
                            `aggregate-${aggregate.label}`.toLowerCase()
                          "
                          :attribute="aggregate"
                          :attribute-type="getAttributeTypeAggregate"
                          :design="join"
                          @attribute-selected="
                            joinAggregateSelected(join, aggregate)
                          "
                          @filter-click="jumpToFilters"
                        />
                      </template>
                    </template>
                  </template>
                </template>
              </nav>
            </div>
          </template>
          <progress v-else class="progress is-small is-info"></progress>
        </div>
      </aside>

      <div class="column is-three-quarters">
        <div class="box">
          <div class="columns is-vcentered">
            <div class="column">
              <h2 class="title is-5 mb-05r">
                <span>Results</span>
                <span
                  v-if="resultsCount > 0"
                  class="has-text-weight-light has-text-grey-light is-size-7"
                >
                  ({{ resultsCount }})</span
                >
              </h2>
              <div class="has-text-grey is-size-6">
                Last updated: {{ dataLastUpdatedDate }}
              </div>
            </div>
            <div class="column">
              <div class="field is-grouped is-grouped-right">
                <div class="control buttons has-addons">
                  <button
                    class="button tooltip"
                    data-tooltip="Bar chart"
                    :class="{
                      'has-text-grey-light': chartType !== 'BarChart',
                      'is-active has-text-interactive-secondary':
                        chartType === 'BarChart'
                    }"
                    :disabled="!hasChartableResults"
                    @click.stop="setChartType('BarChart')"
                  >
                    <span class="icon is-small">
                      <font-awesome-icon icon="chart-bar"></font-awesome-icon>
                    </span>
                  </button>
                  <button
                    class="button tooltip"
                    data-tooltip="Line chart"
                    :class="{
                      'has-text-grey-light': chartType !== 'LineChart',
                      'is-active has-text-interactive-secondary':
                        chartType === 'LineChart'
                    }"
                    :disabled="!hasChartableResults"
                    @click.stop="setChartType('LineChart')"
                  >
                    <span class="icon is-small">
                      <font-awesome-icon icon="chart-line"></font-awesome-icon>
                    </span>
                  </button>
                  <button
                    class="button tooltip"
                    data-tooltip="Area chart"
                    :class="{
                      'has-text-grey-light': chartType !== 'AreaChart',
                      'is-active has-text-interactive-secondary':
                        chartType === 'AreaChart'
                    }"
                    :disabled="!hasChartableResults"
                    @click.stop="setChartType('AreaChart')"
                  >
                    <span class="icon is-small">
                      <font-awesome-icon icon="chart-area"></font-awesome-icon>
                    </span>
                  </button>
                  <button
                    class="button tooltip"
                    data-tooltip="Scatter chart"
                    :class="{
                      'has-text-grey-light': chartType !== 'ScatterChart',
                      'is-active has-text-interactive-secondary':
                        chartType === 'ScatterChart'
                    }"
                    :disabled="!hasChartableResults"
                    @click.stop="setChartType('ScatterChart')"
                  >
                    <span class="icon is-small">
                      <font-awesome-icon icon="dot-circle"></font-awesome-icon>
                    </span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <template v-if="isInitialized">
            <!-- SQL error -->
            <div v-if="hasSQLError" class="notification is-danger">
              <button class="delete" @click="resetErrorMessage"></button>
              <ul>
                <li v-for="(error, key) in sqlErrorMessage" :key="key">
                  {{ error }}
                </li>
              </ul>
            </div>

            <div>
              <article
                v-if="
                  hasCompletedFirstQueryRun && !isLoadingQuery && !hasResults
                "
                class="message is-info"
              >
                <div class="message-body">
                  <div class="content">
                    <p>
                      Sometimes a query has no results. When this happens, try
                      one or more of the following:
                    </p>
                    <ul>
                      <li>
                        Change the <strong>Column</strong> and/or
                        <strong>Aggregate</strong> selections in the
                        <em>Attributes</em> panel
                      </li>
                      <li>
                        Add, remove, or update one of the
                        <a
                          class="has-text-underlined"
                          @click.stop="jumpToFilters"
                          ><strong>Filters</strong></a
                        >
                      </li>
                    </ul>
                    <p v-if="!isAutoRunQuery">
                      Then click the <em>Run</em> button.
                    </p>
                  </div>
                </div>
              </article>

              <template v-else>
                <ResultChart :is-loading="isShowLoader"></ResultChart>
                <hr />
                <ResultTable :is-loading="isShowLoader"></ResultTable>
              </template>
            </div>
          </template>
          <progress v-else class="progress is-small is-info"></progress>

          <!-- Create Dashboard Modal -->
          <CreateDashboardModal
            v-if="isCreateDashboardModalOpen"
            :report="activeReport"
            @close="toggleCreateDashboardModal"
          >
          </CreateDashboardModal>
        </div>
      </div>
    </div>
  </section>
</template>

<style lang="scss">
.panel-block {
  position: relative;

  &.analyze-join-table {
    margin-top: 1.5rem;
    border-top: 1px solid $grey-lighter;
  }

  &.attribute-heading {
    cursor: auto;
    padding: 0.25rem 0.75rem;
  }

  &.indented {
    padding-left: 1.5rem;
  }

  &.table-heading {
    padding: 0.75rem 0.5rem;

    .icon {
      margin-right: 0.5rem;
    }
  }
}

// Temporary hack due to Bulma specificity
.title.mb-05r {
  margin-bottom: 0.5rem;
}

textarea {
  width: 400px;
  padding: 8px 16px;
  outline: 0;
  resize: none;
}
</style>
