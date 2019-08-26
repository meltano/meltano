<script>
import { mapState, mapGetters, mapActions } from 'vuex'
import Vue from 'vue'

import capitalize from '@/filters/capitalize'
import Chart from '@/components/analyze/Chart'
import Dropdown from '@/components/generic/Dropdown'
import NewDashboardModal from '@/components/dashboards/NewDashboardModal'
import QueryFilters from '@/components/analyze/QueryFilters'
import ResultTable from '@/components/analyze/ResultTable'
import utils from '@/utils/utils'

export default {
  name: 'Design',
  filters: {
    capitalize
  },
  components: {
    Chart,
    Dropdown,
    NewDashboardModal,
    QueryFilters,
    ResultTable
  },
  data() {
    return {
      isNewDashboardModalOpen: false
    }
  },
  computed: {
    ...mapState('designs', [
      'activeReport',
      'design',
      'currentModel',
      'currentDesign',
      'currentSQL',
      'loadingQuery',
      'saveReportSettings',
      'reports',
      'hasSQLError',
      'sqlErrorMessage',
      'results',
      'resultAggregates',
      'chartType',
      'dialect',
      'filterOptions'
    ]),
    ...mapGetters('designs', [
      'getSelectedAttributesCount',
      'currentModelLabel',
      'currentDesignLabel',
      'hasChartableResults',
      'resultsCount',
      'getChartYAxis',
      'hasJoins',
      'showJoinColumnAggregateHeader',
      'formattedSql',
      'filtersCount',
      'hasFilters',
      'getIsAttributeInFilters'
    ]),
    ...mapState('dashboards', ['dashboards']),
    ...mapState('plugins', ['installedPlugins']),
    ...mapGetters('settings', ['isConnectionDialectSqlite']),

    canToggleTimeframe() {
      return !this.isConnectionDialectSqlite(this.dialect)
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
    },

    dialect: {
      get() {
        return this.$store.getters['designs/getDialect']
      },
      set(value) {
        this.$store.commit('designs/setDialect', value)

        // set the default dialect for unknown designs
        localStorage.setItem('dialect', value)

        // set the connection for this specific design
        localStorage.setItem(
          `dialect:${this.currentModel}:${this.currentDesign}`,
          value
        )
      }
    }
  },
  beforeDestroy() {
    this.$store.dispatch('designs/resetDefaults')
  },
  created() {
    const { slug, model, design } = this.$route.params
    const uponDesign = this.$store.dispatch('designs/getDesign', {
      model,
      design,
      slug
    })
    const uponPlugins = this.$store.dispatch('plugins/getInstalledPlugins')

    Promise.all([uponDesign, uponPlugins]).then(() => {
      const defaultDialect =
        localStorage.getItem(
          `dialect:${this.currentModel}:${this.currentDesign}`
        ) ||
        localStorage.getItem('dialect') ||
        this.installedPlugins.connections[0].name

      // don't use the setter here not to update the user's preferences
      this.$store.commit('designs/setDialect', defaultDialect)
    })

    this.$store.dispatch('designs/getFilterOptions')
  },
  methods: {
    ...mapActions('dashboards', ['getDashboards', 'setDashboard']),
    ...mapActions('designs', ['resetErrorMessage']),

    goToDashboard(dashboard) {
      this.setDashboard(dashboard)
      this.$router.push({ name: 'Dashboards' })
    },

    hasActiveReport() {
      return Object.keys(this.activeReport).length > 0
    },

    toggleActiveReportInDashboard(dashboard) {
      const methodName = this.isActiveReportInDashboard(dashboard)
        ? 'removeReportFromDashboard'
        : 'addReportToDashboard'
      this.$store.dispatch(`dashboards/${methodName}`, {
        reportId: this.activeReport.id,
        dashboardId: dashboard.id
      })
    },

    jumpToFilters() {
      utils.scrollToTop()
      this.$refs['filter-dropdown'].open()
    },

    setChartType(chartType) {
      this.$store.dispatch('designs/setChartType', chartType)
    },

    tableRowClicked(relatedTable) {
      this.$store.dispatch('designs/expandRow', relatedTable)
    },

    joinRowClicked(join) {
      this.$store.dispatch('designs/expandJoinRow', join)
    },

    columnSelected(column) {
      this.$store.dispatch('designs/toggleColumn', column)
      this.$store.dispatch('designs/getSQL', { run: false })
    },

    timeframeSelected(timeframe) {
      if (!this.canToggleTimeframe) {
        return
      }
      this.$store.dispatch('designs/toggleTimeframe', timeframe)
    },

    timeframePeriodSelected(period) {
      this.$store.dispatch('designs/toggleTimeframePeriod', period)
      this.$store.dispatch('designs/getSQL', { run: false })
    },

    aggregateSelected(aggregate) {
      this.$store.dispatch('designs/toggleAggregate', aggregate)
      this.$store.dispatch('designs/getSQL', { run: false })
    },

    joinColumnSelected(join, column) {
      this.$store.dispatch('designs/toggleColumn', column)
      this.$store.dispatch('designs/getSQL', { run: false })
    },

    joinAggregateSelected(join, aggregate) {
      this.$store.dispatch('designs/toggleAggregate', aggregate)
      this.$store.dispatch('designs/getSQL', { run: false })
    },

    runQuery() {
      this.$store.dispatch('designs/getSQL', { run: true })
    },

    loadReport(report) {
      this.$store.dispatch('designs/loadReport', { name: report.name })
    },

    saveReport() {
      const reportName = this.saveReportSettings.name
      this.$store
        .dispatch('designs/saveReport', this.saveReportSettings)
        .then(() => {
          Vue.toasted.global.success(`Report Saved - ${reportName}`)
        })
        .catch(error => {
          Vue.toasted.global.error(error.response.data.code)
        })
    },

    updateReport() {
      this.$store.dispatch('designs/updateReport').then(() => {
        Vue.toasted.global.success(`Report Updated - ${this.activeReport.name}`)
      })
    },

    toggleNewDashboardModal() {
      this.isNewDashboardModalOpen = !this.isNewDashboardModalOpen
    }
  }
}
</script>

<template>
  <section>
    <div class="columns is-vcentered">
      <div class="column is-one-quarter">
        <div class="is-grouped is-pulled-left">
          <div v-if="hasActiveReport()">{{ activeReport.name }}</div>
          <div v-else><em>Untitled Report</em></div>
        </div>
      </div>

      <div class="column">
        <div class="field is-grouped is-pulled-right">
          <p v-if="hasActiveReport()" class="control" @click="getDashboards">
            <Dropdown label="Add to Dashboard" is-right-aligned>
              <div class="dropdown-content">
                <a
                  class="dropdown-item"
                  data-dropdown-auto-close
                  @click="toggleNewDashboardModal()"
                >
                  New Dashboard
                </a>

                <template v-if="dashboards.length">
                  <hr class="dropdown-divider" />
                  <div
                    v-for="dashboard in dashboards"
                    :key="dashboard.id"
                    class="dropdown-item"
                  >
                    <div class="row-space-between">
                      <label
                        class="row-space-between-primary has-cursor-pointer is-unselectable"
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
                        <span class="icon is-small panel-icon">
                          <font-awesome-icon icon="table"></font-awesome-icon>
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
            :class="{ 'has-addons': hasActiveReport() }"
          >
            <p class="control">
              <button
                v-if="hasActiveReport()"
                class="button"
                @click="updateReport()"
              >
                <span>Update Report</span>
              </button>
            </p>
            <p class="control">
              <Dropdown
                :disabled="!hasChartableResults"
                :label="hasActiveReport() ? '' : 'Save Report'"
                is-right-aligned
              >
                <div class="dropdown-content">
                  <div class="dropdown-item">
                    <div class="field">
                      <label v-if="hasActiveReport()" class="label"
                        >Save as</label
                      >
                      <div class="control">
                        <input
                          v-model="saveReportSettings.name"
                          class="input"
                          type="text"
                          placeholder="Name your report"
                        />
                      </div>
                    </div>
                    <div class="buttons is-right">
                      <button
                        class="button is-small is-text"
                        data-dropdown-auto-close
                      >
                        Cancel
                      </button>
                      <button
                        class="button is-small"
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
                  class="dropdown-item"
                  data-dropdown-auto-close
                  @click="loadReport(report)"
                >
                  {{ report.name }}
                </a>
              </div>
            </Dropdown>
          </p>

          <div class="control">
            <div class="select">
              <select v-model="dialect" name="connection">
                <option
                  v-for="connection in installedPlugins.connections"
                  :key="connection.name"
                  >{{ connection.name }}</option
                >
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="columns">
      <aside class="column is-one-quarter">
        <div class="box">
          <div class="columns is-vcentered">
            <div class="column is-two-fifths">
              <h2 class="title is-5">Query</h2>
            </div>
            <div class="column is-three-fifths">
              <div class="buttons is-right">
                <Dropdown
                  label="SQL"
                  button-classes="is-text is-small"
                  :disabled="!currentSQL"
                  is-icon-removed
                >
                  <div class="dropdown-content">
                    <div class="level">
                      <div class="level-item">
                        <code>{{ formattedSql }}</code>
                      </div>
                    </div>
                  </div>
                </Dropdown>
                <button
                  class="button is-success"
                  :class="{ 'is-loading': loadingQuery }"
                  :disabled="!currentSQL"
                  @click="runQuery"
                >
                  Run
                </button>
              </div>
            </div>
          </div>

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

          <nav class="panel is-unselectable">
            <!-- Base table first followed by join tables -->
            <template>
              <a
                class="panel-block
                has-background-white-bis
                has-text-grey
                is-expandable"
                :class="{ 'is-collapsed': design.relatedTable.collapsed }"
                @click="tableRowClicked(design.relatedTable)"
              >
                <span class="icon is-small panel-icon">
                  <font-awesome-icon icon="table"></font-awesome-icon>
                </span>
                {{ design.label }}
              </a>
            </template>
            <template v-if="!design.relatedTable.collapsed">
              <a
                v-if="
                  showJoinColumnAggregateHeader(design.relatedTable.columns)
                "
                class="panel-block
                  panel-block-heading
                  has-background-white"
              >
                Columns
              </a>
              <template v-for="timeframe in design.relatedTable.timeframes">
                <a
                  v-if="!timeframe.relatedView.hidden"
                  :key="timeframe.label"
                  class="panel-block dimension-group"
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
                    @click="timeframePeriodSelected(period)"
                  >
                    {{ period.label }}
                  </a>
                </template>
              </template>
              <template v-for="column in design.relatedTable.columns">
                <a
                  v-if="!column.hidden"
                  :key="column.label"
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
                  showJoinColumnAggregateHeader(design.relatedTable.aggregates)
                "
                class="panel-block
                  panel-block-heading
                  has-background-white"
              >
                Aggregates
              </a>
              <a
                v-for="aggregate in design.relatedTable.aggregates"
                :key="aggregate.label"
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
                    has-background-white-bis
                    has-text-grey
                    is-expandable"
                  :class="{ 'is-collapsed': join.collapsed }"
                  @click="joinRowClicked(join)"
                >
                  <span class="icon is-small panel-icon">
                    <font-awesome-icon icon="table"></font-awesome-icon>
                  </span>
                  {{ join.label }}
                </a>
                <template v-if="!join.collapsed">
                  <!-- eslint-disable-next-line vue/require-v-for-key -->
                  <a
                    v-if="
                      showJoinColumnAggregateHeader(join.relatedTable.columns)
                    "
                    class="panel-block
                    panel-block-heading
                    has-text-weight-light
                    has-background-white"
                  >
                    Columns
                  </a>
                  <template v-for="timeframe in join.relatedTable.timeframes">
                    <a
                      v-if="!timeframe.hidden"
                      :key="timeframe.label"
                      class="panel-block timeframe"
                      :class="{
                        'is-active': timeframe.selected,
                        'is-sqlite-unsupported': isConnectionDialectSqlite(
                          dialect
                        )
                      }"
                      @click="
                        isConnectionDialectSqlite(dialect) ||
                          timeframeSelected(timeframe)
                      "
                    >
                      {{ timeframe.label }}
                      <div
                        v-if="isConnectionDialectSqlite(dialect)"
                        class="sqlite-unsupported-container"
                      >
                        <small>Unsupported by SQLite</small>
                      </div>
                    </a>
                    <template v-if="timeframe.selected">
                      <template v-for="period in timeframe.periods">
                        <a
                          :key="timeframe.label.concat('-', period.label)"
                          class="panel-block indented"
                          :class="{ 'is-active': period.selected }"
                          @click="timeframePeriodSelected(period)"
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
                          <font-awesome-icon icon="filter"></font-awesome-icon>
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
                    panel-block-heading
                    has-background-white"
                  >
                    Aggregates
                  </a>
                  <template v-for="aggregate in join.relatedTable.aggregates">
                    <a
                      v-if="!aggregate.hidden"
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
                          <font-awesome-icon icon="filter"></font-awesome-icon>
                        </span>
                      </button>
                    </a>
                  </template>
                </template>
              </template>
            </template>
          </nav>
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

          <!-- charts tab -->
          <div>
            <div v-if="hasChartableResults" class="chart-toggles">
              <chart
                :chart-type="chartType"
                :results="results"
                :result-aggregates="resultAggregates"
              ></chart>
            </div>
            <div v-if="!hasChartableResults">
              <div class="box is-radiusless is-shadowless has-text-centered">
                <p>
                  Run a query with at least one aggregate selected or load a
                  report
                </p>
              </div>
            </div>
          </div>

          <hr />

          <!-- results/SQL tab -->
          <div>
            <div v-if="hasSQLError" class="notification is-danger">
              <button class="delete" @click="resetErrorMessage"></button>
              <ul>
                <li v-for="(error, key) in sqlErrorMessage" :key="key">
                  {{ error }}
                </li>
              </ul>
            </div>

            <ResultTable></ResultTable>
          </div>

          <!-- New Dashboard Modal -->
          <NewDashboardModal
            v-if="isNewDashboardModalOpen"
            :report="activeReport"
            @close="toggleNewDashboardModal"
          >
          </NewDashboardModal>
        </div>
      </div>
    </div>
  </section>
</template>

<style lang="scss">
.panel-block {
  position: relative;
  &.space-between {
    justify-content: space-between;
  }
  &.indented {
    padding-left: 1.75rem;
  }
  &.panel-block-heading {
    padding: 0.25rem 0.75rem;
    font-size: 0.75rem;
    &:hover {
      background: white;
    }
  }
  &.is-sqlite-unsupported {
    opacity: 0.5;
    cursor: not-allowed;
    .sqlite-unsupported-container {
      display: flex;
      flex-direction: row;
      justify-content: flex-end;
      flex-grow: 1;

      small {
        font-size: 60%;
        font-style: italic;
      }
    }
    &.timeframe {
      &::after {
        display: none;
      }
    }
  }

  &.timeframe {
    &::after {
      border: 3px solid #363636;
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
</style>
