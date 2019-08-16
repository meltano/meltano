<script>
import { BarChart, LineChart, AreaChart, ScatterChart } from './charts'

export default {
  name: 'Bar',
  components: {
    BarChart,
    LineChart,
    AreaChart,
    ScatterChart
  },
  props: ['chartType', 'results', 'resultAggregates']
}
</script>

<template>
  <div v-show="results.length">
    <component
      :is="chartType"
      :chart-type="chartType"
      :results="results"
      :result-aggregates="resultAggregates"
    ></component>
  </div>
</template>

<style lang="scss"></style>
