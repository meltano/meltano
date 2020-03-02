<script>
import chartMixin from './chartMixin'
import { CHART_MODELS } from '@/components/analyze/charts/ChartModels'

export default {
  name: 'BarChart',
  mixins: [chartMixin],
  mounted() {
    this.config.type = CHART_MODELS.HORIZONTAL_BAR.configType
    this.createChart()
  }
}
</script>

<template>
  <canvas v-show="results.length" ref="chart" height="200"></canvas>
</template>

<style lang="scss"></style>
