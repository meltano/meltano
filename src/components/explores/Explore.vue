<template>
<div class="container">
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
        <template v-for="(view, index) in explore.views">
        <a class="panel-block
                panel-block-heading
                has-background-white-ter
                has-text-grey
                is-expandable"
                :class="{'is-collapsed': view.collapsed}"
                :key="view.unique_name"
                @click="viewRowClicked(index)">
          {{view | printable | underscoreToSpace | titleCase}}
        </a>
        <!-- eslint-disable-next-line vue/require-v-for-key -->
        <a class="panel-block
                panel-block-heading
                has-background-white"
                v-if="!view.collapsed">
          Dimensions
        </a>
        <a class="panel-block"
            v-for="dimension in view.dimensions"
            :key="dimension.unique_name"
            v-if="!view.collapsed">
          {{dimension | printable | underscoreToSpace | titleCase}}
        </a>
        <!-- eslint-disable-next-line vue/require-v-for-key -->
        <a class="panel-block
                panel-block-heading
                has-background-white"
                v-if="!view.collapsed">
          Measures
        </a>
        <a class="panel-block"
                v-for="measure in view.measures"
                :key="measure.unique_name"
                v-if="!view.collapsed">
          {{measure | printable | underscoreToSpace | titleCase}}
        </a>
        </template>
      </div>
      <div class="panel-block">
        <button class="button is-link is-outlined is-fullwidth">
          reset all filters
        </button>
      </div>
    </nav>
  </div>
</div>
</template>
<script>
import { mapState } from 'vuex';

export default {
  name: 'Explore',
  created() {
    this.$store.dispatch('explores/getExplore', {
      model: this.$route.params.model,
      explore: this.$route.params.explore,
    });
  },
  filters: {
    printable(value) {
      return value.settings.view_label ? value.settings.view_label : value.name;
    },
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
    ]),
  },
  methods: {
    viewRowClicked(viewIndex) {
      this.$store.dispatch('explores/expandRow', viewIndex);
    },
  },
};
</script>
<style lang="scss" scoped>
.panel {
  margin-top: 10px;
}

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
