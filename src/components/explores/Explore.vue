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
                  v-if="!explore.view.collapsed">
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
            <a class="button is-primary" @click="runQuery">Run</a>
          </div>
        </div>
      </div>
    </div>
  </section>
</div>
</template>
<script>
import { mapState, mapGetters } from 'vuex';

export default {
  name: 'Explore',
  created() {
    this.$store.dispatch('explores/getExplore', {
      model: this.$route.params.model,
      explore: this.$route.params.explore,
    });
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
    ]),
    ...mapGetters('explores', [
      'currentModelLabel',
      'currentExploreLabel',
    ]),
  },
  methods: {
    viewRowClicked() {
      this.$store.dispatch('explores/expandRow');
    },

    dimensionSelected(dimension) {
      this.$store.dispatch('explores/toggleDimension', dimension);
    },

    runQuery() {
      this.$store.dispatch('explores/runQuery');
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

  &.is-expandable::after {
    content: "-";
    width: 20px;
    height: 20px;
    position: absolute;
    right: 0;
  }

  &.is-collapsed::after {
    content: "+";
    width: 20px;
    height: 20px;
    position: absolute;
    right: 0;
  }
}

.inner-scroll {
  position: relative;
  height: calc(100vh - 252px);
  border-left: 1px solid #dbdbdb;
  border-right: 1px solid #dbdbdb;
  overflow: scroll;
}
</style>
