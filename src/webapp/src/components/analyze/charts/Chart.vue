<script>
import {
  AreaChart,
  BarChart,
  LineChart,
  ScatterChart,
  VerticalBarChart
} from '@/components/analyze/charts'

export default {
  name: 'Chart',
  components: {
    AreaChart,
    BarChart,
    LineChart,
    ScatterChart,
    VerticalBarChart
  },
  props: {
    chartType: {
      type: String,
      required: true
    },
    resultAggregates: {
      type: Array,
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
