<template>
  <div v-show="results.length">
    <component :is="chartType"
                :chart-type='chartType'
                :results='results'
                :result-aggregates='resultAggregates'></component>
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
  props: [
    'chartType',
    'results',
    'resultAggregates',
  ],
};
</script>
