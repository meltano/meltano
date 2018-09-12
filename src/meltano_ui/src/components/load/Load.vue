<template>
<div class="container">
  <section class="section">
    <div class="columns is-mobile is-centered">
      <div class="column is-half box">
        <a class="button is-primary is-pulled-right" @click="runLoader">Run</a>
        <h3 class="is-size-3">Loaders</h3>
        <p>Choose a loader</p>
        <div class="select">
          <select @change="currentLoaderClicked">
            <option selected="true" disabled="disabled">Choose a loader</option>
            <option v-for="loader in loaders" :key="loader">{{loader}}</option>
          </select>
        </div>
        <div class="select">
          <select @change="currentExtractorClicked">
            <option selected="true" disabled="disabled">Choose an extractor</option>
            <option v-for="extractor in extractors" :key="extractor">{{extractor}}</option>
          </select>
        </div>
        <div class="log-output">{{log}}</div>
      </div>
    </div>
  </section>
</div>
</template>
<script>
import { mapState, mapActions } from 'vuex';

export default {
  name: 'Extract',
  created() {
    this.$store.dispatch('orchestrations/getAll');
  },
  computed: {
    ...mapState('orchestrations', [
      'loaders',
      'extractors',
      'log',
    ]),
  },
  methods: {
    ...mapActions('orchestrations', [
      'currentLoaderClicked',
      'currentExtractorClicked',
      'runLoader',
    ]),
  },
  beforeRouteUpdate(to, from, next) {
    this.$store.dispatch('orchestrations/getAll');
    next();
  },
};
</script>
