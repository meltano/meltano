<template>
<div class="container">
  <section class="section">
    <div class="columns is-mobile is-centered">
      <div class="column is-half box">
        <a class="button is-primary is-pulled-right" @click="runTransform">Run</a>
        <h3 class="is-size-3">Transformers</h3>
        <p>Choose a transformer</p>
        <div class="select" @click="currentExtractorClicked">
          <select>
            <option selected="true" disabled="disabled">Choose an transformer</option>
            <option v-for="extractor in extractors" :key="extractor">{{extractor}}</option>
            <option value="date">date</option>
          </select>
        </div>
        <div class="select">
          <select @click="currentConnectionNameClicked">
            <option selected="true" disabled="disabled">Choose a connection</option>
            <option v-for="connection in connectionNames"
              :key="connection">{{connection}}</option>
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
    this.$store.dispatch('orchestrations/getConnectionNames');
  },
  computed: {
    ...mapState('orchestrations', [
      'extractors',
      'connectionNames',
      'log',
    ]),
  },
  methods: {
    ...mapActions('orchestrations', [
      'currentExtractorClicked',
      'currentConnectionNameClicked',
      'runTransform',
    ]),
  },
  beforeRouteUpdate(to, from, next) {
    this.$store.dispatch('orchestrations/getAll');
    next();
  },
};
</script>
