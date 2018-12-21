<template>
<div class="container">
  <section class="section">
    <div class="columns">
      <nav class="panel column is-one-quarter">
        <p class="panel-heading">
          {{explore.label}}
        </p>
        <div class="panel-block">
          <p class="control">
            <input class="input is-small" type="text" placeholder="search">
          </p>
        </div>

        <pre>TODO joins partial</pre>

        <div class="panel-block">
          <button class="button is-link is-outlined is-fullwidth">
            reset all filters
          </button>
        </div>
      </nav>
      <div class="column is-three-quarters">
        <div class="columns">
          <div class="column">
            <a class="button is-primary is-pulled-right"
              :class="{'is-loading': loadingQuery}"
              @click="runQuery">Run</a>
          </div>
        </div>
        <!-- <template v-if="explore.settings.has_filters">
          <div class="has-background-grey-darker
          section-header
          has-text-white-bis
          is-expandable"
          @click="toggleFilterOpen"
          :class="{'is-collapsed': !filtersOpen}">Filters</div>
          <div class="has-background-white-ter filter-item"
                v-for="filter in explore.settings.always_filter.filters"
                :key="filter.field"
                v-if="filtersOpen">
            <div class="columns">
              <div class="column is-3">
                <strong>{{filter.explore_label}}</strong>
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
                  <template v-for="selected in getSelectionsFromDistinct(filter.sql)">
                    <span class="tag is-link" :key="selected">
                      {{selected}}
                      <button class="delete is-small"></button>
                    </span>
                  </template>
                </div>
              </div>
            </div>
          </div>
        </template> -->

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
            <li v-for="error in sqlErrorMessage" :key="error">{{error}}</li>
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
  name: 'Explore',
  created() {
    this.$store.dispatch('explores/getExplore', {
      model: this.$route.params.model,
      explore: this.$route.params.explore,
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
    this.$store.dispatch('explores/getExplore', {
      model: to.params.model,
      explore: to.params.explore,
    });
    next();
  },
  computed: {
    ...mapState('explores', [
      'explore',
      'selectedDimensions',
      'currentModel',
      'currentExplore',
      'currentSQL',
      'loadingQuery',
      'filtersOpen',
      'dataOpen',
      'chartsOpen',
      'hasSQLError',
      'sqlErrorMessage',
    ]),
    ...mapGetters('explores', [
      'currentModelLabel',
      'currentExploreLabel',
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
      'getLabelForJoin',
      'showJoinDimensionMeasureHeader',
      'formattedSql',
    ]),

    limit: {
      get() {
        return this.$store.getters['explores/currentLimit'];
      },
      set(value) {
        this.$store.dispatch('explores/limitSet', value);
        this.$store.dispatch('explores/getSQL', { run: false });
      },
    },
  },
  methods: {
    inputFocused(field) {
      if (!this.getDistinctsForField(field)) {
        this.$store.dispatch('explores/getDistinct', field);
      }
    },

    setChartType(chartType) {
      this.$store.dispatch('explores/setChartType', chartType);
    },

    viewRowClicked() {
      this.$store.dispatch('explores/expandRow');
    },

    joinRowClicked(join) {
      this.$store.dispatch('explores/expandJoinRow', join);
    },

    dimensionSelected(dimension) {
      this.$store.dispatch('explores/removeSort', dimension);
      this.$store.dispatch('explores/toggleDimension', dimension);
      this.$store.dispatch('explores/getSQL', { run: false });
    },

    dimensionGroupSelected(dimensionGroup) {
      this.$store.dispatch('explores/toggleDimensionGroup', dimensionGroup);
    },

    dimensionGroupTimeframeSelected(dimensionGroup, timeframe) {
      this.$store.dispatch('explores/toggleDimensionGroupTimeframe', {
        dimensionGroup,
        timeframe,
      });
      this.$store.dispatch('explores/getSQL', { run: false });
    },

    measureSelected(measure) {
      this.$store.dispatch('explores/toggleMeasure', measure);
      this.$store.dispatch('explores/getSQL', { run: false });
    },

    joinDimensionSelected(join, dimension) {
      this.$store.dispatch('explores/toggleDimension', dimension);
      this.$store.dispatch('explores/getSQL', { run: false });
    },

    joinMeasureSelected(join, measure) {
      this.$store.dispatch('explores/toggleMeasure', measure);
      this.$store.dispatch('explores/getSQL', { run: false });
    },

    runQuery() {
      this.$store.dispatch('explores/getSQL', { run: true });
    },

    setCurrentTab(tab) {
      this.$store.dispatch('explores/switchCurrentTab', tab);
    },

    toggleFilterOpen() {
      this.$store.dispatch('explores/toggleFilterOpen');
    },

    toggleDataOpen() {
      this.$store.dispatch('explores/toggleDataOpen');
    },

    toggleChartsOpen() {
      this.$store.dispatch('explores/toggleChartsOpen');
    },

    dropdownSelected(item, field) {
      this.$store.dispatch('explores/addDistinctSelection', {
        item,
        field,
      });
      this.$store.dispatch('explores/getSQL', { run: false });
    },

    modifierChanged(item, field) {
      this.$store.dispatch('explores/addDistinctModifier', {
        item,
        field,
      });
      this.$store.dispatch('explores/getSQL', { run: false });
    },
    ...mapActions('explores', [
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

  &.dimension-group {
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
