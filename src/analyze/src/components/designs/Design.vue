<template>
<div class="container">
  <section class="section">
    <div class="columns">
      <nav class="panel column is-one-quarter">
        <p class="panel-heading">
          {{design.label}}
        </p>
        <div class="panel-block">
          <p class="control">
            <input class="input is-small" type="text" placeholder="search">
          </p>
        </div>

        <div class="inner-scroll text-selection-off">
          <!-- no v-ifs with v-fors https://vuejs.org/v2/guide/conditional.html#v-if-with-v-for -->
          <template v-if="hasJoins">
            <template v-for="join in design.joins">
              <a
                class="panel-block
                  panel-block-heading
                  has-background-white-ter
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
                      @click="timeframeSelected(timeframe)"
                      :key="timeframe.label"
                      :class="{
                        'is-active': timeframe.selected,
                        'is-sqlite-unsupported': isConnectionDialectSqlite(connectionDialect)
                      }">
                    {{timeframe.label}}
                    <div class='sqlite-unsupported-container'
                      v-if='isConnectionDialectSqlite(connectionDialect)'
                    >
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
                  v-if="showJoinColumnAggregateHeader(join.aggregates)">
                  Aggregates
                </a>
                <template v-for="aggregate in join.aggregates">
                  <a class="panel-block"
                    v-if="aggregate.related_table.hidden"
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
              has-background-white-ter
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

        <div class="panel-block">
          <button class="button is-link is-outlined is-fullwidth">
            Reset All Filters
          </button>
        </div>
      </nav>
      <div class="column is-three-quarters">
        <div class="columns">
          <div class="column">
            <div class="buttons is-pulled-right">

              <div class="dropdown"
                    :class="{'is-active': loadReportOpen}"
                    v-if="reports.length > 0">
                <div class="dropdown-trigger">
                  <button class="button"
                          aria-haspopup="true"
                          aria-controls="dropdown-menu-load-report"
                          @click="toggleLoadReportOpen">
                    <span>Load Report</span>
                    <span class="icon is-small">
                      <i class="fas fa-angle-down" aria-hidden="true"></i>
                    </span>
                  </button>
                </div>
                <div class="dropdown-menu" id="dropdown-menu-load-report" role="menu">
                  <div class="dropdown-content">
                    <a class="dropdown-item"
                        :class="{'is-loading': loadingQuery}"
                        v-for="report in reports"
                        :key="report.name"
                        @click="loadReport(report)">
                      {{report.name}}
                    </a>
                  </div>
                </div>
              </div>

              <div class="dropdown"
                    :class="{'is-active': saveReportOpen}"
                    v-if="numResults > 0">
                <div class="dropdown-trigger">
                  <button class="button"
                          aria-haspopup="true"
                          aria-controls="dropdown-menu-save-report"
                          @click="toggleSaveReportOpen">
                    <span>Save Report</span>
                    <span class="icon is-small">
                      <i class="fas fa-angle-down" aria-hidden="true"></i>
                    </span>
                  </button>
                </div>
                <div class="dropdown-menu" id="dropdown-menu-save-report" role="menu">
                  <div class="dropdown-content">
                    <div class="dropdown-item">
                      <div class="field">
                        <label class="label">Name</label>
                        <div class="control">
                          <input class="input"
                                  type="text"
                                  placeholder="Name your report"
                                  v-model="saveReportSettings.name">
                        </div>
                      </div>
                      <div class="field">
                        <label class="label">Description</label>
                        <div class="control">
                          <textarea class="textarea"
                                    placeholder="Describe your report for easier reference later"
                                    v-model="saveReportSettings.description"></textarea>
                        </div>
                      </div>
                      <div class="field is-grouped">
                        <div class="control">
                          <button class="button is-link" @click="saveReport">Confirm</button>
                        </div>
                        <div class="control">
                          <button class="button is-text" @click="toggleSaveReportOpen">Cancel</button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <a class="button is-primary"
                  :class="{'is-loading': loadingQuery}"
                  @click="runQuery">Run Query</a>

            </div>
          </div>
        </div>
        <template v-if="design.has_filters">
          <div class="has-background-grey-darker
            section-header
            has-text-white-bis
            is-expandable"
            @click="toggleFilterOpen"
            :class="{'is-collapsed': !filtersOpen}">Filters</div>
          <div class="has-background-white-ter filter-item"
                v-for="filter in design.always_filter.filters"
                :key="filter.label"
                v-if="filtersOpen">
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
        </template>

        <!-- charts tab -->
        <div class="has-background-grey-darker
          section-header
          has-text-white-bis
          is-expandable"
          @click="toggleChartsOpen"
          :class="{'is-collapsed': !chartsOpen}">Charts</div>

        <template v-if="chartsOpen">
          <div class="field has-addons chart-buttons">
            <p class="control">
              <a class="button is-small" @click="setChartType('BarChart')">
                <span class="icon is-small">
                  <font-awesome-icon icon="chart-bar" style="color:white;"></font-awesome-icon>
                </span>
              </a>
            </p>
            <p class="control">
              <a class="button is-small">
                <span class="icon is-small" @click="setChartType('LineChart')">
                  <font-awesome-icon icon="chart-line" style="color:white;"></font-awesome-icon>
                </span>
              </a>
            </p>
            <p class="control">
              <a class="button is-small">
                <span class="icon is-small" @click="setChartType('AreaChart')">
                  <font-awesome-icon icon="chart-area" style="color:white;"></font-awesome-icon>
                </span>
              </a>
            </p>
            <p class="control">
              <a class="button is-small">
                <span class="icon is-small" @click="setChartType('ScatterChart')">
                  <font-awesome-icon icon="dot-circle" style="color:white;"></font-awesome-icon>
                </span>
              </a>
            </p>
            <p class="control">
              <a class="button is-small">
                <span class="icon is-small" @click="setChartType('pie')">
                  <font-awesome-icon icon="chart-pie" style="color:white;"></font-awesome-icon>
                </span>
              </a>
            </p>
            <p class="control">
              <a class="button is-small" @click="setChartType('number')">
                <span class="icon is-small" style="color:white;font-weight: bold;">
                  9
                </span>
              </a>
            </p>
          </div>
          <div class="has-background-white-ter chart-toggles">
            <chart></chart>
          </div>
        </template>

        <!-- results/SQL tab -->
        <div class="has-background-grey-darker
        section-header
        has-text-white-bis
        is-expandable"
        @click="toggleDataOpen"
        :class="{'is-collapsed': !dataOpen}">Data</div>
        <template v-if="dataOpen">
        <div class="notification is-danger" v-if="hasSQLError">
          <button class="delete" @click="resetErrorMessage"></button>
          <ul>
            <li v-for="(error, key) in sqlErrorMessage" :key="key">{{error}}</li>
          </ul>
        </div>
        <div class="has-background-white-ter data-toggles">
          <div class="field is-pulled-right">
            <div class="control">
              <input class="input is-small" type="text" v-model="limit" placeholder="Limit">
            </div>
          </div>
          <div class="buttons has-addons">
            <span class="button"
                  :class="{'is-active': isResultsTab}"
                  @click="setCurrentTab('results')">Results ({{numResults}})</span>
            <span class="button"
                  :class="{'is-active': isSQLTab}"
                  @click="setCurrentTab('sql')">SQL</span>
          </div>
        </div>
        <ResultTable></ResultTable>
        <div>
          <div class="" v-if="isSQLTab && currentSQL">
            <code>{{formattedSql}}</code>
          </div>
        </div>
        </template>
      </div>
    </div>
  </section>
</div>
</template>
<script>
import { mapState, mapGetters, mapActions } from 'vuex';
import capitalize from '@/filters/capitalize';
import ResultTable from './ResultTable';
import SelectDropdown from '../SelectDropdown';
import YesNoFilter from '../filters/YesNoFilter';
import Chart from './Chart';

export default {
  name: 'Design',
  created() {
    this.$store.dispatch('designs/getDesign', {
      model: this.$route.params.model,
      design: this.$route.params.design,
    });
  },
  filters: {
    capitalize,
  },
  components: {
    ResultTable,
    SelectDropdown,
    YesNoFilter,
    Chart,
  },
  beforeRouteUpdate(to, from, next) {
    this.$store.dispatch('designs/getDesign', {
      model: to.params.model,
      design: to.params.design,
    });
    next();
  },
  computed: {
    ...mapState('designs', [
      'design',
      'selectedColumns',
      'currentModel',
      'currentDesign',
      'currentSQL',
      'loadingQuery',
      'filtersOpen',
      'dataOpen',
      'loadReportOpen',
      'saveReportOpen',
      'saveReportSettings',
      'reports',
      'chartsOpen',
      'hasSQLError',
      'sqlErrorMessage',
      'connectionDialect',
    ]),
    ...mapGetters('designs', [
      'currentModelLabel',
      'currentDesignLabel',
      'isDataTab',
      'isResultsTab',
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
    ...mapGetters('settings', [
      'isConnectionDialectSqlite',
    ]),
    canToggleTimeframe() {
      return !this.isConnectionDialectSqlite(this.connectionDialect);
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
    inputFocused(field) {
      if (!this.getDistinctsForField(field)) {
        this.$store.dispatch('designs/getDistinct', field);
      }
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
      this.toggleLoadReportOpen();
    },

    saveReport() {
      this.$store.dispatch('designs/saveReport', this.saveReportSettings);
      this.toggleSaveReportOpen();
    },

    setCurrentTab(tab) {
      this.$store.dispatch('designs/switchCurrentTab', tab);
    },

    toggleFilterOpen() {
      this.$store.dispatch('designs/toggleFilterOpen');
    },

    toggleLoadReportOpen() {
      this.$store.dispatch('designs/toggleLoadReportOpen');
    },

    toggleSaveReportOpen() {
      this.$store.dispatch('designs/toggleSaveReportOpen');
    },

    toggleDataOpen() {
      this.$store.dispatch('designs/toggleDataOpen');
    },

    toggleChartsOpen() {
      this.$store.dispatch('designs/toggleChartsOpen');
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
code {
  white-space: pre;
  word-wrap: break-word;
}
.panel-block {
  position: relative;
  &.indented {
    padding-left: 1.75rem;
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
  padding: 1.5rem;
}

.section-header {
  padding: 0.25rem;
  margin-bottom: 0.25rem;
  cursor: pointer;

  &.is-expandable::after {
    right: 30px;
    text-align: center;
    margin-top: -7px;
  }
}
.filter-item {
  padding: 1.5rem;
}

.inner-scroll {
  position: relative;
  height: calc(100vh - 252px);
  border-left: 1px solid #dbdbdb;
  border-right: 1px solid #dbdbdb;
  overflow: scroll;
}

.selected-filters {
  padding: 1.5rem;
  padding-left: 0;
}
.chart-buttons {
  margin-top: -34px;
  margin-left: 70px;
  width: 20%;

  .button {
    background: transparent;
  }
}
</style>
