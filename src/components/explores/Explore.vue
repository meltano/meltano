<template>
<div class="container">
  <section class="section">
    <div class="columns">
      <nav class="panel column is-one-quarter">
        <p class="panel-heading">
          {{explore.settings.label}}
        </p>
        <div class="panel-block">
          <p class="control">
            <input class="input is-small" type="text" placeholder="search">
          </p>
        </div>
        <div class="inner-scroll">
          <a class="panel-block
                  panel-block-heading
                  has-background-white-ter
                  has-text-grey
                  is-expandable"
                  :class="{'is-collapsed': explore.view.collapsed}"
                  :key="explore.view.unique_name"
                  @click="viewRowClicked()">
            {{currentExploreLabel}}
          </a>
          <!-- eslint-disable-next-line vue/require-v-for-key -->
          <a class="panel-block
                  panel-block-heading
                  has-background-white"
                  v-if="!explore.view.collapsed">
            Dimensions
          </a>
          <a class="panel-block"
              v-for="dimension in explore.view.dimensions"
              :key="dimension.unique_name"
              v-if="!explore.view.collapsed && !dimension.settings.hidden"
              @click="dimensionSelected(dimension)"
              :class="{'is-active': dimension.selected}">
            {{dimension.label}}
          </a>
          <!-- eslint-disable-next-line vue/require-v-for-key -->
          <a class="panel-block
                  panel-block-heading
                  has-background-white"
                  v-if="!explore.view.collapsed">
            Measures
          </a>
          <a class="panel-block"
                  v-for="measure in explore.view.measures"
                  :key="measure.unique_name"
                  v-if="!explore.view.collapsed"
                  @click="measureSelected(measure)"
                  :class="{'is-active': measure.selected}">
            {{measure.label}}
          </a>
        </div>
        <div class="panel-block">
          <button class="button is-link is-outlined is-fullwidth">
            reset all filters
          </button>
        </div>
      </nav>
      <div class="column">
        <div class="level">
          <div class="level-item level-right">
            <a class="button is-primary"
              :class="{'is-loading': loadingQuery}"
              @click="runQuery">Run</a>
          </div>
        </div>
        <template v-if="explore.settings.has_filters">
        <div class="level
        has-background-grey-darker
        section-header
        has-text-white-bis
        is-expandable"
        @click="toggleFilterOpen"
        :class="{'is-collapsed': !filtersOpen}">Filters</div>
        <div class="level has-background-white-ter filter-item"
              v-for="filter in explore.settings.always_filter.filters"
              :key="filter.field"
              v-if="filtersOpen">
          <div class="columns level-left level-item">
            <span class="column is-1 tag is-info">Required</span>
            <div class="column is-2">
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
        </template>
        <div class="level
        has-background-grey-darker
        section-header
        has-text-white-bis
        is-expandable"
        @click="toggleDataOpen"
        :class="{'is-collapsed': !dataOpen}">Data</div>
        <template v-if="dataOpen">
        <div class="level has-background-white-ter data-toggles">
          <div class="level-left">
            <div class="buttons has-addons level-item">
              <span class="button"
                    :class="{'is-active': isResultsTab}"
                    @click="setCurrentTab('results')">Results</span>
              <span class="button"
                    :class="{'is-active': isSQLTab}"
                    @click="setCurrentTab('sql')">SQL</span>
            </div>
          </div>
          <div class="level-right">
            <div class="level-item">
              <div class="field">
                <div class="control">
                  <input class="input is-small" type="text" v-model="limit" placeholder="Limit">
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="level">
          <div class="level-item" v-if="isResultsTab">
            <div class="notification is-info" v-if="!hasResults">
              No results
            </div>
            <table class="table
                is-bordered
                is-striped
                is-narrow
                is-hoverable
                is-fullwidth"
                v-if="hasResults">
              <thead>
                <th v-for="key in keys" :key="key">
                  {{key}}
                </th>
              </thead>
              <tbody>
                <!-- eslint-disable-next-line vue/require-v-for-key -->
                <tr v-for="result in results">
                  <td v-for="key in keys" :key="key">
                    {{result[key]}}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="level">
          <div class="level-item" v-if="isSQLTab">
            <code>{{currentSQL}}</code>
          </div>
        </div>
        </template>
      </div>
    </div>
  </section>
</div>
</template>
<script>
import { mapState, mapGetters } from 'vuex';
import SelectDropdown from '../SelectDropdown';
import YesNoFilter from '../filters/YesNoFilter';

export default {
  name: 'Explore',
  created() {
    this.$store.dispatch('explores/getExplore', {
      model: this.$route.params.model,
      explore: this.$route.params.explore,
    });
  },
  components: {
    SelectDropdown,
    YesNoFilter,
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
      'keys',
      'results',
      'loadingQuery',
      'filtersOpen',
      'dataOpen',
    ]),
    ...mapGetters('explores', [
      'hasResults',
      'currentModelLabel',
      'currentExploreLabel',
      'isDataTab',
      'isResultsTab',
      'isSQLTab',
      'getDistinctsForField',
      'getResultsFromDistinct',
      'getKeyFromDistinct',
      'getSelectionsFromDistinct',
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

    viewRowClicked() {
      this.$store.dispatch('explores/expandRow');
    },

    dimensionSelected(dimension) {
      this.$store.dispatch('explores/toggleDimension', dimension);
      this.$store.dispatch('explores/getSQL', { run: false });
    },

    measureSelected(measure) {
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
  },
};
</script>
<style lang="scss" scoped>
.panel-block {
  &.panel-block-heading {
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
    font-weight: bold;
    &:hover {
      background: white;
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
</style>
