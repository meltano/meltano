<script>
import { mapActions, mapGetters, mapMutations, mapState } from 'vuex'
import Vue from 'vue'

import capitalize from '@/filters/capitalize'
import CreateDashboardModal from '@/components/dashboards/CreateDashboardModal'
import Dropdown from '@/components/generic/Dropdown'
import QueryFilters from '@/components/analyze/QueryFilters'
import ResultChart from '@/components/analyze/ResultChart'
import ResultTable from '@/components/analyze/ResultTable'
import utils from '@/utils/utils'

export default {
  name: 'Design',
  filters: {
    capitalize
  },
  components: {
    CreateDashboardModal,
    Dropdown,
    QueryFilters,
    ResultChart,
    ResultTable
  },
  data() {
    return {
      isInitialized: false,
      isCreateDashboardModalOpen: false
    }
  },
  computed: {
    ...mapState('designs', [
      'activeReport',
      'chartType',
      'currentDesign',
      'currentModel',
      'currentSQL',
      'design',
      'filterOptions',
      'hasSQLError',
      'isAutoRunQuery',
      'isLoadingQuery',
      'reports',
      'resultAggregates',
      'results',
      'saveReportSettings',
      'sqlErrorMessage'
    ]),
    ...mapGetters('designs', [
      'currentDesignLabel',
      'currentModelLabel',
      'filtersCount',
      'formattedSql',
      'getIsAttributeInFilters',
      'getSelectedAttributesCount',
      'hasChartableResults',
      'hasFilters',
      'hasJoins',
      'hasResults',
      'resultsCount',
      'showJoinColumnAggregateHeader'
    ]),
    ...mapState('dashboards', ['dashboards']),

    hasActiveReport() {
      return Object.keys(this.activeReport).length > 0
    },

    isActiveReportInDashboard() {
      return dashboard => dashboard.reportIds.includes(this.activeReport.id)
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
  created() {
    this.initializeSettings()
  },
  methods: {
    ...mapActions('dashboards', ['getDashboards']),
    ...mapActions('designs', [
      'resetErrorMessage',
      'runQuery',
      'toggleIsAutoRunQuery'
    ]),
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
        // preselect if not loading a report
        if (!slug && this.isAutoRunQuery) {
          this.preselectAttributes()
        }

        // validate initialization so UI can display while removing the loading bar
        this.isInitialized = true
      })

      this.$store.dispatch('designs/getFilterOptions')
    },

    initializeSettings() {
      if ('isAutoRunQuery' in localStorage) {
        this.setIsAutoRunQuery(
          localStorage.getItem('isAutoRunQuery') === 'true'
        )
      }
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

    preselectAttributes() {
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
        this.columnSelected(aggregate)
      }

      if (column || aggregate) {
        this.runQuery()
      }
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
      this.$store.dispatch('designs/updateSaveReportSettings', name)
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
              dashboard.name
            }. [Error code: ${error.response.data.code}]`
          )
        })
    },

    toggleCreateDashboardModal() {
      this.isCreateDashboardModalOpen = !this.isCreateDashboardModalOpen
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
        <div class="is-grouped is-pulled-left">
          <div
            class="has-text-weight-bold"
            :class="{ 'is-italic': !hasActiveReport }"
          >
            <span>{{
              hasActiveReport ? activeReport.name : 'Untitled Report'
            }}</span>
          </div>
          <div v-if="design.description">{{ design.description }}</div>
        </div>
      </div>

      <div class="column">
        <div class="field is-grouped is-pulled-right">
          <p
            v-if="hasActiveReport"
            class="control"
            data-test-id="dropdown-add-to-dashboard"
            @click="getDashboards"
          >
            <Dropdown label="Add to Dashboard" is-right-aligned>
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

          <div
            class="control field"
            :class="{ 'has-addons': hasActiveReport }"
            data-test-id="dropdown-save-report"
          >
            <p class="control">
              <button
                v-if="hasActiveReport"
                class="button"
                @click="updateReport()"
              >
                <span>Save Report</span>
              </button>
            </p>
            <p class="control">
              <Dropdown
                :disabled="!hasChartableResults"
                :label="hasActiveReport ? '' : 'Save Report'"
                is-right-aligned
                @dropdown:open="setReportName(`report-${new Date().getTime()}`)"
              >
                <div class="dropdown-content">
                  <div class="dropdown-item">
                    <div class="field">
                      <label v-if="hasActiveReport" class="label"
                        >Save as</label
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
                </div>
              </Dropdown>
            </p>
          </div>

          <p class="control">
            <Dropdown
              :disabled="!reports.length"
              label="Reports"
              is-right-aligned
            >
              <div class="dropdown-content">
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
              </div>
            </Dropdown>
          </p>
        </div>
      </div>
    </div>

    <div class="columns">
      <aside class="column is-one-quarter">
        <div class="box">
          <div class="level">
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
                        :class="{ 'is-loading': isLoadingQuery }"
                        :disabled="!currentSQL"
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
                        :disabled="!currentSQL"
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
                      v-if="filtersCount > 0"
                      class="has-text-weight-light has-text-grey-light is-size-7"
                      >({{ filtersCount }})</span
                    >
                  </label>
                  <div class="control is-expanded">
                    <Dropdown
                      ref="filter-dropdown"
                      :label="hasFilters ? 'Edit' : 'None'"
                      :button-classes="
                        `is-small ${
                          hasFilters ? 'has-text-interactive-secondary' : ''
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
                  v-if="
                    showJoinColumnAggregateHeader(design.relatedTable.columns)
                  "
                  class="panel-block
                    attribute-heading
                    has-text-weight-semibold
                    has-background-white"
                >
                  Columns
                </a>
                <template v-for="timeframe in design.relatedTable.timeframes">
                  <a
                    :key="timeframe.label"
                    class="panel-block timeframe"
                    :class="{ 'is-active': timeframe.selected }"
                    @click="timeframeSelected(timeframe)"
                  >
                    {{ timeframe.label }}
                  </a>
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
                <template v-for="column in design.relatedTable.columns">
                  <a
                    v-if="!column.hidden"
                    :key="column.label"
                    :data-test-id="`column-${column.label}`.toLowerCase()"
                    class="panel-block space-between has-text-weight-medium"
                    :class="{ 'is-active': column.selected }"
                    @click="columnSelected(column)"
                  >
                    {{ column.label }}
                    <button
                      v-if="
                        getIsAttributeInFilters(
                          design.name,
                          column.name,
                          'column'
                        )
                      "
                      class="button is-small"
                      @click.stop="jumpToFilters"
                    >
                      <span class="icon has-text-interactive-secondary">
                        <font-awesome-icon icon="filter"></font-awesome-icon>
                      </span>
                    </button>
                  </a>
                </template>
                <!-- eslint-disable-next-line vue/require-v-for-key -->
                <a
                  v-if="
                    showJoinColumnAggregateHeader(
                      design.relatedTable.aggregates
                    )
                  "
                  class="panel-block
                    attribute-heading
                    has-text-weight-semibold
                    has-background-white"
                >
                  Aggregates
                </a>
                <a
                  v-for="aggregate in design.relatedTable.aggregates"
                  :key="aggregate.label"
                  :data-test-id="`aggregate-${aggregate.label}`.toLowerCase()"
                  class="panel-block space-between has-text-weight-medium"
                  :class="{ 'is-active': aggregate.selected }"
                  @click="aggregateSelected(aggregate)"
                >
                  {{ aggregate.label }}
                  <button
                    v-if="
                      getIsAttributeInFilters(
                        design.name,
                        aggregate.name,
                        'aggregate'
                      )
                    "
                    class="button is-small"
                    @click.stop="jumpToFilters"
                  >
                    <span class="icon has-text-interactive-secondary">
                      <font-awesome-icon icon="filter"></font-awesome-icon>
                    </span>
                  </button>
                </a>
              </template>

              <!-- Join table(s) second, preceded by the base table -->
              <!-- no v-ifs with v-fors https://vuejs.org/v2/guide/conditional.html#v-if-with-v-for -->
              <template v-if="hasJoins">
                <template v-for="join in design.joins">
                  <a
                    :key="join.label"
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
                      v-if="
                        showJoinColumnAggregateHeader(join.relatedTable.columns)
                      "
                      class="panel-block
                      attribute-heading
                      has-text-weight-semibold
                      has-background-white"
                    >
                      Columns
                    </a>
                    <template v-for="timeframe in join.relatedTable.timeframes">
                      <a
                        :key="timeframe.label"
                        class="panel-block timeframe"
                        :class="{
                          'is-active': timeframe.selected
                        }"
                        @click="timeframeSelected(timeframe)"
                      >
                        {{ timeframe.label }}
                      </a>
                      <template v-if="timeframe.selected">
                        <template v-for="period in timeframe.periods">
                          <a
                            :key="timeframe.label.concat('-', period.label)"
                            class="panel-block indented"
                            :class="{ 'is-active': period.selected }"
                            @click="timeframePeriodSelected(timeframe, period)"
                          >
                            {{ period.label }}
                          </a>
                        </template>
                      </template>
                    </template>
                    <template v-for="column in join.relatedTable.columns">
                      <a
                        v-if="!column.hidden"
                        :key="column.label"
                        class="panel-block space-between has-text-weight-medium"
                        :class="{ 'is-active': column.selected }"
                        @click="joinColumnSelected(join, column)"
                      >
                        {{ column.label }}
                        <button
                          v-if="
                            getIsAttributeInFilters(
                              join.name,
                              column.name,
                              'column'
                            )
                          "
                          class="button is-small"
                          @click.stop="jumpToFilters"
                        >
                          <span class="icon has-text-interactive-secondary">
                            <font-awesome-icon
                              icon="filter"
                            ></font-awesome-icon>
                          </span>
                        </button>
                      </a>
                    </template>
                    <!-- eslint-disable-next-line vue/require-v-for-key -->
                    <a
                      v-if="
                        showJoinColumnAggregateHeader(
                          join.relatedTable.aggregates
                        )
                      "
                      class="panel-block
                      attribute-heading
                      has-text-weight-semibold
                      has-background-white"
                    >
                      Aggregates
                    </a>
                    <template v-for="aggregate in join.relatedTable.aggregates">
                      <a
                        :key="aggregate.label"
                        class="panel-block space-between has-text-weight-medium"
                        :class="{ 'is-active': aggregate.selected }"
                        @click="joinAggregateSelected(join, aggregate)"
                      >
                        {{ aggregate.label }}
                        <button
                          v-if="
                            getIsAttributeInFilters(
                              join.name,
                              aggregate.name,
                              'aggregate'
                            )
                          "
                          class="button is-small"
                          @click.stop="jumpToFilters"
                        >
                          <span class="icon has-text-interactive-secondary">
                            <font-awesome-icon
                              icon="filter"
                            ></font-awesome-icon>
                          </span>
                        </button>
                      </a>
                    </template>
                  </template>
                </template>
              </template>
            </nav>
          </template>
          <progress v-else class="progress is-small is-info"></progress>
        </div>
      </aside>

      <div class="column is-three-quarters">
        <div class="box">
          <div class="columns is-vcentered">
            <div class="column">
              <h2 class="title is-5">
                <span>Results</span>
                <span
                  v-if="resultsCount > 0"
                  class="has-text-weight-light has-text-grey-light is-size-7"
                  >({{ resultsCount }})</span
                >
              </h2>
            </div>
            <div class="column">
              <div class="buttons has-addons is-right">
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
                v-if="!isLoadingQuery && !hasResults"
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
                <ResultChart :is-loading="isLoadingQuery"></ResultChart>
                <hr />
                <ResultTable :is-loading="isLoadingQuery"></ResultTable>
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

  &.space-between {
    justify-content: space-between;
  }

  &.indented {
    padding-left: 1.5rem;
  }

  &.attribute-heading {
    cursor: auto;
    padding: 0.25rem 0.75rem;
  }

  &.table-heading {
    padding: 0.75rem 0.5rem;

    .icon {
      margin-right: 0.5rem;
    }
  }

  &.timeframe {
    &::after {
      border: 3px solid $grey-darker;
      border-radius: 2px;
      border-right: 0;
      border-top: 0;
      content: ' ';
      display: block;
      height: 0.625em;
      margin-top: -0.321em;
      pointer-events: none;
      position: absolute;
      top: 50%;
      -webkit-transform: rotate(-134deg);
      transform: rotate(-134deg);
      -webkit-transform-origin: center;
      transform-origin: center;
      width: 0.625em;
      right: 7%;
    }
    &.is-active {
      &::after {
        margin-top: -0.4375em;
        -webkit-transform: rotate(-45deg);
        transform: rotate(-45deg);
      }
    }
  }
}

textarea {
  width: 400px;
  padding: 8px 16px;
  outline: 0;
  resize: none;
}
</style>
