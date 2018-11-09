<template>
  <canvas ref="chart" height="200" v-show="results.length"></canvas>
</template>
<script>
import chartMixin from './chartMixin';

export default {
  name: 'LineChart',
  mixins: [chartMixin],
  mounted() {
    this.config.type = 'line';
    this.createChart();
  },
};
</script>
