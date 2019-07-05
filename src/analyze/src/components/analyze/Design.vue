<script>
import { mapState, mapGetters, mapActions } from 'vuex';
import capitalize from '@/filters/capitalize';
import Chart from '@/components/analyze/Chart';
import Dropdown from '@/components/generic/Dropdown';
import NewDashboardModal from '@/components/dashboards/NewDashboardModal';
import QueryFilters from '@/components/analyze/QueryFilters';
import ResultTable from '@/components/analyze/ResultTable';
import utils from '@/utils/utils';

export default {
  name: 'Design',
  data() {
    return {
      isNewDashboardModalOpen: false,
    };
  },
  created() {
    const { slug, model, design } = this.$route.params;
    this.$store.dispatch('designs/getDesign', { model, design, slug });
    this.$store.dispatch('plugins/getInstalledPlugins')
      .then(() => {
        this.dialect = this.installedPlugins.connections[0].name;
      });
    this.$store.dispatch('designs/getFilterOptions');
  },
  filters: {
    capitalize,
  },
  components: {
    Chart,
    Dropdown,
    NewDashboardModal,
    QueryFilters,
    ResultTable,
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
      'filterOptions',
    ]),
    ...mapGetters('designs', [
      'attributesCount',
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
      'getIsAttributeInFilters',
    ]),
    ...mapState('dashboards', [
      'dashboards',
    ]),
    ...mapState('plugins', [
      'installedPlugins',
    ]),
    ...mapGetters('settings', [
      'isConnectionDialectSqlite',
    ]),

    canToggleTimeframe() {
      return !this.isConnectionDialectSqlite(this.dialect);
    },

    limit: {
      get() {
        return this.$store.getters['designs/currentLimit'];
      },
      set(value) {
        this.$store.dispatch('designs/limitSet', value);
        this.$store.dispatch('designs/getSQL', { run: false });
      },
    },

    dialect: {
      get() {
        return this.$store.getters['designs/getDialect'];
      },
      set(value) {
        this.$store.commit('designs/setDialect', value);
      },
    },
  },
  methods: {
    ...mapActions('dashboards', [
      'getDashboards',
    ]),
<<<<<<< HEAD
    ...mapActions('designs', [
<<<<<<< HEAD
      'resetErrorMessage',
=======
      'toggleFilter',
>>>>>>> 8270e9dc... initial filter add functionality, still need to toggle vs naive add
    ]),
=======
>>>>>>> 783d062a... initial toggle/add/remove filter functionality implemented

    isActiveReportInDashboard(dashboard) {
      return dashboard.reportIds.includes(this.activeReport.id);
    },

    hasActiveReport() {
      return Object.keys(this.activeReport).length > 0;
    },

    toggleActiveReportInDashboard(dashboard) {
      const methodName = this.isActiveReportInDashboard(dashboard)
        ? 'removeReportFromDashboard'
        : 'addReportToDashboard';
      this.$store.dispatch(`dashboards/${methodName}`, {
        reportId: this.activeReport.id,
        dashboardId: dashboard.id,
      });
    },

    jumpToFilters() {
      utils.scrollToTop();
      this.$refs['filter-dropdown'].open();
    },

    setChartType(chartType) {
      this.$store.dispatch('designs/setChartType', chartType);
    },

    tableRowClicked(relatedTable) {
      this.$store.dispatch('designs/expandRow', relatedTable);
    },

    joinRowClicked(join) {
      this.$store.dispatch('designs/expandJoinRow', join);
    },

    columnSelected(column) {
      this.$store.dispatch('designs/removeSort', column);
      this.$store.dispatch('designs/toggleColumn', column);
      this.$store.dispatch('designs/getSQL', { run: false });
    },

    timeframeSelected(timeframe) {
      if (!this.canToggleTimeframe) {
        return;
      }
      this.$store.dispatch('designs/toggleTimeframe', timeframe);
    },

    timeframePeriodSelected(period) {
      this.$store.dispatch('designs/toggleTimeframePeriod', period);
      this.$store.dispatch('designs/getSQL', { run: false });
    },

    aggregateSelected(aggregate) {
      this.$store.dispatch('designs/toggleAggregate', { aggregate, tableName: this.design.from });
      this.$store.dispatch('designs/getSQL', { run: false });
    },

    joinColumnSelected(join, column) {
      this.$store.dispatch('designs/toggleColumn', column);
      this.$store.dispatch('designs/getSQL', { run: false });
    },

    joinAggregateSelected(join, aggregate) {
      this.$store.dispatch('designs/toggleAggregate', { aggregate, tableName: join.name });
      this.$store.dispatch('designs/getSQL', { run: false });
    },

    runQuery() {
      this.$store.dispatch('designs/getSQL', { run: true });
    },

    loadReport(report) {
      this.$store.dispatch('designs/loadReport', { name: report.name });
    },

    saveReport() {
      this.$store.dispatch('designs/saveReport', this.saveReportSettings);
    },

    updateReport() {
      this.$store.dispatch('designs/updateReport');
    },

    toggleNewDashboardModal() {
      this.isNewDashboardModalOpen = !this.isNewDashboardModalOpen;
    },
  },
};
</script>

<template>
  <section>

    <div class="columns is-vcentered">

      <div class="column is-one-quarter">
        <div class="is-grouped is-pulled-left">
          <div v-if="hasActiveReport()">{{activeReport.name}}</div>
          <div v-else><em>Untitled Report</em></div>
        </div>
      </div>

      <div class="column">
        <div class="field is-grouped is-pulled-right">

          <p v-if="hasActiveReport()" class="control" @click="getDashboards">
            <Dropdown label="Add to Dashboard" is-right-aligned>
<<<<<<< HEAD
              <div class="dropdown-content" slot-scope="{ dropdownClose }">
                <a
                  class="dropdown-item"
                  @click="toggleNewDashboardModal(); dropdownClose();">
=======
              <div class="dropdown-content" slot-scope="{ dropdownForceClose }">
                <a
                  class="dropdown-item"
                  @click="toggleNewDashboardModal(); dropdownForceClose();">
>>>>>>> 87b7551f... initial UI cleanup in Analyze to better group editing tasks (Query as data related edits and Results as presentation related edits) as opposed to conflating what a user can do in each container (aimed as a user mental model improvment)
                  New Dashboard
                </a>
                <div v-if="dashboards.length">
                  <div class="dropdown-item"
                      v-for="dashboard in dashboards"
                      :key="dashboard.id">
                    <label for="'checkbox-' + dashboard.id"
                            @click="
                              toggleActiveReportInDashboard(dashboard);
<<<<<<< HEAD
                              dropdownClose();">
=======
                              dropdownForceClose();">
>>>>>>> 87b7551f... initial UI cleanup in Analyze to better group editing tasks (Query as data related edits and Results as presentation related edits) as opposed to conflating what a user can do in each container (aimed as a user mental model improvment)
                      <input type="checkbox"
                            :id="'checkbox-' + dashboard.id"
                            :checked="isActiveReportInDashboard(dashboard)">
                      {{dashboard.name}}
                    </label>
                  </div>
                </div>
              </div>
            </Dropdown>
          </p>

          <div class="control field" :class="{'has-addons': hasActiveReport()}">
            <p class="control">
              <button
                class="button is-interactive-primary is-outlined"
                v-if="hasActiveReport()"
                @click="updateReport();">
                <span>Save</span>
              </button>
            </p>
            <p class="control">
              <Dropdown
                :disabled="!hasChartableResults"
                :label="hasActiveReport() ? '' : 'Save'"
                button-classes='is-interactive-primary is-outlined'
                is-right-aligned>
<<<<<<< HEAD
                <div class="dropdown-content" slot-scope="{ dropdownClose }">
=======
                <div class="dropdown-content" slot-scope="{ dropdownForceClose }">
>>>>>>> 87b7551f... initial UI cleanup in Analyze to better group editing tasks (Query as data related edits and Results as presentation related edits) as opposed to conflating what a user can do in each container (aimed as a user mental model improvment)
                  <div class="dropdown-item">
                    <div class="field">
                      <label class="label" v-if="hasActiveReport()">Save as</label>
                      <div class="control">
                        <input class="input"
                                type="text"
                                placeholder="Name your report"
                                v-model="saveReportSettings.name">
                      </div>
                    </div>
                    <div class="field is-grouped">
                      <div class="control">
                        <button class="button is-interactive-primary"
                                :disabled="!saveReportSettings.name"
<<<<<<< HEAD
                                @click="saveReport(); dropdownClose();">Save</button>
                      </div>
                      <div class="control">
                        <button class="button is-text"
                                @click="dropdownClose();">
=======
                                @click="saveReport(); dropdownForceClose();">Save</button>
                      </div>
                      <div class="control">
                        <button class="button is-text"
                                @click="dropdownForceClose();">
>>>>>>> 87b7551f... initial UI cleanup in Analyze to better group editing tasks (Query as data related edits and Results as presentation related edits) as opposed to conflating what a user can do in each container (aimed as a user mental model improvment)
                          Cancel</button>
                      </div>
                    </div>
                  </div>
                </div>
              </Dropdown>
            </p>
          </div>

          <p class="control">
            <Dropdown
              :disabled="!reports.length"
              label="Load"
              button-classes='is-interactive-primary is-outlined'
              is-right-aligned>
<<<<<<< HEAD
              <div class="dropdown-content" slot-scope="{ dropdownClose }">
                <a class="dropdown-item"
                    v-for="report in reports"
                    :key="report.name"
                    @click="loadReport(report); dropdownClose();">
=======
              <div class="dropdown-content" slot-scope="{ dropdownForceClose }">
                <a class="dropdown-item"
                    v-for="report in reports"
                    :key="report.name"
                    @click="loadReport(report); dropdownForceClose();">
>>>>>>> 87b7551f... initial UI cleanup in Analyze to better group editing tasks (Query as data related edits and Results as presentation related edits) as opposed to conflating what a user can do in each container (aimed as a user mental model improvment)
                  {{report.name}}
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
          <div class="columns is-vcentered">
<<<<<<< HEAD
            <div class="column is-two-fifths">
              <h2 class="title is-5">Query</h2>
            </div>
            <div class="column is-three-fifths">
              <div class="buttons is-right">
                <Dropdown
                  label="SQL"
                  button-classes='is-text is-small'
                  :disabled='!currentSQL'
                  is-caret-removed>
                  <div class="dropdown-content">
                    <div class="level">
                      <div class="level-item">
                        <code>{{formattedSql}}</code>
                      </div>
                    </div>
                  </div>
                </Dropdown>
=======
            <div class="column">
              <h2 class="title is-5">Query</h2>
            </div>
            <div class="column">
              <div class="buttons is-right">
>>>>>>> 87b7551f... initial UI cleanup in Analyze to better group editing tasks (Query as data related edits and Results as presentation related edits) as opposed to conflating what a user can do in each container (aimed as a user mental model improvment)
                <button class="button is-success"
                  :class="{'is-loading': loadingQuery}"
                  :disabled="!currentSQL"
                  @click="runQuery">Run</button>
              </div>
            </div>
          </div>

<<<<<<< HEAD
          <div class="columns is-vcentered">
            <div class="column">
              <div class="field">
                <label class="label">Limit</label>
                <div class="control is-expanded">
                  <input
                    class="input is-small has-text-interactive-secondary"
                    type="text"
                    placeholder="Limit"
                    v-model="limit"
                    @focus="$event.target.select()">
                </div>
              </div>
            </div>
            <div class="column">
              <div class="field">
                <label class="label">
                  <span>Filters</span>
                  <span
                    v-if='filtersCount > 0'
                    class='has-text-weight-light has-text-grey-light is-size-7'>({{filtersCount}})</span>
                </label>
                <div class="control is-expanded">
                  <Dropdown
                    :label="hasFilters ? 'Edit' : 'None'"
                    :button-classes="`is-small ${hasFilters ? 'has-text-interactive-secondary' : ''}`"
                    ref='filter-dropdown'>
                    <div class="dropdown-content" style='width: 600px;'>
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
                v-if='attributesCount > 0'
                class='has-text-weight-light has-text-grey-light is-size-7'>({{attributesCount}})</span>
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
                :class="{'is-collapsed': design.related_table.collapsed}"
                @click="tableRowClicked(design.related_table)">
                <span class="icon is-small panel-icon">
                  <font-awesome-icon icon="table"></font-awesome-icon>
                </span>
                {{design.label}}
                </a>
            </template>
            <template v-if="!design.related_table.collapsed">
              <a class="panel-block
                  panel-block-heading
                  has-background-white"
                  v-if="showJoinColumnAggregateHeader(design.related_table.columns)">
                Columns
              </a>
              <template v-for="timeframe in design.related_table.timeframes">
                <a class="panel-block dimension-group"
                    :key="timeframe.label"
                    v-if="!timeframe.related_view.hidden"
                    @click="timeframeSelected(timeframe)"
                    :class="{'is-active': timeframe.selected}">
                  {{timeframe.label}}
                </a>
                <template v-for="period in timeframe.periods">
                  <a class="panel-block indented"
                      :key="period.label"
                      @click="timeframePeriodSelected(period)"
                      v-if="timeframe.selected"
                      :class="{'is-active': period.selected}">
                    {{period.label}}
                  </a>
                </template>
              </template>
              <a class="panel-block space-between has-text-weight-medium"
                  v-for="column in design.related_table.columns"
                  :key="column.label"
                  v-if="!column.hidden"
                  @click="columnSelected(column)"
                  :class="{'is-active': column.selected}">
                {{column.label}}
                <button
                  v-if="getIsAttributeInFilters(design.from, column.name, 'column')"
                  class="button is-small"
                  @click.stop='jumpToFilters'>
                  <span class="icon has-text-interactive-secondary">
                    <font-awesome-icon icon="filter"></font-awesome-icon>
                  </span>
                </button>
              </a>
              <!-- eslint-disable-next-line vue/require-v-for-key -->
              <a class="panel-block
                  panel-block-heading
                  has-background-white"
                  v-if="showJoinColumnAggregateHeader(design.related_table.aggregates)">
                Aggregates
              </a>
              <a class="panel-block space-between has-text-weight-medium"
                  v-for="aggregate in design.related_table.aggregates"
                  :key="aggregate.label"
                  @click="aggregateSelected(aggregate)"
                  :class="{'is-active': aggregate.selected}">
                {{aggregate.label}}
                <button
                  v-if="getIsAttributeInFilters(design.from, aggregate.name, 'aggregate')"
                  class="button is-small"
                  @click.stop='jumpToFilters'>
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
                  class="panel-block
                    has-background-white-bis
                    has-text-grey
                    is-expandable"
                    :class="{'is-collapsed': join.collapsed}"
                    :key="join.label"
                    @click="joinRowClicked(join)">
                    <span class="icon is-small panel-icon">
                      <font-awesome-icon icon="table"></font-awesome-icon>
                    </span>
                    {{join.label}}
                </a>
                <template v-if="!join.collapsed">
                  <!-- eslint-disable-next-line vue/require-v-for-key -->
                  <a class="panel-block
                    panel-block-heading
                    has-text-weight-light
                    has-background-white"
                    v-if="showJoinColumnAggregateHeader(join.related_table.columns)">
                    Columns
=======
          <nav class="panel has-background-white">

            <div class="is-unselectable">
              <!-- no v-ifs with v-fors https://vuejs.org/v2/guide/conditional.html#v-if-with-v-for -->
              <template v-if="hasJoins">
                <template v-for="join in design.joins">
                  <a
                    class="panel-block
                      panel-block-heading
                      has-background-white-bis
                      has-text-grey
                      is-expandable"
                      :class="{'is-collapsed': join.collapsed}"
                      :key="join.label"
                      @click="joinRowClicked(join)">
                      {{join.label}}
>>>>>>> 87b7551f... initial UI cleanup in Analyze to better group editing tasks (Query as data related edits and Results as presentation related edits) as opposed to conflating what a user can do in each container (aimed as a user mental model improvment)
                  </a>
                  <template v-if="!join.collapsed">
                    <!-- eslint-disable-next-line vue/require-v-for-key -->
                    <a class="panel-block
                      panel-block-heading
                      has-background-white"
                      v-if="showJoinColumnAggregateHeader(join.related_table.columns)">
                      Columns
                    </a>
                    <template v-for="timeframe in join.related_table.timeframes">
                      <a class="panel-block timeframe"
                          v-if="!timeframe.hidden"
                          @click="isConnectionDialectSqlite(dialect) || timeframeSelected(timeframe)"
                          :key="timeframe.label"
                          :class="{
                            'is-active': timeframe.selected,
                            'is-sqlite-unsupported': isConnectionDialectSqlite(dialect)
                          }">
                        {{timeframe.label}}
                        <div class='sqlite-unsupported-container'
                              v-if='isConnectionDialectSqlite(dialect)'>
                          <small>Unsupported by SQLite</small>
                        </div>
                      </a>
                      <template v-if="timeframe.selected">
                        <template v-for="period in timeframe.periods">
                          <a class="panel-block indented"
                              :key="timeframe.label.concat('-', period.label)"
                              @click="timeframePeriodSelected(period)"
                              :class="{'is-active': period.selected}">
                            {{period.label}}
                          </a>
                        </template>
                      </template>
                    </template>
<<<<<<< HEAD
                  </template>
                  <template v-for="column in join.related_table.columns">
                    <a class="panel-block space-between has-text-weight-medium"
                      v-if="!column.hidden"
                      :key="column.label"
                      :class="{'is-active': column.selected}"
                      @click="joinColumnSelected(join, column)">
                      {{column.label}}
                      <button
                        v-if="getIsAttributeInFilters(join.name, column.name, 'column')"
                        class="button is-small"
                        @click.stop='jumpToFilters'>
                        <span class="icon has-text-interactive-secondary">
                          <font-awesome-icon icon="filter"></font-awesome-icon>
                        </span>
                      </button>
=======
                    <template v-for="column in join.related_table.columns">
                      <a class="panel-block"
                        v-if="!column.hidden"
                        :key="column.label"
                        :class="{'is-active': column.selected}"
                        @click="joinColumnSelected(join, column)">
                      {{column.label}}
                      </a>
                    </template>
                    <!-- eslint-disable-next-line vue/require-v-for-key -->
                    <a class="panel-block
                      panel-block-heading
                      has-background-white"
                      v-if="showJoinColumnAggregateHeader(join.related_table.aggregates)">
                      Aggregates
>>>>>>> 87b7551f... initial UI cleanup in Analyze to better group editing tasks (Query as data related edits and Results as presentation related edits) as opposed to conflating what a user can do in each container (aimed as a user mental model improvment)
                    </a>
                    <template v-for="aggregate in join.related_table.aggregates">
                      <a class="panel-block"
                        v-if="!aggregate.hidden"
                        :key="aggregate.label"
                        :class="{'is-active': aggregate.selected}"
                        @click="joinAggregateSelected(join, aggregate)">
                      {{aggregate.label}}
                      </a>
                    </template>
                  </template>
                </template>
              </template>
              <template>
                <a
                  class="panel-block
                  panel-block-heading
                  has-background-white-bis
                  has-text-grey
                  is-expandable"
                  :class="{'is-collapsed': design.related_table.collapsed}"
                  @click="tableRowClicked(design.related_table)">
                    {{design.label}}
                  </a>
              </template>
              <template v-if="!design.related_table.collapsed">
                <a class="panel-block
                    panel-block-heading
                    has-background-white"
                    v-if="showJoinColumnAggregateHeader(design.related_table.columns)">
                  Columns
                </a>
                <template v-for="timeframe in design.related_table.timeframes">
                  <a class="panel-block dimension-group"
                      :key="timeframe.label"
                      v-if="!timeframe.related_view.hidden"
                      @click="timeframeSelected(timeframe)"
                      :class="{'is-active': timeframe.selected}">
                    {{timeframe.label}}
                  </a>
<<<<<<< HEAD
                  <template v-for="aggregate in join.related_table.aggregates">
                    <a class="panel-block space-between has-text-weight-medium"
                      v-if="!aggregate.hidden"
                      :key="aggregate.label"
                      :class="{'is-active': aggregate.selected}"
                      @click="joinAggregateSelected(join, aggregate)">
                      {{aggregate.label}}
                      <button
                        v-if="getIsAttributeInFilters(join.name, aggregate.name, 'aggregate')"
                        class="button is-small"
                        @click.stop='jumpToFilters'>
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
                  v-if='resultsCount > 0'
                  class='has-text-weight-light has-text-grey-light is-size-7'>({{resultsCount}})</span>
              </h2>
            </div>
            <div class="column">
              <div class="buttons has-addons is-right">
                <button
                  class="button"
                  @click.stop="setChartType('BarChart')"
                  :class="{
                    'has-text-grey-lighter': chartType !== 'BarChart',
                    'is-active has-text-interactive-secondary': chartType === 'BarChart',
                  }"
                  :disabled="!hasChartableResults">
                  <span class="icon is-small">
                    <font-awesome-icon icon="chart-bar"></font-awesome-icon>
                  </span>
                </button>
                <button
                  class="button"
                  @click.stop="setChartType('LineChart')"
                  :class="{
                    'has-text-grey-lighter': chartType !== 'LineChart',
                    'is-active has-text-interactive-secondary': chartType === 'LineChart',
                  }"
                  :disabled="!hasChartableResults">
                  <span class="icon is-small">
                    <font-awesome-icon icon="chart-line"></font-awesome-icon>
                  </span>
                </button>
                <button
                  class="button"
                  @click.stop="setChartType('AreaChart')"
                  :class="{
                    'has-text-grey-lighter': chartType !== 'AreaChart',
                    'is-active has-text-interactive-secondary': chartType === 'AreaChart',
                  }"
                  :disabled="!hasChartableResults">
                  <span class="icon is-small">
                    <font-awesome-icon icon="chart-area"></font-awesome-icon>
                  </span>
                </button>
                <button
                  class="button"
                  @click.stop="setChartType('ScatterChart')"
                  :class="{
                    'has-text-grey-lighter': chartType !== 'ScatterChart',
                    'is-active has-text-interactive-secondary': chartType === 'ScatterChart',
                  }"
                  :disabled="!hasChartableResults">
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
              <chart :chart-type='chartType'
                      :results='results'
                      :result-aggregates='resultAggregates'></chart>
            </div>
            <div v-if="!hasChartableResults">
              <div class="box is-radiusless is-shadowless">
                <p>
                  Run a query with at least one aggregate selected or load a report
                </p>
              </div>
            </div>
          </div>

          <hr>

          <!-- results/SQL tab -->
          <div>
            <div class="notification is-danger" v-if="hasSQLError">
              <button class="delete" @click="resetErrorMessage"></button>
              <ul>
                <li v-for="(error, key) in sqlErrorMessage" :key="key">{{error}}</li>
              </ul>
            </div>

            <ResultTable></ResultTable>

=======
                  <template v-for="period in timeframe.periods">
                    <a class="panel-block indented"
                        :key="period.label"
                        @click="timeframePeriodSelected(period)"
                        v-if="timeframe.selected"
                        :class="{'is-active': period.selected}">
                      {{period.label}}
                    </a>
                  </template>
                </template>
                <a class="panel-block"
                    v-for="column in design.related_table.columns"
                    :key="column.label"
                    v-if="!column.hidden"
                    @click="columnSelected(column)"
                    :class="{'is-active': column.selected}">
                  {{column.label}}
                </a>
                <!-- eslint-disable-next-line vue/require-v-for-key -->
                <a class="panel-block
                    panel-block-heading
                    has-background-white"
                    v-if="showJoinColumnAggregateHeader(design.related_table.aggregates)">
                  Aggregates
                </a>
                <a class="panel-block"
                    v-for="aggregate in design.related_table.aggregates"
                    :key="aggregate.label"
                    @click="aggregateSelected(aggregate)"
                    :class="{'is-active': aggregate.selected}">
                  {{aggregate.label}}
                </a>
              </template>
            </div>

          </nav>
        </div>
      </aside>

      <div class="column is-three-quarters">

        <div class="box">
          <div class="columns is-vcentered">
            <div class="column">
              <h2 class="title is-5">Results</h2>
            </div>
            <div class="column">
              <div class="buttons is-right">
                <button class="button is-success"
                  :class="{'is-loading': loadingQuery}"
                  :disabled="!currentSQL"
                  @click="runQuery">Run</button>
              </div>
            </div>
          </div>

          <!-- filters tab -->
          <div v-if="design.has_filters">
            <div class="has-background-primary
              accordion-header
              has-text-white-bis
              is-expandable"
              @click="toggleFilterOpen"
              :class="{'is-collapsed': !filtersOpen}">

              <span>Filters</span>
              <div class="accordion-toggle">
                <a class="button is-primary is-small">
                  <span class="icon is-small">
                    <font-awesome-icon :icon="filtersOpen ? 'angle-up' : 'angle-down'">
                    </font-awesome-icon>
                  </span>
                </a>
              </div>
            </div>
            <div class="accordion-body">
              <div v-if="filtersOpen">
                <div class="columns">
                  <div class="column is-3">
                    <strong>{{filter.design_label}}</strong>
                    <span>{{filter.label}}</span>
                    <span>({{filter.type}})</span>
                  </div>
                  <div class="column is-9">
                    <yes-no-filter v-if="filter.type === 'yesno'"></yes-no-filter>
                    <div class="field" v-if="filter.type == 'string'">
                      <select-dropdown
                        :placeholder="filter.field"
                        :field="filter.sql"
                        :dropdownList="getResultsFromDistinct(filter.sql)"
                        :dropdownLabelKey="getKeyFromDistinct(filter.sql)"
                        @focused="inputFocused(filter.sql)"
                        @selected="dropdownSelected"
                        @modifierChanged="modifierChanged">
                      </select-dropdown>
                    </div>
                    <div class="tags selected-filters">
                      <template v-for="(selected, key) in getSelectionsFromDistinct(filter.sql)">
                        <span class="tag is-link" :key="key">
                          {{selected}}
                          <button class="delete is-small"></button>
                        </span>
                      </template>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- charts tab -->
          <div class="has-background-primary
            accordion-header
            has-text-white-bis
            is-expandable"
            @click="toggleChartsOpen"
            :class="{'is-collapsed': !chartsOpen}">

            <span class="accordion-title">Charts</span>
            <div>
              <div class="field has-addons chart-buttons">
                <p class="control" @click.stop="setAndOpenChart('BarChart')">
                  <button
                    class="button is-small is-text has-text-white"
                    :class="{'is-active': chartType === 'BarChart'}"
                    :disabled="!hasChartableResults">
                    <span class="icon is-small">
                      <font-awesome-icon icon="chart-bar"></font-awesome-icon>
                    </span>
                  </button>
                </p>
                <p class="control" @click.stop="setAndOpenChart('LineChart')">
                  <button
                    class="button is-small is-text has-text-white"
                    :class="{'is-active': chartType === 'LineChart'}"
                    :disabled="!hasChartableResults">
                    <span class="icon is-small">
                      <font-awesome-icon icon="chart-line"></font-awesome-icon>
                    </span>
                  </button>
                </p>
                <p class="control" @click.stop="setAndOpenChart('AreaChart')">
                  <button
                    class="button is-small is-text has-text-white"
                    :class="{'is-active': chartType === 'AreaChart'}"
                    :disabled="!hasChartableResults">
                    <span class="icon is-small">
                      <font-awesome-icon icon="chart-area"></font-awesome-icon>
                    </span>
                  </button>
                </p>
                <p class="control" @click.stop="setAndOpenChart('ScatterChart')">
                  <button
                    class="button is-small is-text has-text-white"
                    :class="{'is-active': chartType === 'ScatterChart'}"
                    :disabled="!hasChartableResults">
                    <span class="icon is-small">
                      <font-awesome-icon icon="dot-circle"></font-awesome-icon>
                    </span>
                  </button>
                </p>
              </div>
            </div>

            <div class="accordion-toggle">
              <a class="button is-primary is-small">
                <span class="icon is-small">
                  <font-awesome-icon :icon="chartsOpen ? 'angle-up' : 'angle-down'"></font-awesome-icon>
                </span>
              </a>
            </div>

          </div>

          <div class="accordion-body">
            <div v-if="chartsOpen" >
              <div v-if="hasChartableResults" class="chart-toggles">
                <chart :chart-type='chartType'
                        :results='results'
                        :result-aggregates='resultAggregates'></chart>
              </div>
              <div v-if="!hasChartableResults">
                <div class="box is-radiusless is-shadowless">
                  <p>
                    Run a query with at least one aggregate selected or load a report
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- results/SQL tab -->
          <div class="has-background-primary
            accordion-header
            has-text-white-bis
            is-expandable"
            @click="toggleDataOpen"
            :class="{'is-collapsed': !dataOpen}">

            <span>Data</span>
            <div class="accordion-toggle">
              <a class="button is-primary is-small">
                <span class="icon is-small">
                  <font-awesome-icon :icon="dataOpen ? 'angle-up' : 'angle-down'"></font-awesome-icon>
                </span>
              </a>
            </div>
          </div>
          <div class="accordion-body">
            <div v-if="dataOpen" class="box is-radiusless is-shadowless">
              <div class="notification is-danger" v-if="hasSQLError">
                <button class="delete" @click="resetErrorMessage"></button>
                <ul>
                  <li v-for="(error, key) in sqlErrorMessage" :key="key">{{error}}</li>
                </ul>
              </div>
              <div class="columns is-vcentered">

                <div class="column">
                  <div class="tabs">
                    <ul>
                      <li :class="{'is-active': isResultsTab}" @click="setCurrentTab('results')">
                        <a>Results ({{numResults}})</a>
                      </li>
                      <li :class="{'is-active': isSQLTab}" @click="setCurrentTab('sql')">
                        <a>SQL</a>
                      </li>
                    </ul>
                  </div>
                </div>

                <div class="column">
                  <div class="field is-horizontal is-marginless is-pulled-right">
                    <div class="field-label">
                      <label class="label">Limit</label>
                    </div>
                    <div class="field-body">
                      <div class="field">
                        <div class="control">
                          <input class="input is-small" type="text" v-model="limit" placeholder="Limit">
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

              </div>
              <ResultTable></ResultTable>
              <div>
                <div class="" v-if="isSQLTab && currentSQL">
                  <code>{{formattedSql}}</code>
                </div>
              </div>
            </div>
>>>>>>> 87b7551f... initial UI cleanup in Analyze to better group editing tasks (Query as data related edits and Results as presentation related edits) as opposed to conflating what a user can do in each container (aimed as a user mental model improvment)
          </div>

          <!-- New Dashboard Modal -->
          <NewDashboardModal
            v-if="isNewDashboardModalOpen"
            @close="toggleNewDashboardModal"
            :report="activeReport">
          </NewDashboardModal>

        </div>
      </div>
    </div>
  </section>
</template>

<style lang="scss" scoped>
@import '@/scss/bulma-preset-overrides.scss';
@import "../../../node_modules/bulma/bulma";

code {
  white-space: pre;
  word-wrap: break-word;
}
.panel-block {
  position: relative;
  &.space-between {
    justify-content: space-between;
  }
  &.indented {
    padding-left: 1.75rem;
  }
  &.is-active {
    color: $interactive-secondary;
    border-left-color: $interactive-secondary;
    border-left-width: 2px;
    @extend .has-background-white-ter;
  }
  &.panel-block-heading {
    padding: 0.25rem 0.75rem;
    font-size: 0.75rem;
    &:hover {
      background: white;
    }
  }
  &.is-sqlite-unsupported {
    opacity: .5;
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
      content: " ";
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

.data-toggles {
  padding-top: .5rem;
}

.filter-item {
  padding: 1.5rem;
}

.selected-filters {
  padding: 1.5rem;
  padding-left: 0;
}
</style>
