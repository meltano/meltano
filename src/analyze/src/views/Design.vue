<template>
  <router-view-layout>

    <div slot='left'>
      <nav class="panel ">
        <div class="panel-block">
          <div class="field has-addons">
            <div class="control is-expanded">
              <input class="input" type="text" placeholder="Filter" disabled>
            </div>
            <div class="control">
              <button class="button" disabled>
                <span class="icon">
                  <font-awesome-icon icon="search"></font-awesome-icon>
                </span>
              </button>
            </div>
          </div>
        </div>

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

    <div slot="right">

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
                <div class="dropdown-content" slot-scope="{ dropdownForceClose }">
                  <a
                    class="dropdown-item"
                    @click="toggleNewDashboardModal(); dropdownForceClose();">
                    New Dashboard
                  </a>
                  <div v-if="dashboards.length">
                    <div class="dropdown-item"
                        v-for="dashboard in dashboards"
                        :key="dashboard.id">
                      <label for="'checkbox-' + dashboard.id"
                              @click="
                                toggleActiveReportInDashboard(dashboard);
                                dropdownForceClose();">
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
                  class="button is-success is-outlined"
                  v-if="hasActiveReport()"
                  @click="updateReport();">
                  <span>Save</span>
                </button>
              </p>
              <p class="control">
                <Dropdown
                  :disabled="!hasChartableResults"
                  :label="hasActiveReport() ? '' : 'Save'"
                  button-classes='is-success is-outlined'
                  is-right-aligned>
                  <div class="dropdown-content" slot-scope="{ dropdownForceClose }">
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
                          <button class="button is-link"
                                  :disabled="!saveReportSettings.name"
                                  @click="saveReport(); dropdownForceClose();">Save</button>
                        </div>
                        <div class="control">
                          <button class="button is-text"
                                  @click="dropdownForceClose();">
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
                button-classes='is-success is-outlined'
                is-right-aligned>
                <div class="dropdown-content" slot-scope="{ dropdownForceClose }">
                  <a class="dropdown-item"
                      v-for="report in reports"
                      :key="report.name"
                      @click="loadReport(report); dropdownForceClose();">
                    {{report.name}}
                  </a>
                </div>
              </Dropdown>
            </p>

            <p class="control">
              <button class="button is-success"
                :class="{'is-loading': loadingQuery}"
                :disabled="!currentSQL"
                @click="runQuery">Run Query</button>
            </p>

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
      </div>

      <!-- New Dashboard Modal -->
      <NewDashboardModal
        v-if="isNewDashboardModalOpen"
        @close="toggleNewDashboardModal"
        :report="activeReport">
      </NewDashboardModal>

    </div>

  </router-view-layout>
</template>
<script>
import { mapState, mapGetters, mapActions } from 'vuex';
import capitalize from '@/filters/capitalize';
import RouterViewLayout from '@/views/RouterViewLayout';
import Store from '@/store';
import Dropdown from '../components/generic/Dropdown';
import ResultTable from '../components/designs/ResultTable';
import SelectDropdown from '../components/generic/SelectDropdown';
import YesNoFilter from '../components/filters/YesNoFilter';
import Chart from '../components/designs/Chart';

import NewDashboardModal from '../components/dashboards/NewDashboardModal';

export default {
  name: 'Design',
  data() {
    return {
      isNewDashboardModalOpen: false,
    };
  },

  beforeRouteUpdate(to, from, next) {
    const { slug, model, design } = to.params;
    Store.dispatch('designs/getDesign', { model, design, slug });
    next();
  },

  mounted() {
    const { slug, model, design } = this.$route.params;
    this.$store.dispatch('designs/getDesign', { model, design, slug });
  },
  filters: {
    capitalize,
  },
  components: {
    Chart,
    NewDashboardModal,
    Dropdown,
    ResultTable,
    RouterViewLayout,
    SelectDropdown,
    YesNoFilter,
  },
  computed: {
    ...mapState('designs', [
      'activeReport',
      'design',
      'currentModel',
      'currentDesign',
      'currentSQL',
      'loadingQuery',
      'filtersOpen',
      'dataOpen',
      'saveReportSettings',
      'reports',
      'chartsOpen',
      'hasSQLError',
      'sqlErrorMessage',
      'results',
      'resultAggregates',
      'chartType',
      'dialect',
    ]),
    ...mapGetters('designs', [
      'currentModelLabel',
      'currentDesignLabel',
      'isDataTab',
      'isResultsTab',
      'hasChartableResults',
      'numResults',
      'isSQLTab',
      'getDistinctsForField',
      'getResultsFromDistinct',
      'getKeyFromDistinct',
      'getSelectionsFromDistinct',
      'getChartYAxis',
      'hasJoins',
      'showJoinColumnAggregateHeader',
      'formattedSql',
    ]),
    ...mapState('dashboards', [
      'dashboards',
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
  },
  methods: {
    ...mapActions('dashboards', [
      'getDashboards',
    ]),

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

    inputFocused(field) {
      if (!this.getDistinctsForField(field)) {
        this.$store.dispatch('designs/getDistinct', field);
      }
    },

    setAndOpenChart(chartType) {
      this.$store.dispatch('designs/setChartType', chartType);
      if (!this.chartsOpen) {
        this.$store.dispatch('designs/toggleChartsOpen');
      }
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
      this.$store.dispatch('designs/toggleAggregate', aggregate);
      this.$store.dispatch('designs/getSQL', { run: false });
    },

    joinColumnSelected(join, column) {
      this.$store.dispatch('designs/toggleColumn', column);
      this.$store.dispatch('designs/getSQL', { run: false });
    },

    joinAggregateSelected(join, aggregate) {
      this.$store.dispatch('designs/toggleAggregate', aggregate);
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

    setCurrentTab(tab) {
      this.$store.dispatch('designs/switchCurrentTab', tab);
    },

    toggleFilterOpen() {
      this.$store.dispatch('designs/toggleFilterOpen');
    },

    toggleDataOpen() {
      this.$store.dispatch('designs/toggleDataOpen');
    },

    toggleChartsOpen() {
      this.$store.dispatch('designs/toggleChartsOpen');
    },

    toggleNewDashboardModal() {
      this.isNewDashboardModalOpen = !this.isNewDashboardModalOpen;
    },

    dropdownSelected(item, field) {
      this.$store.dispatch('designs/addDistinctSelection', {
        item,
        field,
      });
      this.$store.dispatch('designs/getSQL', { run: false });
    },

    modifierChanged(item, field) {
      this.$store.dispatch('designs/addDistinctModifier', {
        item,
        field,
      });
      this.$store.dispatch('designs/getSQL', { run: false });
    },
    ...mapActions('designs', [
      'resetErrorMessage',
    ]),
  },
};
</script>
<style lang="scss" scoped>
@import '@/scss/bulma-preset-overrides.scss';
@import "../../node_modules/bulma/bulma";

code {
  white-space: pre;
  word-wrap: break-word;
}
.panel-block {
  position: relative;
  &.indented {
    padding-left: 1.75rem;
  }
  &.is-active {
    border-left-color: $primary;
    border-left-width: 4px;
    @extend .has-background-white-ter;
  }
  &.panel-block-heading {
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
    font-weight: bold;
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

.accordion-header {
  padding: .5rem .5rem .5rem 1rem;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  cursor: pointer;
  @extend .is-unselectable;
  .accordion-title {
    padding-right: 1.5rem;
  }
  .button:not([disabled]) {
    &.is-active {
      @extend .has-text-primary;
      @extend .has-background-white-ter;
    }
    &.is-text:hover,
    &.is-text:focus {
      @extend .has-text-primary;
      @extend .has-background-white;
    }
  }
  .accordion-toggle {
    margin-left: auto;
  }
}
.accordion-body {
  margin-bottom: 0.25rem;
  @extend .has-background-white-bis;
  .box {
    @extend .has-background-white-bis;
  }
}
.filter-item {
  padding: 1.5rem;
}

.selected-filters {
  padding: 1.5rem;
  padding-left: 0;
}
.chart-buttons {
  .button {
    background: transparent;
  }
}
</style>
