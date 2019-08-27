<script>
import { AreaChart, BarChart, LineChart, ScatterChart } from './charts'

export default {
  name: 'Bar',
  components: {
    BarChart,
    LineChart,
    AreaChart,
    ScatterChart
  },
  props: {
    chartType: {
      type: String,
      required: true
    },
    resultAggregates: {
      type: Object,
      required: true
    },
    results: {
      type: Array,
      required: true
    }
  }
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
