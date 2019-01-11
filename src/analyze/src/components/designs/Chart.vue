<template>
  <div v-show="results.length">
    <component :is="chartType"></component>
  </div>
</template>
<script>
import { mapState } from 'vuex';
import { BarChart, LineChart, AreaChart, ScatterChart } from './charts';

export default {
  name: 'Bar',
  components: {
    BarChart,
    LineChart,
    AreaChart,
    ScatterChart,
  },
  computed: {
    ...mapState('designs', [
      'results',
      'chartType',
    ]),
  },
};
</script>
