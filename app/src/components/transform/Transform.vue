<template>
<div class="container">
  <section class="section">
    <div class="columns is-mobile is-centered">
      <div class="column is-half box">
        <a class="button is-primary is-pulled-right">Run</a>
        <h3 class="is-size-3">Transformers</h3>
        <p>Choose a transformer</p>
        <div class="select">
          <select>
            <option selected="true" disabled="disabled">Choose an transformer</option>
            <option v-for="extractor in extractors" :key="extractor">{{extractor}}</option>
            <option>Optimus Prime</option>
          </select>
        </div>
      </div>
    </div>
  </section>
</div>
</template>
<script>
import { mapState } from 'vuex';

export default {
  name: 'Extract',
  created() {
    this.$store.dispatch('orchestrations/getAll');
  },
  computed: {
    ...mapState('orchestrations', [
      'extractors',
    ]),
  },
  beforeRouteUpdate(to, from, next) {
    this.$store.dispatch('orchestrations/getAll');
    next();
  },
};
</script>
