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
        <template v-for="view in explore.views">
        <a class="panel-block panel-block-heading has-background-white-ter has-text-grey-light" :key="view.unique_name">
          {{view.settings.label}}
        </a>
        <!-- eslint-disable-next-line vue/require-v-for-key -->
        <a class="panel-block panel-block-heading has-background-white-ter has-text-grey-light">
          Dimensions
        </a>
        <a class="panel-block" v-for="dimension in view.dimensions" :key="dimension.unique_name">
          {{dimension | printable | underscoreToSpace | capitalize}}
        </a>
        <!-- eslint-disable-next-line vue/require-v-for-key -->
        <a class="panel-block panel-block-heading has-background-white-ter has-text-grey-light">
          Measures
        </a>
        <a class="panel-block" v-for="measure in view.measures" :key="measure.unique_name">
          {{measure | printable | underscoreToSpace | capitalize}}
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
      return value.settings.label ? value.settings.label : value.name;
    },
  },
  computed: {
    ...mapState('explores', [
      'explore',
    ]),
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
}

.inner-scroll {
  position: relative;
  height: calc(100vh - 252px);
  overflow: scroll;
}
</style>
