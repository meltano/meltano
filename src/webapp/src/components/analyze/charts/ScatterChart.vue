<script>
import chartMixin from './chartMixin'
import { CHART_MODELS } from '@/components/analyze/charts/ChartModels'

export default {
  name: 'ScatterChart',
  mixins: [chartMixin],
  mounted() {
    this.config.type = CHART_MODELS.SCATTER.configType
    this.createChart()
  }
}
</script>

<template>
  <canvas v-show="results.length" ref="chart" height="200"></canvas>
</template>

<style lang="scss"></style>
