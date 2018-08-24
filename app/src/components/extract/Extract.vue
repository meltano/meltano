<template>
<div class="container">
  <section class="section">
    <div class="columns is-mobile is-centered">
      <div class="column is-half box">
        <a class="button is-primary is-pulled-right" @click="runExtractor">Run</a>
        <h3 class="is-size-3">Extractors</h3>
        <p>Choose an extractor</p>
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
      'log',
      'extractors',
    ]),
  },
  methods: {
    ...mapActions('orchestrations', [
      'currentExtractorClicked',
      'runExtractor',
    ]),
  },
  beforeRouteUpdate(to, from, next) {
    this.$store.dispatch('orchestrations/getAll');
    next();
  },
};
</script>
